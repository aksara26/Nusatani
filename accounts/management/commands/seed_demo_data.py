"""Isi data demo lintas peran agar dashboard dan alur bisa dicek langsung."""

from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from accounts.models import CustomUser
from assets.models import Asset, AssetCategory, AssetCondition, FinancingScheme
from bankku.models import FarmerPerformance, FinancingAssessment
from deliveries.models import Delivery, DeliveryStatus
from mentorship.models import Mentorship, MentorshipActivity, MentorshipStatus
from orders.models import (
    Order,
    OrderItem,
    OrderStatus,
    OrderType,
    PaymentRecord,
    PaymentStatus,
    QcResult,
)
from products.models import Inventory, Product, Variety
from quality_control.models import QcStatus, QualityInspection

DEMO_ORDERS = (
    "NT-DEMO-0001",
    "NT-DEMO-0002",
    "NT-DEMO-0003",
    "NT-DEMO-0004",
    "NT-DEMO-0005",
)


class Command(BaseCommand):
    help = (
        "Buat produk, pesanan, QC, pengiriman, aset, dan pendampingan contoh. "
        "Aman dijalankan berulang kali karena data demo memakai penanda tetap."
    )

    def handle(self, *args, **options):
        try:
            petani = CustomUser.objects.get(username="petani1")
            horeca = CustomUser.objects.get(username="horeca1")
            konsumen = CustomUser.objects.get(username="konsumen1")
            qc = CustomUser.objects.get(username="qc1")
            mentor = CustomUser.objects.get(username="mentor1")
        except CustomUser.DoesNotExist as exc:
            raise CommandError(
                "Akun demo belum lengkap. Jalankan `python manage.py seed_demo_users` dulu."
            ) from exc

        with transaction.atomic():
            products = self._seed_products(petani)
            self._seed_orders(petani, horeca, konsumen, products)
            self._seed_assets(petani)
            self._seed_mentorship(petani, mentor)
            self._seed_performance(petani)

        self.stdout.write(
            self.style.SUCCESS(
                "Data demo siap: 4 produk, 5 pesanan, QC, pengiriman, 4 aset, "
                "2 pendampingan, dan indikator performa petani1."
            )
        )

    def _variety(self, name):
        variety, _ = Variety.objects.get_or_create(
            name=name, defaults={"slug": slugify(name)}
        )
        return variety

    def _seed_products(self, petani):
        specs = [
            ("Selada Microgreen Premium", "Selada", 18000, 40, False),
            ("Sawi Putih Segar", "Sawi Putih", 15000, 25, False),
            ("Brokoli Microgreen", "Brokoli", 22000, 12, False),
            ("Daun Katuk Surplus", "Daun Katuk", 12000, 8, True),
        ]
        products = {}
        for name, variety_name, price, stock, is_surplus in specs:
            product, _ = Product.objects.update_or_create(
                farmer=petani,
                name=name,
                defaults={
                    "variety": self._variety(variety_name),
                    "price": price,
                    "description": (
                        "Microgreens segar dari kebun dataran tinggi Nusantara."
                        if not is_surplus
                        else "Produk surplus hari ini dengan harga lebih hemat."
                    ),
                    "is_surplus": is_surplus,
                    "is_active": True,
                },
            )
            Inventory.objects.update_or_create(
                product=product, defaults={"quantity": stock}
            )
            products[name] = product
        return products

    def _make_order(
        self,
        number,
        buyer,
        farmer,
        status,
        order_type,
        items,
        payment_status,
        paid_amount,
        delivery_status=None,
        days_ago=0,
        needed_by=None,
        notes="",
    ):
        Order.objects.filter(order_number=number).delete()
        order = Order.objects.create(
            order_number=number,
            buyer=buyer,
            farmer=farmer,
            status=status,
            order_type=order_type,
            needed_by=needed_by,
            notes=notes,
        )
        for product, quantity, qc_result in items:
            item = OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=product.price,
                qc_result=qc_result,
            )
            if qc_result == QcResult.LOLOS.value:
                QualityInspection.objects.create(
                    order_item=item,
                    inspector=CustomUser.objects.get(username="qc1"),
                    visual_ok=True,
                    cleanliness_ok=True,
                    freshness_ok=True,
                    weight_ok=True,
                    notes="Sesuai standar pengiriman.",
                    result=QcStatus.LOLOS.value,
                    inspected_at=timezone.now(),
                )
            elif status == OrderStatus.MENUNGGU_QC.value:
                QualityInspection.objects.create(
                    order_item=item,
                    notes="Menunggu pemeriksaan petugas QC.",
                )

        PaymentRecord.objects.create(
            order=order, status=payment_status, paid_amount=paid_amount
        )

        if delivery_status:
            sent_at = timezone.now() - timedelta(days=max(days_ago - 1, 0))
            Delivery.objects.create(
                order=order,
                status=delivery_status,
                tracking_number=f"TRK-{number[-4:]}",
                sent_at=sent_at,
                received_at=(
                    timezone.now() - timedelta(hours=6)
                    if delivery_status == DeliveryStatus.DITERIMA.value
                    else None
                ),
                notes="Pengiriman simulasi NusaTani.",
            )

        Order.objects.filter(pk=order.pk).update(
            created_at=timezone.now() - timedelta(days=days_ago)
        )
        return order

    def _seed_orders(self, petani, horeca, konsumen, products):
        selada = products["Selada Microgreen Premium"]
        sawi = products["Sawi Putih Segar"]
        brokoli = products["Brokoli Microgreen"]
        surplus = products["Daun Katuk Surplus"]
        today = timezone.localdate()

        self._make_order(
            "NT-DEMO-0001",
            horeca,
            petani,
            OrderStatus.SELESAI.value,
            OrderType.PREORDER.value,
            [(selada, 10, QcResult.LOLOS.value), (sawi, 5, QcResult.LOLOS.value)],
            PaymentStatus.LUNAS.value,
            255000,
            delivery_status=DeliveryStatus.DITERIMA.value,
            days_ago=12,
            needed_by=today - timedelta(days=9),
            notes="Pesanan rutin mingguan HOREKA.",
        )
        self._make_order(
            "NT-DEMO-0002",
            konsumen,
            petani,
            OrderStatus.MENUNGGU_KONFIRMASI.value,
            OrderType.SURPLUS.value,
            [(surplus, 2, QcResult.MENUNGGU.value)],
            PaymentStatus.BELUM_DIBAYAR.value,
            0,
            days_ago=1,
            notes="Ambil produk surplus sore ini.",
        )
        self._make_order(
            "NT-DEMO-0003",
            horeca,
            petani,
            OrderStatus.DALAM_PRODUKSI.value,
            OrderType.PREORDER.value,
            [(brokoli, 6, QcResult.MENUNGGU.value)],
            PaymentStatus.DP_TERCATAT.value,
            50000,
            days_ago=5,
            needed_by=today + timedelta(days=4),
            notes="Pre-order untuk menu akhir pekan.",
        )
        self._make_order(
            "NT-DEMO-0004",
            horeca,
            petani,
            OrderStatus.MENUNGGU_QC.value,
            OrderType.PREORDER.value,
            [(selada, 4, QcResult.MENUNGGU.value)],
            PaymentStatus.BELUM_DIBAYAR.value,
            0,
            days_ago=2,
            needed_by=today + timedelta(days=2),
            notes="Menunggu pemeriksaan kualitas.",
        )
        self._make_order(
            "NT-DEMO-0005",
            konsumen,
            petani,
            OrderStatus.SIAP_DIKIRIM.value,
            OrderType.SURPLUS.value,
            [(sawi, 3, QcResult.LOLOS.value)],
            PaymentStatus.LUNAS.value,
            45000,
            delivery_status=DeliveryStatus.DISIAPKAN.value,
            days_ago=3,
            notes="Sudah lolos QC, menunggu kurir simulasi.",
        )

    def _seed_assets(self, petani):
        specs = [
            ("Rak budidaya 3 tingkat", AssetCategory.RAK.value, 3, "unit", AssetCondition.BAIK.value, FinancingScheme.MILIK_SENDIRI.value),
            ("Tray tanam 40x30", AssetCategory.TRAY.value, 24, "tray", AssetCondition.BAIK.value, FinancingScheme.MILIK_SENDIRI.value),
            ("Lampu LED grow light", AssetCategory.LAMPU.value, 4, "unit", AssetCondition.CUKUP.value, FinancingScheme.IJARAH.value),
            ("Gunting panen", AssetCategory.PANEN.value, 2, "unit", AssetCondition.BAIK.value, FinancingScheme.MILIK_SENDIRI.value),
        ]
        for name, category, quantity, unit, condition, scheme in specs:
            Asset.objects.update_or_create(
                owner=petani,
                name=name,
                defaults={
                    "category": category,
                    "quantity": quantity,
                    "unit": unit,
                    "condition": condition,
                    "financing_scheme": scheme,
                    "ijarah_duration_months": 6 if scheme == FinancingScheme.IJARAH.value else None,
                    "ijarah_monthly_payment": 85000 if scheme == FinancingScheme.IJARAH.value else None,
                },
            )

    def _seed_mentorship(self, petani, mentor):
        active, _ = Mentorship.objects.update_or_create(
            farmer=petani,
            mentor=mentor,
            topic="Pengaturan cahaya dan kelembapan",
            defaults={
                "description": "Evaluasi kondisi rak dan jadwal penyiraman.",
                "scheduled_at": timezone.now() + timedelta(days=2, hours=9),
                "status": MentorshipStatus.DIJADWALKAN.value,
            },
        )
        MentorshipActivity.objects.update_or_create(
            mentorship=active,
            description="Pengecekan awal media tanam dan intensitas lampu.",
            defaults={
                "author": mentor,
                "evaluation": "Media tanam perlu ditambah perlite.",
            },
        )

        completed, _ = Mentorship.objects.update_or_create(
            farmer=petani,
            mentor=mentor,
            topic="Panen dan pengemasan",
            defaults={
                "description": "Standar panen, sortir, dan pengemasan produk.",
                "scheduled_at": timezone.now() - timedelta(days=3),
                "status": MentorshipStatus.SELESAI.value,
                "evaluation": "Pemilik usaha siap melakukan panen mandiri.",
            },
        )
        MentorshipActivity.objects.update_or_create(
            mentorship=completed,
            description="Praktik panen dan penimbangan produk.",
            defaults={
                "author": mentor,
                "evaluation": "Hasil panen konsisten, pengemasan rapi.",
            },
        )

    def _seed_performance(self, petani):
        performance, _ = FarmerPerformance.objects.get_or_create(farmer=petani)
        performance.recalculate()
        assessment, _ = FinancingAssessment.objects.get_or_create(performance=performance)
        assessment.recalculate()
