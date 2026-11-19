"""Pengujian BANKKU, indikator simulasi, dan skenario akhir 11–12."""

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.roles import Role
from assets.models import Asset
from mentorship.models import Mentorship, MentorshipStatus
from orders.models import (
    Order,
    OrderItem,
    OrderStatus,
    PaymentRecord,
    PaymentStatus,
    QcResult,
)
from products.models import Inventory, Product, Variety
from quality_control.models import QcStatus, QualityInspection

from .models import EligibilityBand, FarmerPerformance, FinancingAssessment

User = get_user_model()


class BankkuTests(TestCase):
    def setUp(self):
        self.farmer = User.objects.create_user(
            username="petaniuji", password="password123", role=Role.FARMER.value
        )
        self.buyer = User.objects.create_user(
            username="horecauji", password="password123", role=Role.HORECA.value
        )
        self.bank = User.objects.create_user(
            username="bankuji", password="password123", role=Role.BANK.value
        )
        self.mentor = User.objects.create_user(
            username="mentoruji", password="password123", role=Role.MENTOR.value
        )
        self.admin = User.objects.create_superuser(
            username="adminuji", password="password123", role=Role.ADMIN.value
        )
        variety, _ = Variety.objects.get_or_create(
            slug="sawi-putih", defaults={"name": "Sawi Putih"}
        )
        self.product = Product.objects.create(
            farmer=self.farmer, variety=variety, name="Sawi Segar", price=Decimal("25000")
        )
        Inventory.objects.create(product=self.product, quantity=50)

    def make_order(self, status=OrderStatus.SELESAI.value, payment=PaymentStatus.LUNAS.value, qc=QcResult.LOLOS.value):
        order = Order.objects.create(
            buyer=self.buyer,
            farmer=self.farmer,
            order_type="preorder",
            status=status,
            needed_by=timezone.localdate() + timedelta(days=10),
        )
        item = OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=1,
            unit_price=self.product.price,
            qc_result=qc,
        )
        PaymentRecord.objects.create(order=order, status=payment)
        QualityInspection.objects.create(
            order_item=item,
            result=QcStatus.LOLOS.value if qc == QcResult.LOLOS.value else QcStatus.DITOLAK.value,
        )
        return order

    def make_performance(self):
        performance, _ = FarmerPerformance.objects.get_or_create(farmer=self.farmer)
        return performance.recalculate()

    def test_performance_recalculates_from_orders_qc_and_assets(self):
        self.make_order(status=OrderStatus.SELESAI.value)
        self.make_order(
            status=OrderStatus.MENUNGGU_QC.value,
            payment=PaymentStatus.BELUM_DIBAYAR.value,
            qc=QcResult.DITOLAK.value,
        )
        for index in range(3):
            Asset.objects.create(name=f"Rak {index}", owner=self.farmer)

        performance = self.make_performance()
        self.assertEqual(performance.total_orders, 2)
        self.assertEqual(performance.completed_orders, 1)
        self.assertEqual(performance.total_order_value, Decimal("50000"))
        self.assertEqual(performance.fulfillment_rate, Decimal("50.00"))
        self.assertEqual(performance.quality_pass_rate, Decimal("50.00"))
        self.assertEqual(performance.asset_count, 3)
        self.assertIsNotNone(performance.last_calculated_at)

    def test_assessment_scores_all_factors(self):
        self.make_order()
        for index in range(5):
            Asset.objects.create(name=f"Tray {index}", owner=self.farmer)
        for index in range(3):
            Mentorship.objects.create(
                farmer=self.farmer,
                mentor=self.mentor,
                topic=f"Materi {index}",
                scheduled_at=timezone.now(),
                status=MentorshipStatus.SELESAI.value,
            )

        performance = self.make_performance()
        assessment, _ = FinancingAssessment.objects.get_or_create(performance=performance)
        assessment.recalculate()

        self.assertEqual(assessment.fulfillment_score, Decimal("30.00"))
        self.assertEqual(assessment.quality_score, Decimal("25.00"))
        self.assertEqual(assessment.asset_score, Decimal("20.00"))
        self.assertEqual(assessment.mentorship_score, Decimal("15.00"))
        self.assertEqual(assessment.payment_score, Decimal("10.00"))
        self.assertEqual(assessment.total_score, Decimal("100.00"))
        self.assertEqual(assessment.eligibility, EligibilityBand.POTENSIAL.value)

    def test_low_data_falls_into_lowest_band(self):
        performance = self.make_performance()
        assessment, _ = FinancingAssessment.objects.get_or_create(performance=performance)
        assessment.recalculate()
        self.assertEqual(assessment.total_score, Decimal("0.00"))
        self.assertEqual(assessment.eligibility, EligibilityBand.BELUM.value)

    def test_bank_dashboard_is_limited_to_bank_and_admin(self):
        self.make_order()
        self.client.login(username="bankuji", password="password123")
        response = self.client.get(
            reverse("bankku:dashboard"), {"petani": self.farmer.pk}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "petaniuji")
        self.assertContains(response, "Indikator — petaniuji")

        self.client.logout()
        self.client.login(username="petaniuji", password="password123")
        response = self.client.get(reverse("bankku:dashboard"))
        self.assertEqual(response.status_code, 403)

        self.client.logout()
        self.client.login(username="adminuji", password="password123")
        response = self.client.get(reverse("bankku:dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_farmer_can_open_own_performance(self):
        self.make_order()
        self.client.login(username="petaniuji", password="password123")
        response = self.client.get(reverse("bankku:my_performance"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Performaku")
        self.assertContains(response, "Indikator simulasi")

    def test_scenario_11_completed_order_appears_in_history(self):
        order = self.make_order()
        self.client.login(username="horecauji", password="password123")
        response = self.client.get(reverse("orders:my_orders"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, order.order_number)
        self.assertContains(response, "Selesai")

    def test_scenario_12_admin_dashboard_shows_platform_data(self):
        self.make_order()
        self.client.login(username="adminuji", password="password123")
        response = self.client.get(reverse("accounts:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard Administrator")
        self.assertContains(response, "Pengguna")
        self.assertContains(response, "Antrean QC")
