"""Bersihkan data demo sebelum aplikasi dipakai dengan data sungguhan."""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from accounts.models import CustomUser
from assets.models import Asset
from bankku.models import FarmerPerformance, FinancingAssessment
from deliveries.models import Delivery
from mentorship.models import Mentorship, MentorshipActivity
from orders.models import Order
from products.models import Product, Variety
from quality_control.models import QualityInspection


class Command(BaseCommand):
    help = (
        "Hapus pesanan, QC, pengiriman, aset, pendampingan, dan data performa demo. "
        "Akun pengguna dan varietas dipertahankan."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Konfirmasi penghapusan data demo.",
        )

    def handle(self, *args, **options):
        if not options["yes"]:
            raise CommandError(
                "Perintah ini destruktif. Jalankan lagi dengan --yes jika Anda yakin."
            )

        with transaction.atomic():
            delivery_count = Delivery.objects.count()
            inspection_count = QualityInspection.objects.count()
            order_count = Order.objects.count()
            asset_count = Asset.objects.count()
            activity_count = MentorshipActivity.objects.count()
            mentorship_count = Mentorship.objects.count()
            performance_count = FarmerPerformance.objects.count()
            assessment_count = FinancingAssessment.objects.count()
            product_count = Product.objects.count()

            Delivery.objects.all().delete()
            QualityInspection.objects.all().delete()
            Order.objects.all().delete()
            Asset.objects.all().delete()
            MentorshipActivity.objects.all().delete()
            Mentorship.objects.all().delete()
            FinancingAssessment.objects.all().delete()
            FarmerPerformance.objects.all().delete()
            Product.objects.all().delete()

        self.stdout.write(
            self.style.SUCCESS(
                "Data demo dibersihkan: "
                f"{delivery_count} pengiriman, {inspection_count} QC, "
                f"{order_count} pesanan, {asset_count} aset, "
                f"{activity_count} kegiatan mentor, {mentorship_count} pendampingan, "
                f"{assessment_count} penilaian, {performance_count} performa, "
                f"{product_count} produk."
            )
        )
        self.stdout.write(
            f"Dipertahankan: {CustomUser.objects.count()} akun dan {Variety.objects.count()} varietas."
        )
