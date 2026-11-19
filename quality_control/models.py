"""Pemeriksaan kualitas produk sebelum pengiriman (Tahap 5)."""

from django.conf import settings
from django.db import models

from orders.models import OrderItem


class QcStatus(models.TextChoices):
    MENUNGGU = "menunggu", "Menunggu pemeriksaan"
    DIPERIKSA = "diperiksa", "Sedang diperiksa"
    LOLOS = "lolos", "Lolos QC"
    DITOLAK = "ditolak", "Tidak lolos QC"


class QualityInspection(models.Model):
    order_item = models.ForeignKey(
        OrderItem, on_delete=models.CASCADE, related_name="inspections", verbose_name="Item pesanan"
    )
    inspector = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inspections",
        verbose_name="Petugas QC",
    )
    visual_ok = models.BooleanField(default=False, verbose_name="Kondisi visual sesuai")
    cleanliness_ok = models.BooleanField(default=False, verbose_name="Kebersihan sesuai")
    freshness_ok = models.BooleanField(default=False, verbose_name="Kesegaran sesuai")
    weight_ok = models.BooleanField(default=False, verbose_name="Kesesuaian berat")
    notes = models.TextField(blank=True, verbose_name="Catatan perbaikan")
    result = models.CharField(
        max_length=16,
        choices=QcStatus.choices,
        default=QcStatus.MENUNGGU.value,
        verbose_name="Hasil pemeriksaan",
    )
    inspected_at = models.DateTimeField(null=True, blank=True, verbose_name="Diperiksa pada")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Pemeriksaan kualitas"
        verbose_name_plural = "Pemeriksaan kualitas"

    def __str__(self):
        return f"{self.order_item} — {self.get_result_display()}"

    @property
    def product(self):
        return self.order_item.product

    @property
    def result_badge_class(self):
        return {
            QcStatus.MENUNGGU.value: "text-bg-warning",
            QcStatus.DIPERIKSA.value: "text-bg-info",
            QcStatus.LOLOS.value: "text-bg-success",
            QcStatus.DITOLAK.value: "text-bg-danger",
        }.get(self.result, "text-bg-secondary")
