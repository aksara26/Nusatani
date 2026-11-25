"""Verifikasi navbar fitur per peran muncul dan menandai halaman aktif."""

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

User = get_user_model()

ROLE_NAV_CASES = {
    "petani1": ("Fitur Petani", "products:my_products", "Produk Saya"),
    "horeca1": ("Fitur HOREKA", "orders:my_orders", "Pesanan Saya"),
    "konsumen1": ("Fitur Konsumen", "orders:my_orders", "Pesanan Saya"),
    "qc1": ("Fitur Quality Control", "quality_control:queue", "Antrean QC"),
    "mentor1": ("Fitur Mentor", "mentorship:list", "Mentorku"),
    "bank1": ("Fitur BANKKU", "bankku:dashboard", "BANKKU"),
    "admin": ("Fitur Administrator", "accounts:dashboard", "Dashboard"),
}


class RoleNavigationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo_users", verbosity=0)

    def test_role_nav_lists_features_and_marks_current_page(self):
        for username, (label, route, active_label) in ROLE_NAV_CASES.items():
            with self.subTest(username=username):
                self.client.force_login(User.objects.get(username=username))
                response = self.client.get(reverse(route))

                self.assertEqual(response.status_code, 200)
                nav = response.context["role_nav"]
                self.assertEqual(nav["label"], label)
                self.assertTrue(nav["items"])
                self.assertIn(
                    active_label,
                    [item["label"] for item in nav["items"] if item["active"]],
                )
                self.assertContains(response, label)

    def test_nav_is_hidden_for_anonymous_visitors(self):
        response = self.client.get(reverse("accounts:guide"))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["role_nav"])
        self.assertNotContains(response, 'class="role-nav"')
