"""Pengujian alur transaksi Tahap 4, termasuk Skenario 5 dan 6."""

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from products.models import Inventory, Product, Variety

from .models import (
    Order,
    OrderItem,
    OrderStatus,
    OrderType,
    PaymentRecord,
    PaymentStatus,
    QcResult,
)

User = get_user_model()


class OrderFlowTests(TestCase):
    def setUp(self):
        self.farmer = User.objects.create_user(
            username="petaniuji", password="password123", role="farmer"
        )
        self.horeca = User.objects.create_user(
            username="horecauji", password="password123", role="horeca"
        )
        self.consumer = User.objects.create_user(
            username="konsumenuji", password="password123", role="consumer"
        )
        variety, _ = Variety.objects.get_or_create(
            slug="sawi-putih", defaults={"name": "Sawi Putih"}
        )
        self.product = Product.objects.create(
            farmer=self.farmer,
            variety=variety,
            name="Sawi Segar",
            price=Decimal("25000"),
            is_surplus=True,
        )
        Inventory.objects.create(product=self.product, quantity=10)

    def make_order(self, buyer=None, order_type=OrderType.PREORDER.value):
        order = Order.objects.create(
            buyer=buyer or self.horeca,
            farmer=self.farmer,
            order_type=order_type,
            needed_by=timezone.localdate() + timedelta(days=10),
        )
        OrderItem.objects.create(
            order=order, product=self.product, quantity=2, unit_price=self.product.price
        )
        PaymentRecord.objects.create(order=order)
        return order

    def test_horeka_creates_preorder(self):
        """Skenario 5: pre-order HOREKA tercatat beserta item dan pembayaran simulasi."""
        self.client.login(username="horecauji", password="password123")
        needed = (timezone.localdate() + timedelta(days=10)).isoformat()
        response = self.client.post(
            reverse("orders:preorder_create"),
            {
                "product": self.product.pk,
                "quantity": 2,
                "needed_by": needed,
                "notes": "Butuh setiap Selasa",
            },
        )
        self.assertEqual(response.status_code, 302)
        order = Order.objects.get()
        self.assertEqual(order.buyer, self.horeca)
        self.assertEqual(order.farmer, self.farmer)
        self.assertEqual(order.order_type, OrderType.PREORDER.value)
        self.assertEqual(order.status, OrderStatus.MENUNGGU_KONFIRMASI.value)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.payment.status, PaymentStatus.BELUM_DIBAYAR.value)
        self.assertEqual(order.total, Decimal("50000"))

    def test_consumer_buys_surplus_and_stock_decreases(self):
        """Skenario 6: pembelian surplus tercatat dan stok berkurang."""
        self.client.login(username="konsumenuji", password="password123")
        response = self.client.post(
            reverse("orders:surplus_create"),
            {"product": self.product.pk, "quantity": 3},
        )
        self.assertEqual(response.status_code, 302)
        order = Order.objects.get()
        self.assertEqual(order.order_type, OrderType.SURPLUS.value)
        self.assertEqual(order.items.count(), 1)
        inventory = Inventory.objects.get(product=self.product)
        self.assertEqual(inventory.quantity, 7)

    def test_preorder_window_is_7_to_14_days(self):
        self.client.login(username="horecauji", password="password123")
        too_soon = (timezone.localdate() + timedelta(days=3)).isoformat()
        response = self.client.post(
            reverse("orders:preorder_create"),
            {"product": self.product.pk, "quantity": 1, "needed_by": too_soon},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "7–14 hari")
        self.assertFalse(Order.objects.exists())

    def test_surplus_order_cannot_exceed_stock(self):
        self.client.login(username="konsumenuji", password="password123")
        response = self.client.post(
            reverse("orders:surplus_create"),
            {"product": self.product.pk, "quantity": 99},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Stok yang tersedia")
        self.assertFalse(Order.objects.exists())
        self.assertEqual(Inventory.objects.get(product=self.product).quantity, 10)

    def test_farmer_cannot_jump_status_to_shipping(self):
        order = self.make_order()
        self.assertFalse(order.can_transition_to(OrderStatus.SIAP_DIKIRIM.value))
        with self.assertRaises(ValueError):
            order.transition_to(OrderStatus.SIAP_DIKIRIM.value)

        self.client.login(username="petaniuji", password="password123")
        response = self.client.post(
            reverse("orders:update_status", args=[order.pk]),
            {"status": OrderStatus.SIAP_DIKIRIM.value},
        )
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, OrderStatus.MENUNGGU_KONFIRMASI.value)

    def test_farmer_can_advance_until_waiting_for_qc(self):
        order = self.make_order()
        self.client.login(username="petaniuji", password="password123")
        for expected in [
            OrderStatus.DIKONFIRMASI.value,
            OrderStatus.DALAM_PRODUKSI.value,
            OrderStatus.MENUNGGU_QC.value,
        ]:
            response = self.client.post(
                reverse("orders:update_status", args=[order.pk]),
                {"status": expected},
            )
            self.assertEqual(response.status_code, 302)
            order.refresh_from_db()
            self.assertEqual(order.status, expected)

        response = self.client.get(reverse("orders:detail", args=[order.pk]))
        self.assertNotContains(response, "Perbarui status")

    def test_qc_gate_blocks_shipping_until_items_pass(self):
        order = self.make_order()
        order.status = OrderStatus.QC_LOLOS.value
        order.save(update_fields=["status"])
        with self.assertRaises(ValueError):
            order.transition_to(OrderStatus.SIAP_DIKIRIM.value)

        order.items.update(qc_result=QcResult.LOLOS.value)
        order = Order.objects.get(pk=order.pk)
        self.assertTrue(order.qc_ready)
        self.assertEqual(
            order.transition_to(OrderStatus.SIAP_DIKIRIM.value),
            OrderStatus.SIAP_DIKIRIM.value,
        )

    def test_buyer_cannot_open_incoming_orders_page(self):
        self.client.login(username="konsumenuji", password="password123")
        response = self.client.get(reverse("orders:incoming"))
        self.assertEqual(response.status_code, 403)

    def test_farmer_updates_payment_simulation(self):
        order = self.make_order(order_type=OrderType.SURPLUS.value)
        self.client.login(username="petaniuji", password="password123")
        response = self.client.post(
            reverse("orders:update_payment", args=[order.pk]),
            {
                "status": PaymentStatus.DP_TERCATAT.value,
                "paid_amount": "12500",
                "note": "DP 50% (simulasi)",
            },
        )
        self.assertEqual(response.status_code, 302)
        payment = PaymentRecord.objects.get(order=order)
        self.assertEqual(payment.status, PaymentStatus.DP_TERCATAT.value)
        self.assertEqual(payment.paid_amount, Decimal("12500"))
