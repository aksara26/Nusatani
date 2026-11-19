"""Pencatatan aset usaha petani, starter kit, dan simulasi ijarah (Tahap 6)."""

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from accounts.roles import Role


class AssetCategory(models.TextChoices):
    RAK = "rak", "Rak budidaya"
    TRAY = "tray", "Tray tanam"
    LAMPU = "lampu", "Lampu budidaya"
    PANEN = "panen", "Peralatan panen"
    PENGEMASAN = "pengemasan", "Peralatan pengemasan"
    LAINNYA = "lainnya", "Lainnya"


class AssetCondition(models.TextChoices):
    BAIK = "baik", "Baik"
    CUKUP = "cukup", "Cukup"
    PERLU_PERBAIKAN = "perlu_perbaikan", "Perlu perbaikan"


class FinancingScheme(models.TextChoices):
    MILIK_SENDIRI = "milik_sendiri", "Milik sendiri"
    STARTER_KIT = "starter_kit", "Starter kit"
    IJARAH = "ijarah", "Ijarah (simulasi)"


class Asset(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assets",
        limit_choices_to={"role": Role.FARMER.value},
        verbose_name="Petani pemilik",
    )
    name = models.CharField(max_length=120, verbose_name="Nama aset")
    category = models.CharField(
        max_length=24,
        choices=AssetCategory.choices,
        default=AssetCategory.LAINNYA.value,
        verbose_name="Kategori",
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Jumlah",
    )
    unit = models.CharField(max_length=24, default="unit", verbose_name="Satuan")
    condition = models.CharField(
        max_length=20,
        choices=AssetCondition.choices,
        default=AssetCondition.BAIK.value,
        verbose_name="Kondisi",
    )
    acquisition_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Tanggal diperoleh",
    )
    financing_scheme = models.CharField(
        max_length=20,
        choices=FinancingScheme.choices,
        default=FinancingScheme.MILIK_SENDIRI.value,
        verbose_name="Skema perolehan",
    )
    ijarah_duration_months = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        verbose_name="Tenor ijarah (bulan)",
    )
    ijarah_monthly_payment = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Cicilan ijarah per bulan",
    )
    notes = models.TextField(blank=True, verbose_name="Catatan")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Aset petani"
        verbose_name_plural = "Aset petani"

    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})"

    @property
    def is_ijarah(self):
        return self.financing_scheme == FinancingScheme.IJARAH.value

    @property
    def is_starter_kit(self):
        return self.financing_scheme == FinancingScheme.STARTER_KIT.value

    @property
    def ijarah_total(self):
        """Total cicilan simulasi selama tenor, hanya untuk skema ijarah."""
        if not self.is_ijarah:
            return None
        if self.ijarah_duration_months is None or self.ijarah_monthly_payment is None:
            return None
        return Decimal(self.ijarah_duration_months) * self.ijarah_monthly_payment

    @property
    def condition_badge_class(self):
        return {
            AssetCondition.BAIK.value: "text-bg-success",
            AssetCondition.CUKUP.value: "text-bg-warning",
            AssetCondition.PERLU_PERBAIKAN.value: "text-bg-danger",
        }.get(self.condition, "text-bg-secondary")
