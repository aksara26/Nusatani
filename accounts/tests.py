"""Verifikasi alur login dan dashboard untuk seluruh akun demo NusaTani."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .roles import ROLE_DASHBOARDS

User = get_user_model()

DEMO_ACCOUNTS = [
    ("admin", "admin", True),
    ("petani1", "farmer", False),
    ("horeca1", "horeca", False),
    ("konsumen1", "consumer", False),
    ("qc1", "qc", False),
    ("mentor1", "mentor", False),
]


class DemoLoginTests(TestCase):
    def test_all_demo_accounts_can_login_and_open_own_dashboard(self):
        for username, role, is_admin in DEMO_ACCOUNTS:
            with self.subTest(username=username):
                user, _ = User.objects.update_or_create(
                    username=username,
                    defaults={
                        "email": f"{username}@example.com",
                        "role": role,
                        "is_staff": is_admin,
                        "is_superuser": is_admin,
                        "is_active": True,
                    },
                )
                user.set_password("password123")
                user.save()

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

    def test_wrong_password_is_rejected(self):
        User.objects.create_user(username="petani1", password="password123", role="farmer")
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "petani1", "password": "salah"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "sandi yang benar")
