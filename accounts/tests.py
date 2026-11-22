"""Verifikasi alur login dan dashboard untuk seluruh akun demo NusaTani."""

from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from assets.models import Asset
from bankku.models import FarmerPerformance, FinancingAssessment
from mentorship.models import Mentorship, MentorshipActivity
from orders.models import Order, OrderItem, PaymentRecord
from products.models import Product, Variety

from .roles import ROLE_DASHBOARDS

User = get_user_model()

DEMO_ACCOUNTS = [
    ("admin", "admin", True),
    ("petani1", "farmer", False),
    ("horeca1", "horeca", False),
    ("konsumen1", "consumer", False),
    ("qc1", "qc", False),
    ("mentor1", "mentor", False),
    ("bank1", "bank", False),
]

# Penanda bahwa dashboard benar-benar berbeda per peran, bukan template generik.
DASHBOARD_MARKERS = {
    "admin": "Pengguna",
    "farmer": "Produk aktif",
    "horeca": "Buat pre-order",
    "consumer": "Pesanan surplus",
    "qc": "Antrean QC",
    "mentor": "Petani dibimbing",
    "bank": "Rata-rata skor",
}


class DemoLoginTests(TestCase):
    def test_all_demo_accounts_can_login_and_open_own_dashboard(self):
        call_command("seed_demo_users", verbosity=0)

        for username, role, _is_admin in DEMO_ACCOUNTS:
            with self.subTest(username=username):
                self.client.logout()
                response = self.client.post(
                    reverse("accounts:login"),
                    {"username": username, "password": "password123"},
                )
                self.assertEqual(response.status_code, 302, msg=f"login gagal untuk {username}")
                self.assertEqual(response.url, reverse("accounts:dashboard"))

                dashboard = self.client.get(reverse("accounts:dashboard"))
                self.assertEqual(dashboard.status_code, 200)
                self.assertContains(dashboard, ROLE_DASHBOARDS[role]["label"])
                self.assertContains(dashboard, DASHBOARD_MARKERS[role])

    def test_seed_command_repairs_existing_account_with_bad_password(self):
        broken, _ = User.objects.update_or_create(
            username="petani1", defaults={"role": "farmer"}
        )
        broken.password = "plaintext-tanpa-hash"
        broken.save(update_fields=["password"])
        self.assertFalse(broken.check_password("password123"))

        call_command("seed_demo_users", verbosity=0)
        broken.refresh_from_db()
        self.assertTrue(broken.check_password("password123"))

        self.client.logout()
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "petani1", "password": "password123"},
        )
        self.assertRedirects(response, reverse("accounts:dashboard"))

    def test_seed_demo_data_is_idempotent_and_fills_each_area(self):
        call_command("seed_demo_users", verbosity=0)
        call_command("seed_demo_data", verbosity=0)
        call_command("seed_demo_data", verbosity=0)

        self.assertEqual(
            Product.objects.filter(farmer__username="petani1").count(), 4
        )
        self.assertEqual(
            Order.objects.filter(order_number__startswith="NT-DEMO").count(), 5
        )
        self.assertEqual(Asset.objects.filter(owner__username="petani1").count(), 4)
        self.assertEqual(
            Mentorship.objects.filter(mentor__username="mentor1").count(), 2
        )
        self.assertTrue(
            FarmerPerformance.objects.filter(farmer__username="petani1").exists()
        )
        self.assertTrue(
            FinancingAssessment.objects.filter(
                performance__farmer__username="petani1"
            ).exists()
        )

    def test_guide_links_to_real_registration_not_demo_credentials(self):
        guide = self.client.get(reverse("accounts:guide"))
        self.assertEqual(guide.status_code, 200)
        self.assertContains(guide, 'data-role="farmer"')
        self.assertContains(guide, 'data-register-url="/accounts/daftar/?role=farmer"')
        self.assertContains(guide, "Lanjut ke pendaftaran")
        self.assertNotContains(guide, "password123")
        self.assertNotContains(guide, "Akun demo")

    def test_registration_creates_account_then_login_works(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "petanibaru",
                "email": "petanibaru@example.com",
                "first_name": "Sari",
                "last_name": "Utami",
                "role": "farmer",
                "password1": "password123",
                "password2": "password123",
            },
        )
        self.assertRedirects(response, reverse("accounts:login"))

        user = User.objects.get(username="petanibaru")
        self.assertEqual(user.role, "farmer")
        self.assertTrue(user.check_password("password123"))

        login = self.client.post(
            reverse("accounts:login"),
            {"username": "petanibaru", "password": "password123"},
        )
        self.assertRedirects(login, reverse("accounts:dashboard"))

    def test_registration_rejects_internal_roles_and_weak_password(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "qcbaru",
                "email": "qcbaru@example.com",
                "role": "qc",
                "password1": "pendek",
                "password2": "pendek",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="qcbaru").exists())
        self.assertContains(response, "Password minimal 8 karakter")

    def test_registration_form_prefills_role_from_guide(self):
        response = self.client.get(reverse("accounts:register"), {"role": "horeca"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="horeca" selected')
        self.assertContains(response, "Nama usaha HOREKA")
        self.assertContains(response, "Email usaha")

    def test_registration_fields_and_guidance_match_selected_role(self):
        farmer = self.client.get(reverse("accounts:register"), {"role": "farmer"})
        self.assertContains(farmer, "Nama usaha / kelompok tani")
        self.assertContains(farmer, "Alamat atau daerah lahan belum diminta")

        consumer = self.client.get(reverse("accounts:register"), {"role": "consumer"})
        self.assertContains(consumer, "Email pembeli")
        self.assertContains(consumer, "alamat rumah tidak diminta")

    def test_wrong_password_is_rejected(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "petani1", "password": "salah"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Username atau password salah")
        self.assertContains(response, "password harus sama persis")

    def test_login_tolerates_spaces_and_capitalization(self):
        for typed_username in ("petani 1", " Petani1 ", "PETANI1"):
            with self.subTest(typed_username=typed_username):
                self.client.logout()
                response = self.client.post(
                    reverse("accounts:login"),
                    {"username": typed_username, "password": "password123"},
                )
                self.assertRedirects(response, reverse("accounts:dashboard"))


class PurgeDemoDataTests(TestCase):
    def setUp(self):
        self.farmer = User.objects.create_user(
            username="petaniuji", password="password123", role="farmer"
        )
        self.mentor = User.objects.create_user(
            username="mentoruji", password="password123", role="mentor"
        )
        variety, _ = Variety.objects.get_or_create(
            slug="sawi-putih", defaults={"name": "Sawi Putih"}
        )
        self.product = Product.objects.create(
            farmer=self.farmer, variety=variety, name="Sawi Demo", price=Decimal("25000")
        )
        self.order = Order.objects.create(buyer=self.farmer, farmer=self.farmer)
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            unit_price=self.product.price,
        )
        PaymentRecord.objects.create(order=self.order)
        self.asset = Asset.objects.create(name="Rak demo", owner=self.farmer)
        self.mentorship = Mentorship.objects.create(
            farmer=self.farmer,
            mentor=self.mentor,
            topic="Materi demo",
            scheduled_at=timezone.now(),
        )
        MentorshipActivity.objects.create(
            mentorship=self.mentorship, description="Kegiatan demo", author=self.mentor
        )
        self.performance, _ = FarmerPerformance.objects.get_or_create(farmer=self.farmer)
        FinancingAssessment.objects.get_or_create(performance=self.performance)

    def test_purge_requires_confirmation(self):
        with self.assertRaises(CommandError):
            call_command("purge_demo_data")
        self.assertTrue(Order.objects.exists())
        self.assertTrue(Asset.objects.exists())

    def test_purge_removes_demo_data_but_keeps_users_and_varieties(self):
        call_command("purge_demo_data", "--yes")
        self.assertFalse(Order.objects.exists())
        self.assertFalse(Asset.objects.exists())
        self.assertFalse(Mentorship.objects.exists())
        self.assertFalse(MentorshipActivity.objects.exists())
        self.assertFalse(FarmerPerformance.objects.exists())
        self.assertFalse(FinancingAssessment.objects.exists())
        self.assertFalse(Product.objects.exists())
        self.assertTrue(User.objects.filter(username="petaniuji").exists())
        self.assertTrue(Variety.objects.exists())


class GuideAndProfileTests(TestCase):
    def test_new_visitor_is_guided_before_login(self):
        response = self.client.get(reverse("home"))
        self.assertRedirects(response, reverse("accounts:guide"))

        guide = self.client.get(reverse("accounts:guide"))
        self.assertEqual(guide.status_code, 200)
        self.assertContains(guide, "Sebelum masuk, pilih peran Anda")
        self.assertContains(guide, "Cara daftar")
        self.assertContains(guide, "Lewati panduan")
        self.assertNotContains(guide, "password123")

    def test_skip_guide_remembers_choice(self):
        response = self.client.get(reverse("accounts:guide"), {"skip": "1"})
        self.assertRedirects(response, reverse("accounts:login"))
        self.assertTrue(self.client.session.get("nt_guide_seen"))

        response = self.client.get(reverse("home"))
        self.assertRedirects(response, reverse("accounts:login"))

    def test_guide_is_a_three_step_wizard_separate_from_login(self):
        guide = self.client.get(reverse("accounts:guide"))
        self.assertContains(guide, 'data-step="1"')
        self.assertContains(guide, 'data-step="2"')
        self.assertContains(guide, 'data-step="3"')
        self.assertContains(guide, 'data-role-select')
        self.assertContains(guide, 'data-role-steps="farmer"')
        self.assertNotContains(guide, 'name="password"')

        login = self.client.get(reverse("accounts:login"))
        self.assertContains(login, 'name="password"')
        self.assertNotContains(login, "Sebelum masuk, pilih peran Anda")
        self.assertContains(login, "Buka panduan")
        self.assertContains(login, "Daftar sekarang")
        self.assertNotContains(login, "password123")

    def test_authenticated_user_can_open_guide(self):
        user = User.objects.create_user(
            username="pengguna", password="password123", role="consumer"
        )
        self.client.force_login(user)

        guide = self.client.get(reverse("accounts:guide"))
        self.assertEqual(guide.status_code, 200)
        self.assertContains(guide, "Sebelum masuk, pilih peran Anda")
        self.assertContains(guide, "Kembali ke dashboard")

    def test_login_is_always_discoverable_on_public_pages(self):
        for url in (
            reverse("accounts:guide"),
            reverse("accounts:login"),
            reverse("accounts:register"),
        ):
            with self.subTest(url=url):
                response = self.client.get(url)
                # Guide page uses onboarding, auth pages use auth-page
                if url == reverse("accounts:guide"):
                    self.assertContains(response, 'class="onboarding"')
                else:
                    self.assertContains(response, 'class="auth-page"')
                self.assertContains(response, 'href="/accounts/login/"')
                self.assertContains(response, "Foto sawah:")

        guide = self.client.get(reverse("accounts:guide"))
        self.assertContains(guide, "Lewati panduan, langsung masuk")

        login = self.client.get(reverse("accounts:login"))
        self.assertContains(login, 'autocapitalize="none"')
        self.assertContains(login, "Spasi diabaikan")

    def test_login_prefills_username_from_guide(self):
        response = self.client.get(reverse("accounts:login"), {"username": "petani1"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="petani1"')

    def test_authenticated_user_can_open_login_and_switch_account(self):
        call_command("seed_demo_users", verbosity=0)
        self.client.login(username="petani1", password="password123")

        login_page = self.client.get(reverse("accounts:login"))
        self.assertEqual(login_page.status_code, 200)
        self.assertContains(login_page, "Anda sudah masuk sebagai")
        self.assertContains(login_page, "Ganti akun")

        switched = self.client.post(
            reverse("accounts:login"),
            {"username": "admin", "password": "password123"},
        )
        self.assertRedirects(switched, reverse("accounts:dashboard"))
        self.assertContains(
            self.client.get(reverse("accounts:dashboard")),
            "Dashboard Administrator",
        )

    def test_favicon_and_theme_color_are_declared(self):
        response = self.client.get(reverse("accounts:guide"))
        self.assertContains(response, "favicon")
        self.assertContains(response, "apple-touch-icon")
        self.assertContains(response, 'name="theme-color" content="#2f6b3a"')

    def test_actions_show_toast_and_confirmation_modal(self):
        call_command("seed_demo_users", verbosity=0)

        login = self.client.post(
            reverse("accounts:login"),
            {"username": "petani1", "password": "password123"},
            follow=True,
        )
        self.assertContains(login, "Selamat datang")
        self.assertContains(login, 'id="toastContainer"')
        self.assertContains(login, 'class="toast nt-toast')
        self.assertContains(login, 'id="confirmActionModal"')
        self.assertContains(login, 'data-confirm="Keluar dari akun ini?')
        self.assertContains(login, 'data-confirm-title="Keluar dari akun"')

        logout = self.client.post(reverse("accounts:logout"), follow=True)
        self.assertContains(logout, "Anda telah keluar dari akun")
        self.assertContains(logout, 'id="toastContainer"')

    def test_glassmorphism_and_rice_field_background_are_applied(self):
        css = (Path(settings.BASE_DIR) / "static/css/app.css").read_text(
            encoding="utf-8"
        )
        # Background pattern is in background.css
        bg_css = (Path(settings.BASE_DIR) / "static/css/background.css").read_text(
            encoding="utf-8"
        )
        self.assertIn("pattern.svg", bg_css)
        self.assertIn("backdrop-filter", css)
        self.assertIn(".nt-toast", css)
        self.assertIn(".modal-content", css)
        self.assertIn(".glass-card", css)

    def test_critical_forms_ask_for_confirmation(self):
        templates = (
            "accounts/profile.html",
            "accounts/register.html",
            "products/product_form.html",
            "products/inventory_form.html",
            "orders/order_form.html",
            "orders/order_detail.html",
            "orders/status_form.html",
            "orders/payment_form.html",
            "quality_control/inspection_form.html",
            "deliveries/delivery_form.html",
            "deliveries/delivery_detail.html",
            "assets/asset_form.html",
            "assets/asset_detail.html",
            "mentorship/mentorship_form.html",
            "mentorship/activity_form.html",
        )
        for name in templates:
            with self.subTest(template=name):
                content = (
                    Path(settings.BASE_DIR) / "templates" / name
                ).read_text(encoding="utf-8")
                self.assertIn("data-confirm", content)

    def test_authenticated_user_can_update_profile(self):
        user = User.objects.create_user(
            username="petaniuji", password="password123", role="farmer"
        )
        self.client.login(username="petaniuji", password="password123")
        response = self.client.post(
            reverse("accounts:profile"),
            {
                "first_name": "Sari",
                "last_name": "Utami",
                "email": "sari@example.com",
            },
        )
        self.assertRedirects(response, reverse("accounts:profile"))
        user.refresh_from_db()
        self.assertEqual(user.first_name, "Sari")
        self.assertEqual(user.email, "sari@example.com")
