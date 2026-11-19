"""Simulasi kurir dan pelacakan pengiriman (Tahap 5)."""

from django.db import models

from orders.models import Order


class DeliveryStatus(models.TextChoices):
    DISIAPKAN = "disiapkan", "Disiapkan"
    DIKIRIM = "dikirim", "Dikirim"
    DITERIMA = "diterima", "Diterima"


class Delivery(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="delivery")
    courier_name = models.CharField(max_length=100, default="Kurir Simulasi", verbose_name="Nama kurir")
    tracking_number = models.CharField(max_length=100, blank=True, verbose_name="Nomor pelacakan")
    status = models.CharField(
        max_length=16,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.DISIAPKAN.value,
        verbose_name="Status pengiriman",
    )
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Dikirim pada")
    received_at = models.DateTimeField(null=True, blank=True, verbose_name="Diterima pada")
    notes = models.TextField(blank=True, verbose_name="Catatan")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Pengiriman"
        verbose_name_plural = "Pengiriman"

    def __str__(self):
        return f"{self.order.order_number} — {self.get_status_display()}"

    @property
    def status_badge_class(self):
        return {
            DeliveryStatus.DISIAPKAN.value: "text-bg-warning",
            DeliveryStatus.DIKIRIM.value: "text-bg-info",
            DeliveryStatus.DITERIMA.value: "text-bg-success",
        }.get(self.status, "text-bg-secondary")
