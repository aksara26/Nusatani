"""Verifikasi alur login dan dashboard untuk seluruh akun demo NusaTani."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from assets.models import Asset
from bankku.models import FarmerPerformance, FinancingAssessment
from mentorship.models import Mentorship, MentorshipActivity
from orders.models import Order, OrderItem, PaymentRecord
from products.models import Product, Variety

from .roles import ROLE_DASHBOARDS

User = get_user_model()

DEMO_ACCOUNTS = [
    ("admin", "admin", True),
    ("petani1", "farmer", False),
    ("horeca1", "horeca", False),
    ("konsumen1", "consumer", False),
    ("qc1", "qc", False),
    ("mentor1", "mentor", False),
    ("bank1", "bank", False),
]


class DemoLoginTests(TestCase):
    def test_all_demo_accounts_can_login_and_open_own_dashboard(self):
        for username, role, is_admin in DEMO_ACCOUNTS:
            with self.subTest(username=username):
                user, _ = User.objects.update_or_create(
                    username=username,
                    defaults={
                        "email": f"{username}@example.com",
                        "role": role,
                        "is_staff": is_admin,
                        "is_superuser": is_admin,
                        "is_active": True,
                    },
                )
                user.set_password("password123")
                user.save()

                self.client.logout()
                response = self.client.post(
                    reverse("accounts:login"),
                    {"username": username, "password": "password123"},
                )
                self.assertEqual(response.status_code, 302, msg=f"login gagal untuk {username}")
                self.assertEqual(response.url, reverse("accounts:dashboard"))

                dashboard = self.client.get(reverse("accounts:dashboard"))
                self.assertEqual(dashboard.status_code, 200)
                self.assertContains(dashboard, ROLE_DASHBOARDS[role]["label"])

    def test_wrong_password_is_rejected(self):
        User.objects.create_user(username="petani1", password="password123", role="farmer")
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "petani1", "password": "salah"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "sandi yang benar")


class PurgeDemoDataTests(TestCase):
    def setUp(self):
        self.farmer = User.objects.create_user(
            username="petaniuji", password="password123", role="farmer"
        )
        self.mentor = User.objects.create_user(
            username="mentoruji", password="password123", role="mentor"
        )
        variety, _ = Variety.objects.get_or_create(
            slug="sawi-putih", defaults={"name": "Sawi Putih"}
        )
        self.product = Product.objects.create(
            farmer=self.farmer, variety=variety, name="Sawi Demo", price=Decimal("25000")
        )
        self.order = Order.objects.create(buyer=self.farmer, farmer=self.farmer)
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            unit_price=self.product.price,
        )
        PaymentRecord.objects.create(order=self.order)
        self.asset = Asset.objects.create(name="Rak demo", owner=self.farmer)
        self.mentorship = Mentorship.objects.create(
            farmer=self.farmer,
            mentor=self.mentor,
            topic="Materi demo",
            scheduled_at=timezone.now(),
        )
        MentorshipActivity.objects.create(
            mentorship=self.mentorship, description="Kegiatan demo", author=self.mentor
        )
        self.performance, _ = FarmerPerformance.objects.get_or_create(farmer=self.farmer)
        FinancingAssessment.objects.get_or_create(performance=self.performance)

    def test_purge_requires_confirmation(self):
        with self.assertRaises(CommandError):
            call_command("purge_demo_data")
        self.assertTrue(Order.objects.exists())
        self.assertTrue(Asset.objects.exists())

    def test_purge_removes_demo_data_but_keeps_users_and_varieties(self):
        call_command("purge_demo_data", "--yes")
        self.assertFalse(Order.objects.exists())
        self.assertFalse(Asset.objects.exists())
        self.assertFalse(Mentorship.objects.exists())
        self.assertFalse(MentorshipActivity.objects.exists())
        self.assertFalse(FarmerPerformance.objects.exists())
        self.assertFalse(FinancingAssessment.objects.exists())
        self.assertFalse(Product.objects.exists())
        self.assertTrue(User.objects.filter(username="petaniuji").exists())
        self.assertTrue(Variety.objects.exists())
