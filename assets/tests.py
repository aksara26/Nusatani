"""Pengujian pencatatan aset, starter kit, dan simulasi ijarah."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Asset, FinancingScheme

User = get_user_model()


class AssetTests(TestCase):
    def setUp(self):
        self.farmer = User.objects.create_user(
            username="petaniuji", password="password123", role="farmer"
        )
        self.other_farmer = User.objects.create_user(
            username="petaniuji2", password="password123", role="farmer"
        )
        self.admin = User.objects.create_superuser(
            username="adminuji", password="password123", role="admin"
        )

    def asset_payload(self, **overrides):
        payload = {
            "name": "Rak budidaya",
            "category": "rak",
            "quantity": "2",
            "unit": "unit",
            "condition": "baik",
            "acquisition_date": "2026-01-10",
            "financing_scheme": FinancingScheme.MILIK_SENDIRI.value,
            "ijarah_duration_months": "",
            "ijarah_monthly_payment": "",
            "notes": "Rak utama.",
        }
        payload.update(overrides)
        return payload

    def test_farmer_can_record_starter_kit_asset(self):
        self.client.login(username="petaniuji", password="password123")
        response = self.client.post(
            reverse("assets:create"),
            self.asset_payload(
                name="Tray starter",
                category="tray",
                quantity="10",
                financing_scheme=FinancingScheme.STARTER_KIT.value,
            ),
        )
        self.assertEqual(response.status_code, 302)
        asset = Asset.objects.get(name="Tray starter")
        self.assertEqual(asset.owner, self.farmer)
        self.assertTrue(asset.is_starter_kit)
        self.assertIsNone(asset.ijarah_total)

    def test_ijarah_requires_duration_and_monthly_payment(self):
        self.client.login(username="petaniuji", password="password123")
        response = self.client.post(
            reverse("assets:create"),
            self.asset_payload(financing_scheme=FinancingScheme.IJARAH.value),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tenor wajib diisi untuk skema ijarah.")
        self.assertContains(response, "Cicilan bulanan wajib diisi untuk skema ijarah.")
        self.assertFalse(Asset.objects.exists())

    def test_ijarah_total_is_calculated(self):
        self.client.login(username="petaniuji", password="password123")
        response = self.client.post(
            reverse("assets:create"),
            self.asset_payload(
                name="Lampu ijarah",
                financing_scheme=FinancingScheme.IJARAH.value,
                ijarah_duration_months="12",
                ijarah_monthly_payment="150000",
            ),
        )
        self.assertEqual(response.status_code, 302)
        asset = Asset.objects.get(name="Lampu ijarah")
        self.assertTrue(asset.is_ijarah)
        self.assertEqual(asset.ijarah_total, Decimal("1800000"))

        listing = self.client.get(reverse("assets:list"))
        self.assertContains(listing, "Rp 1.800.000")

    def test_non_ijarah_asset_discards_ijarah_fields(self):
        self.client.login(username="petaniuji", password="password123")
        self.client.post(
            reverse("assets:create"),
            self.asset_payload(
                ijarah_duration_months="6",
                ijarah_monthly_payment="100000",
            ),
        )
        asset = Asset.objects.get(name="Rak budidaya")
        self.assertIsNone(asset.ijarah_duration_months)
        self.assertIsNone(asset.ijarah_monthly_payment)

    def test_list_only_shows_own_assets(self):
        Asset.objects.create(name="Aset petani", owner=self.farmer)
        Asset.objects.create(name="Aset petani lain", owner=self.other_farmer)

        self.client.login(username="petaniuji", password="password123")
        response = self.client.get(reverse("assets:list"))
        self.assertContains(response, "Aset petani")
        self.assertNotContains(response, "Aset petani lain")

        self.client.logout()
        self.client.login(username="adminuji", password="password123")
        response = self.client.get(reverse("assets:list"))
        self.assertContains(response, "Aset petani lain")

    def test_other_farmer_cannot_update_or_delete_asset(self):
        asset = Asset.objects.create(name="Aset petani", owner=self.farmer)
        self.client.login(username="petaniuji2", password="password123")

        update = self.client.get(reverse("assets:update", args=[asset.pk]))
        self.assertEqual(update.status_code, 403)
        deletion = self.client.post(reverse("assets:delete", args=[asset.pk]))
        self.assertEqual(deletion.status_code, 403)
        self.assertTrue(Asset.objects.filter(pk=asset.pk).exists())

    def test_farmer_can_update_own_asset(self):
        asset = Asset.objects.create(name="Rak lama", owner=self.farmer)
        self.client.login(username="petaniuji", password="password123")
        response = self.client.post(
            reverse("assets:update", args=[asset.pk]),
            self.asset_payload(name="Rak baru", condition="cukup"),
        )
        self.assertEqual(response.status_code, 302)
        asset.refresh_from_db()
        self.assertEqual(asset.name, "Rak baru")
        self.assertEqual(asset.condition, "cukup")
