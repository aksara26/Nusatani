"""Pesanan, rincian item, dan catatan pembayaran simulasi (Tahap 4)."""

import secrets
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from products.models import Product


class OrderStatus(models.TextChoices):
    MENUNGGU_KONFIRMASI = "menunggu_konfirmasi", "Menunggu Konfirmasi"
    DIKONFIRMASI = "dikonfirmasi", "Dikonfirmasi"
    DALAM_PRODUKSI = "dalam_produksi", "Dalam Produksi"
    MENUNGGU_QC = "menunggu_qc", "Menunggu QC"
    QC_LOLOS = "qc_lolos", "QC Lolos"
    QC_DITOLAK = "qc_ditolak", "QC Ditolak"
    SIAP_DIKIRIM = "siap_dikirim", "Siap Dikirim"
    DALAM_PENGIRIMAN = "dalam_pengiriman", "Dalam Pengiriman"
    SELESAI = "selesai", "Selesai"
    DIBATALKAN = "dibatalkan", "Dibatalkan"


ALLOWED_TRANSITIONS = {
    OrderStatus.MENUNGGU_KONFIRMASI.value: {
        OrderStatus.DIKONFIRMASI.value,
        OrderStatus.DIBATALKAN.value,
    },
    OrderStatus.DIKONFIRMASI.value: {
        OrderStatus.DALAM_PRODUKSI.value,
        OrderStatus.DIBATALKAN.value,
    },
    OrderStatus.DALAM_PRODUKSI.value: {
        OrderStatus.MENUNGGU_QC.value,
        OrderStatus.DIBATALKAN.value,
    },
    OrderStatus.MENUNGGU_QC.value: {
        OrderStatus.QC_LOLOS.value,
        OrderStatus.QC_DITOLAK.value,
    },
    OrderStatus.QC_LOLOS.value: {OrderStatus.SIAP_DIKIRIM.value},
    OrderStatus.QC_DITOLAK.value: {
        OrderStatus.DALAM_PRODUKSI.value,
        OrderStatus.DIBATALKAN.value,
    },
    OrderStatus.SIAP_DIKIRIM.value: {
        OrderStatus.DALAM_PENGIRIMAN.value,
        OrderStatus.DIBATALKAN.value,
    },
    OrderStatus.DALAM_PENGIRIMAN.value: {OrderStatus.SELESAI.value},
    OrderStatus.SELESAI.value: set(),
    OrderStatus.DIBATALKAN.value: set(),
}

FARMER_MANAGEABLE_STATUSES = {
    OrderStatus.DIKONFIRMASI.value,
    OrderStatus.DALAM_PRODUKSI.value,
    OrderStatus.MENUNGGU_QC.value,
    OrderStatus.DIBATALKAN.value,
}


class OrderType(models.TextChoices):
    PREORDER = "preorder", "Pre-order HOREKA"
    SURPLUS = "surplus", "Pembelian Surplus"


class QcResult(models.TextChoices):
    MENUNGGU = "menunggu", "Menunggu pemeriksaan"
    LOLOS = "lolos", "Lolos"
    DITOLAK = "ditolak", "Ditolak"


def generate_order_number():
    """Nomor pesanan ringkas dan praktis tidak bentrok untuk MVP."""
    prefix = timezone.localdate().strftime("NT-%Y%m%d")
    return f"{prefix}-{secrets.token_hex(3).upper()}"


class Order(models.Model):
    order_number = models.CharField(max_length=32, unique=True, default=generate_order_number)
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders_as_buyer",
        verbose_name="Pembeli",
    )
    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders_as_farmer",
        verbose_name="Petani",
    )
    order_type = models.CharField(
        max_length=16, choices=OrderType.choices, default=OrderType.SURPLUS, verbose_name="Jenis pesanan"
    )
    status = models.CharField(
        max_length=32,
        choices=OrderStatus.choices,
        default=OrderStatus.MENUNGGU_KONFIRMASI,
        verbose_name="Status",
    )
    needed_by = models.DateField(null=True, blank=True, verbose_name="Dibutuhkan pada")
    notes = models.TextField(blank=True, verbose_name="Catatan pembeli")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Pesanan"
        verbose_name_plural = "Pesanan"

    def __str__(self):
        return self.order_number

    @property
    def total(self):
        return sum((item.line_total for item in self.items.all()), Decimal("0"))

    @property
    def total_quantity(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def qc_ready(self):
        """True hanya jika semua item sudah dinyatakan lolos QC."""
        items = list(self.items.all())
        return bool(items) and all(item.qc_result == QcResult.LOLOS.value for item in items)

    @property
    def status_badge_class(self):
        """Kelas Bootstrap untuk badge status pesanan."""
        return {
            OrderStatus.MENUNGGU_KONFIRMASI.value: "text-bg-warning",
            OrderStatus.DIKONFIRMASI.value: "text-bg-info",
            OrderStatus.DALAM_PRODUKSI.value: "text-bg-primary",
            OrderStatus.MENUNGGU_QC.value: "text-bg-secondary",
            OrderStatus.QC_LOLOS.value: "text-bg-success",
            OrderStatus.QC_DITOLAK.value: "text-bg-danger",
            OrderStatus.SIAP_DIKIRIM.value: "text-bg-success",
            OrderStatus.DALAM_PENGIRIMAN.value: "text-bg-info",
            OrderStatus.SELESAI.value: "text-bg-success",
            OrderStatus.DIBATALKAN.value: "text-bg-dark",
        }.get(self.status, "text-bg-secondary")

    def can_transition_to(self, new_status):
        return new_status in ALLOWED_TRANSITIONS.get(self.status, set())

    def transition_to(self, new_status):
        """Ubah status dengan memastikan urutan dan gate QC dipatuhi."""
        if not self.can_transition_to(new_status):
            raise ValueError(
                f"Transisi {self.status} → {new_status} tidak diizinkan."
            )
        if new_status in {
            OrderStatus.SIAP_DIKIRIM.value,
            OrderStatus.DALAM_PENGIRIMAN.value,
        } and not self.qc_ready:
            raise ValueError("Produk belum lolos QC sehingga belum boleh dikirim.")
        self.status = new_status
        self.save(update_fields=["status", "updated_at"])
        return self.status


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name="Jumlah")
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Harga satuan saat pesan",
    )
    qc_result = models.CharField(
        max_length=16,
        choices=QcResult.choices,
        default=QcResult.MENUNGGU.value,
        verbose_name="Hasil QC",
    )

    class Meta:
        verbose_name = "Item pesanan"
        verbose_name_plural = "Item pesanan"

    def __str__(self):
        return f"{self.product.name} × {self.quantity}"

    @property
    def line_total(self):
        return self.unit_price * self.quantity


class PaymentStatus(models.TextChoices):
    BELUM_DIBAYAR = "belum_dibayar", "Belum dibayar"
    MENUNGGU_KONFIRMASI = "menunggu_konfirmasi", "Menunggu konfirmasi"
    DP_TERCATAT = "dp_tercatat", "DP tercatat"
    LUNAS = "lunas", "Lunas"
    DIBATALKAN = "dibatalkan", "Dibatalkan"
    PENGEMBALIAN_DANA = "pengembalian_dana", "Pengembalian dana disimulasikan"


class PaymentRecord(models.Model):
    """Catatan pembayaran simulasi; aplikasi tidak menyimpan atau menahan uang."""

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    status = models.CharField(
        max_length=32,
        choices=PaymentStatus.choices,
        default=PaymentStatus.BELUM_DIBAYAR.value,
        verbose_name="Status pembayaran",
    )
    paid_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name="Jumlah tercatat",
    )
    note = models.TextField(blank=True, verbose_name="Catatan")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui")

    class Meta:
        verbose_name = "Catatan pembayaran"
        verbose_name_plural = "Catatan pembayaran"

    def __str__(self):
        return f"{self.order.order_number} — {self.get_status_display()}"
