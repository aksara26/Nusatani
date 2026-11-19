"""Katalog varietas, produk petani, dan stoknya (Tahap 3)."""

from datetime import date
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from accounts.roles import Role


class Variety(models.Model):
    """Jenis microgreens yang dikenal di platform, misalnya sawi putih atau Daun Katuk."""

    name = models.CharField(max_length=100, unique=True, verbose_name="Nama varietas")
    slug = models.SlugField(max_length=120, unique=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Deskripsi")

    class Meta:
        ordering = ["name"]
        verbose_name = "Varietas"
        verbose_name_plural = "Varietas"

    def __str__(self):
        return self.name


class Product(models.Model):
    """Produk yang ditawarkan seorang petani, baik reguler maupun surplus."""

    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="products",
        limit_choices_to={"role": Role.FARMER.value},
        verbose_name="Petani",
    )
    variety = models.ForeignKey(
        Variety,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="Varietas",
    )
    name = models.CharField(max_length=150, verbose_name="Nama produk")
    description = models.TextField(blank=True, verbose_name="Deskripsi")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Harga per pack",
    )
    photo_url = models.URLField(blank=True, verbose_name="URL foto produk")
    is_surplus = models.BooleanField(default=False, verbose_name="Produk surplus")
    available_from = models.DateField(default=date.today, verbose_name="Tanggal tersedia")
    is_active = models.BooleanField(default=True, verbose_name="Aktif ditampilkan")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui")

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["farmer", "name"],
                name="unique_product_name_per_farmer",
            )
        ]
        verbose_name = "Produk"
        verbose_name_plural = "Produk"

    def __str__(self):
        return self.name

    @property
    def stock(self):
        """Stok dari relasi Inventory; nol jika belum pernah dicatat."""
        inventory = getattr(self, "inventory", None)
        return inventory.quantity if inventory else 0

    @property
    def availability_status(self):
        """Status ketersediaan turunan dari aktif, stok, dan tanggal tersedia."""
        if not self.is_active:
            return "Nonaktif"
        if self.stock <= 0:
            return "Stok habis"
        if self.available_from and self.available_from > date.today():
            return "Akan tersedia"
        return "Tersedia"

    @property
    def availability_badge_class(self):
        """Kelas Bootstrap untuk badge status ketersediaan."""
        return {
            "Tersedia": "text-bg-success",
            "Akan tersedia": "text-bg-info",
            "Stok habis": "text-bg-danger",
            "Nonaktif": "text-bg-secondary",
        }.get(self.availability_status, "text-bg-secondary")


class Inventory(models.Model):
    """Catatan jumlah stok terkini untuk satu produk."""

    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="inventory",
        verbose_name="Produk",
    )
    quantity = models.PositiveIntegerField(default=0, verbose_name="Jumlah stok")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui")

    class Meta:
        verbose_name = "Stok"
        verbose_name_plural = "Stok"

    def __str__(self):
        return f"{self.product.name}: {self.quantity}"
