"""Pengujian alur pengiriman simulasi, termasuk Skenario 10 dan 11."""

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from orders.models import Order, OrderItem, OrderStatus, PaymentRecord, QcResult
from products.models import Inventory, Product, Variety

from .models import Delivery, DeliveryStatus

User = get_user_model()


class DeliveryFlowTests(TestCase):
    def setUp(self):
        self.farmer = User.objects.create_user(
            username="petaniuji", password="password123", role="farmer"
        )
        self.buyer = User.objects.create_user(
            username="konsumenuji", password="password123", role="consumer"
        )
        variety, _ = Variety.objects.get_or_create(
            slug="sawi-putih", defaults={"name": "Sawi Putih"}
        )
        self.product = Product.objects.create(
            farmer=self.farmer, variety=variety, name="Sawi Segar", price=Decimal("25000")
        )
        Inventory.objects.create(product=self.product, quantity=10)

    def make_order(self, status=OrderStatus.QC_LOLOS.value, qc_result=QcResult.LOLOS.value):
        order = Order.objects.create(
            buyer=self.buyer,
            farmer=self.farmer,
            order_type="surplus",
            status=status,
            needed_by=timezone.localdate() + timedelta(days=10),
        )
        OrderItem.objects.create(
            order=order, product=self.product, quantity=2, unit_price=self.product.price,
            qc_result=qc_result,
        )
        PaymentRecord.objects.create(order=order)
        return order

    def test_prepare_requires_qc_pass(self):
        order = self.make_order(status=OrderStatus.DALAM_PRODUKSI.value, qc_result=QcResult.MENUNGGU.value)
        self.client.login(username="petaniuji", password="password123")
        response = self.client.post(reverse("deliveries:prepare", args=[order.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Delivery.objects.exists())
        self.assertEqual(Order.objects.get(pk=order.pk).status, OrderStatus.DALAM_PRODUKSI.value)

    def test_full_delivery_flow(self):
        """Skenario 10 dan 11: dikirim lalu diterima, status pesanan ikut berjalan."""
        order = self.make_order()
        self.client.login(username="petaniuji", password="password123")
        response = self.client.post(
            reverse("deliveries:prepare", args=[order.pk]),
            {"courier_name": "Kurir ABC", "tracking_number": "TRACK-001", "notes": "Simulasi"},
        )
        self.assertEqual(response.status_code, 302)
        delivery = Delivery.objects.get(order=order)
        self.assertEqual(delivery.status, DeliveryStatus.DISIAPKAN.value)
        self.assertEqual(Order.objects.get(pk=order.pk).status, OrderStatus.SIAP_DIKIRIM.value)

        response = self.client.post(
            reverse("deliveries:update_status", args=[delivery.pk]), {"action": "dikirim"}
        )
        self.assertEqual(response.status_code, 302)
        delivery.refresh_from_db()
        self.assertEqual(delivery.status, DeliveryStatus.DIKIRIM.value)
        self.assertIsNotNone(delivery.sent_at)
        self.assertEqual(Order.objects.get(pk=order.pk).status, OrderStatus.DALAM_PENGIRIMAN.value)

        response = self.client.post(
            reverse("deliveries:update_status", args=[delivery.pk]), {"action": "diterima"}
        )
        self.assertEqual(response.status_code, 302)
        delivery.refresh_from_db()
        self.assertEqual(delivery.status, DeliveryStatus.DITERIMA.value)
        self.assertIsNotNone(delivery.received_at)
        self.assertEqual(Order.objects.get(pk=order.pk).status, OrderStatus.SELESAI.value)

    def test_buyer_cannot_prepare_delivery(self):
        order = self.make_order()
        self.client.login(username="konsumenuji", password="password123")
        response = self.client.post(reverse("deliveries:prepare", args=[order.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Delivery.objects.exists())

    def test_repeated_action_does_not_break(self):
        order = self.make_order()
        self.client.login(username="petaniuji", password="password123")
        self.client.post(
            reverse("deliveries:prepare", args=[order.pk]),
            {"courier_name": "Kurir ABC", "tracking_number": "", "notes": ""},
        )
        delivery = Delivery.objects.get(order=order)
        self.client.post(
            reverse("deliveries:update_status", args=[delivery.pk]), {"action": "dikirim"}
        )
        response = self.client.post(
            reverse("deliveries:update_status", args=[delivery.pk]), {"action": "dikirim"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Delivery.objects.get(pk=delivery.pk).status, DeliveryStatus.DIKIRIM.value)
        self.assertEqual(Order.objects.get(pk=order.pk).status, OrderStatus.DALAM_PENGIRIMAN.value)
