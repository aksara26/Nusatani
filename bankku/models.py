"""Ringkasan performa petani dan penilaian pembiayaan simulasi (Tahap 7)."""

from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


def _percentage(numerator, denominator):
    """Persentase 0–100 dengan dua angka desimal; nol jika tidak ada data."""
    if not denominator:
        return Decimal("0.00")
    value = Decimal(numerator) * Decimal("100") / Decimal(denominator)
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _weighted_score(percentage, weight):
    """Ubah persentase menjadi bobot nilai maksimal tertentu."""
    value = Decimal(percentage) * Decimal(weight) / Decimal("100")
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class FarmerPerformance(models.Model):
    farmer = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="performance",
        verbose_name="Petani",
    )
    total_orders = models.PositiveIntegerField(default=0, verbose_name="Total pesanan aktif")
    completed_orders = models.PositiveIntegerField(default=0, verbose_name="Pesanan selesai")
    total_order_value = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name="Total nilai pesanan",
    )
    fulfillment_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name="Konsistensi pemenuhan (%)",
    )
    quality_pass_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name="Tingkat lolos QC (%)",
    )
    asset_count = models.PositiveIntegerField(default=0, verbose_name="Jumlah aset tercatat")
    last_calculated_at = models.DateTimeField(null=True, blank=True, verbose_name="Dihitung pada")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui")

    class Meta:
        verbose_name = "Performa petani"
        verbose_name_plural = "Performa petani"

    def __str__(self):
        return f"Performa {self.farmer.username}"

    def recalculate(self):
        """Hitung ulang ringkasan dari data pesanan, QC, dan aset terkini."""
        from assets.models import Asset
        from orders.models import Order, OrderStatus
        from quality_control.models import QcStatus, QualityInspection

        orders = list(
            Order.objects.filter(farmer=self.farmer)
            .exclude(status=OrderStatus.DIBATALKAN.value)
            .prefetch_related("items")
        )
        inspections = QualityInspection.objects.filter(
            order_item__order__farmer=self.farmer
        )
        decided = inspections.filter(
            result__in=[QcStatus.LOLOS.value, QcStatus.DITOLAK.value]
        ).count()

        self.total_orders = len(orders)
        self.completed_orders = sum(
            1 for order in orders if order.status == OrderStatus.SELESAI.value
        )
        self.total_order_value = sum((order.total for order in orders), Decimal("0"))
        self.fulfillment_rate = _percentage(self.completed_orders, self.total_orders)
        self.quality_pass_rate = _percentage(
            inspections.filter(result=QcStatus.LOLOS.value).count(), decided
        )
        self.asset_count = Asset.objects.filter(owner=self.farmer).count()
        self.last_calculated_at = timezone.now()
        self.save()
        return self


class EligibilityBand(models.TextChoices):
    POTENSIAL = "potensial", "Potensial (simulasi)"
    PENDAMPINGAN = "pendampingan", "Perlu pendampingan"
    BELUM = "belum", "Belum memenuhi ambang simulasi"


class FinancingAssessment(models.Model):
    performance = models.OneToOneField(
        FarmerPerformance,
        on_delete=models.CASCADE,
        related_name="assessment",
        verbose_name="Performa petani",
    )
    fulfillment_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0"))
    quality_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0"))
    asset_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0"))
    mentorship_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0"))
    payment_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0"))
    total_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0"))
    eligibility = models.CharField(
        max_length=20,
        choices=EligibilityBand.choices,
        default=EligibilityBand.BELUM.value,
        verbose_name="Kategori indikator simulasi",
    )
    notes = models.TextField(blank=True, verbose_name="Catatan simulasi")
    calculated_at = models.DateTimeField(null=True, blank=True, verbose_name="Dihitung pada")

    class Meta:
        verbose_name = "Penilaian pembiayaan simulasi"
        verbose_name_plural = "Penilaian pembiayaan simulasi"

    def __str__(self):
        return f"Indikator {self.performance.farmer.username} — {self.total_score}"

    @property
    def eligibility_badge_class(self):
        return {
            EligibilityBand.POTENSIAL.value: "text-bg-success",
            EligibilityBand.PENDAMPINGAN.value: "text-bg-warning",
            EligibilityBand.BELUM.value: "text-bg-secondary",
        }.get(self.eligibility, "text-bg-secondary")

    def recalculate(self):
        """Hitung indikator 0–100 dari data yang sudah tercatat di aplikasi."""
        from mentorship.models import Mentorship, MentorshipActivity, MentorshipStatus
        from orders.models import Order, OrderStatus, PaymentRecord, PaymentStatus

        farmer = self.performance.farmer
        active_orders = (
            Order.objects.filter(farmer=farmer)
            .exclude(status=OrderStatus.DIBATALKAN.value)
            .values_list("pk", flat=True)
        )
        active_order_ids = list(active_orders)
        paid_orders = PaymentRecord.objects.filter(
            order_id__in=active_order_ids,
            status__in=[PaymentStatus.LUNAS.value, PaymentStatus.DP_TERCATAT.value],
        ).count()

        completed_mentorships = Mentorship.objects.filter(
            farmer=farmer, status=MentorshipStatus.SELESAI.value
        ).count()
        activity_count = MentorshipActivity.objects.filter(mentorship__farmer=farmer).count()
        mentorship_raw = min(Decimal(completed_mentorships * 5 + activity_count), Decimal("15"))

        self.fulfillment_score = _weighted_score(self.performance.fulfillment_rate, 30)
        self.quality_score = _weighted_score(self.performance.quality_pass_rate, 25)
        self.asset_score = min(Decimal(self.performance.asset_count * 4), Decimal("20"))
        self.mentorship_score = mentorship_raw
        self.payment_score = _weighted_score(
            _percentage(paid_orders, len(active_order_ids)), 10
        )
        self.total_score = sum(
            [
                self.fulfillment_score,
                self.quality_score,
                self.asset_score,
                self.mentorship_score,
                self.payment_score,
            ],
            Decimal("0"),
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        if self.total_score >= Decimal("75"):
            self.eligibility = EligibilityBand.POTENSIAL.value
        elif self.total_score >= Decimal("45"):
            self.eligibility = EligibilityBand.PENDAMPINGAN.value
        else:
            self.eligibility = EligibilityBand.BELUM.value

        self.notes = (
            "Indikator ini hanya simulasi berdasarkan data pesanan, kualitas, aset, "
            "pendampingan, dan catatan pembayaran. Bukan keputusan kredit atau penilaian resmi."
        )
        self.calculated_at = timezone.now()
        self.save()
        return self
