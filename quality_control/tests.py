"""Pengujian quality gate, termasuk Skenario 7, 8, dan 9."""

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from deliveries.models import Delivery
from orders.models import Order, OrderItem, OrderStatus, PaymentRecord, QcResult
from products.models import Inventory, Product, Variety

from .models import QcStatus, QualityInspection

User = get_user_model()


class QualityControlTests(TestCase):
    def setUp(self):
        self.farmer = User.objects.create_user(
            username="petaniuji", password="password123", role="farmer"
        )
        self.qc = User.objects.create_user(
            username="qcuJI", password="password123", role="qc"
        )
        self.buyer = User.objects.create_user(
            username="horecauji", password="password123", role="horeca"
        )
        variety, _ = Variety.objects.get_or_create(
            slug="sawi-putih", defaults={"name": "Sawi Putih"}
        )
        self.product = Product.objects.create(
            farmer=self.farmer, variety=variety, name="Sawi Segar", price=Decimal("25000")
        )
        Inventory.objects.create(product=self.product, quantity=10)

    def make_order(self, status=OrderStatus.DALAM_PRODUKSI.value, items=1):
        order = Order.objects.create(
            buyer=self.buyer,
            farmer=self.farmer,
            order_type="preorder",
            status=status,
            needed_by=timezone.localdate() + timedelta(days=10),
        )
        for index in range(items):
            OrderItem.objects.create(
                order=order,
                product=self.product,
                quantity=1,
                unit_price=self.product.price,
            )
        PaymentRecord.objects.create(order=order)
        return order

    def make_inspection(self, item, result=QcStatus.MENUNGGU.value):
        return QualityInspection.objects.create(order_item=item, result=result)

    def test_farmer_submits_order_to_qc(self):
        """Skenario 7: status berubah menjadi menunggu QC dan antrean terbentuk."""
        order = self.make_order()
        self.client.login(username="petaniuji", password="password123")
        response = self.client.post(reverse("quality_control:submit_to_qc", args=[order.pk]))
        self.assertEqual(response.status_code, 302)

        updated = Order.objects.get(pk=order.pk)
        self.assertEqual(updated.status, OrderStatus.MENUNGGU_QC.value)
        inspection = QualityInspection.objects.get(order_item__order=updated)
        self.assertEqual(inspection.result, QcStatus.MENUNGGU.value)

    def test_non_farmer_cannot_submit_to_qc(self):
        order = self.make_order()
        self.client.login(username="horecauji", password="password123")
        response = self.client.post(reverse("quality_control:submit_to_qc", args=[order.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Order.objects.get(pk=order.pk).status, OrderStatus.DALAM_PRODUKSI.value)

    def test_qc_approves_product(self):
        """Skenario 8: QC lolos dan pesanan menjadi QC Lolos."""
        order = self.make_order(OrderStatus.MENUNGGU_QC.value)
        inspection = self.make_inspection(order.items.first())
        self.client.login(username="qcuJI", password="password123")
        response = self.client.post(
            reverse("quality_control:inspect", args=[inspection.pk]),
            {
                "visual_ok": "on",
                "cleanliness_ok": "on",
                "freshness_ok": "on",
                "weight_ok": "on",
                "notes": "Semua aspek sesuai standar.",
                "result": QcStatus.LOLOS.value,
            },
        )
        self.assertEqual(response.status_code, 302)

        inspection.refresh_from_db()
        self.assertEqual(inspection.result, QcStatus.LOLOS.value)
        self.assertEqual(inspection.inspector, self.qc)
        self.assertIsNotNone(inspection.inspected_at)
        item = order.items.first()
        item.refresh_from_db()
        self.assertEqual(item.qc_result, QcResult.LOLOS.value)
        self.assertEqual(Order.objects.get(pk=order.pk).status, OrderStatus.QC_LOLOS.value)

    def test_qc_rejects_product_and_blocks_delivery(self):
        """Skenario 9: produk ditolak QC tidak dapat dikirim."""
        order = self.make_order(OrderStatus.MENUNGGU_QC.value)
        inspection = self.make_inspection(order.items.first())
        self.client.login(username="qcuJI", password="password123")
        response = self.client.post(
            reverse("quality_control:inspect", args=[inspection.pk]),
            {"notes": "Kesegaran kurang.", "result": QcStatus.DITOLAK.value},
        )
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Order.objects.get(pk=order.pk).status, OrderStatus.QC_DITOLAK.value)
        self.assertEqual(
            OrderItem.objects.get(pk=order.items.first().pk).qc_result,
            QcResult.DITOLAK.value,
        )

        self.client.logout()
        self.client.login(username="petaniuji", password="password123")
        self.client.post(reverse("deliveries:prepare", args=[order.pk]))
        self.assertFalse(Delivery.objects.exists())
        self.assertEqual(Order.objects.get(pk=order.pk).status, OrderStatus.QC_DITOLAK.value)

    def test_partial_approval_keeps_order_waiting(self):
        order = self.make_order(OrderStatus.MENUNGGU_QC.value, items=2)
        items = list(order.items.all())
        first, second = [self.make_inspection(item) for item in items]
        self.client.login(username="qcuJI", password="password123")
        self.client.post(
            reverse("quality_control:inspect", args=[first.pk]),
            {"result": QcStatus.LOLOS.value, "notes": ""},
        )
        self.assertEqual(Order.objects.get(pk=order.pk).status, OrderStatus.MENUNGGU_QC.value)

        self.client.post(
            reverse("quality_control:inspect", args=[second.pk]),
            {"result": QcStatus.LOLOS.value, "notes": ""},
        )
        self.assertEqual(Order.objects.get(pk=order.pk).status, OrderStatus.QC_LOLOS.value)

    def test_queue_requires_qc_role(self):
        self.client.login(username="petaniuji", password="password123")
        response = self.client.get(reverse("quality_control:queue"))
        self.assertEqual(response.status_code, 403)
