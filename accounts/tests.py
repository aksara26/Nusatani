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
        call_command("seed_demo_users", verbosity=0)

        for username, role, _is_admin in DEMO_ACCOUNTS:
            with self.subTest(username=username):
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

    def test_seed_command_repairs_existing_account_with_bad_password(self):
        broken, _ = User.objects.update_or_create(
            username="petani1", defaults={"role": "farmer"}
        )
        broken.password = "plaintext-tanpa-hash"
        broken.save(update_fields=["password"])
        self.assertFalse(broken.check_password("password123"))

        call_command("seed_demo_users", verbosity=0)
        broken.refresh_from_db()
        self.assertTrue(broken.check_password("password123"))

        self.client.logout()
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "petani1", "password": "password123"},
        )
        self.assertRedirects(response, reverse("accounts:dashboard"))

    def test_guide_links_to_real_registration_not_demo_credentials(self):
        guide = self.client.get(reverse("accounts:guide"))
        self.assertEqual(guide.status_code, 200)
        self.assertContains(guide, 'data-role="farmer"')
        self.assertContains(guide, 'data-register-url="/accounts/daftar/?role=farmer"')
        self.assertContains(guide, "Lanjut ke pendaftaran")
        self.assertNotContains(guide, "password123")
        self.assertNotContains(guide, "Akun demo")

    def test_registration_creates_account_then_login_works(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "petanibaru",
                "email": "petanibaru@example.com",
                "first_name": "Sari",
                "last_name": "Utami",
                "role": "farmer",
                "password1": "password123",
                "password2": "password123",
            },
        )
        self.assertRedirects(response, reverse("accounts:login"))

        user = User.objects.get(username="petanibaru")
        self.assertEqual(user.role, "farmer")
        self.assertTrue(user.check_password("password123"))

        login = self.client.post(
            reverse("accounts:login"),
            {"username": "petanibaru", "password": "password123"},
        )
        self.assertRedirects(login, reverse("accounts:dashboard"))

    def test_registration_rejects_internal_roles_and_weak_password(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "qcbaru",
                "email": "qcbaru@example.com",
                "role": "qc",
                "password1": "pendek",
                "password2": "pendek",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="qcbaru").exists())
        self.assertContains(response, "Password minimal 8 karakter")

    def test_registration_form_prefills_role_from_guide(self):
        response = self.client.get(reverse("accounts:register"), {"role": "horeca"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="horeca" selected')

    def test_wrong_password_is_rejected(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "petani1", "password": "salah"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "sandi yang benar")

    def test_login_tolerates_spaces_and_capitalization(self):
        for typed_username in ("petani 1", " Petani1 ", "PETANI1"):
            with self.subTest(typed_username=typed_username):
                self.client.logout()
                response = self.client.post(
                    reverse("accounts:login"),
                    {"username": typed_username, "password": "password123"},
                )
                self.assertRedirects(response, reverse("accounts:dashboard"))


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


class GuideAndProfileTests(TestCase):
    def test_new_visitor_is_guided_before_login(self):
        response = self.client.get(reverse("home"))
        self.assertRedirects(response, reverse("accounts:guide"))

        guide = self.client.get(reverse("accounts:guide"))
        self.assertEqual(guide.status_code, 200)
        self.assertContains(guide, "Sebelum masuk, pilih peran Anda")
        self.assertContains(guide, "Cara daftar")
        self.assertContains(guide, "Lewati panduan")
        self.assertNotContains(guide, "password123")

    def test_skip_guide_remembers_choice(self):
        response = self.client.get(reverse("accounts:guide"), {"skip": "1"})
        self.assertRedirects(response, reverse("accounts:login"))
        self.assertTrue(self.client.session.get("nt_guide_seen"))

        response = self.client.get(reverse("home"))
        self.assertRedirects(response, reverse("accounts:login"))

    def test_guide_is_a_three_step_wizard_separate_from_login(self):
        guide = self.client.get(reverse("accounts:guide"))
        self.assertContains(guide, 'data-step="1"')
        self.assertContains(guide, 'data-step="2"')
        self.assertContains(guide, 'data-step="3"')
        self.assertContains(guide, 'data-role-select')
        self.assertContains(guide, 'data-role-steps="farmer"')
        self.assertNotContains(guide, 'name="password"')

        login = self.client.get(reverse("accounts:login"))
        self.assertContains(login, 'name="password"')
        self.assertNotContains(login, "Sebelum masuk, pilih peran Anda")
        self.assertContains(login, "Buka panduan")
        self.assertContains(login, "Daftar sekarang")
        self.assertNotContains(login, "password123")

    def test_login_is_always_discoverable_on_public_pages(self):
        for url in (
            reverse("accounts:guide"),
            reverse("accounts:login"),
            reverse("accounts:register"),
        ):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, 'class="public-hero"')
                self.assertContains(response, "d-lg-none")
                self.assertContains(response, 'href="/accounts/login/"')
                self.assertContains(response, "Foto sawah:")

        guide = self.client.get(reverse("accounts:guide"))
        self.assertContains(guide, "Lewati panduan, langsung masuk")

    def test_login_prefills_username_from_guide(self):
        response = self.client.get(reverse("accounts:login"), {"username": "petani1"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="petani1"')

    def test_authenticated_user_can_update_profile(self):
        user = User.objects.create_user(
            username="petaniuji", password="password123", role="farmer"
        )
        self.client.login(username="petaniuji", password="password123")
        response = self.client.post(
            reverse("accounts:profile"),
            {
                "first_name": "Sari",
                "last_name": "Utami",
                "email": "sari@example.com",
            },
        )
        self.assertRedirects(response, reverse("accounts:profile"))
        user.refresh_from_db()
        self.assertEqual(user.first_name, "Sari")
        self.assertEqual(user.email, "sari@example.com")
