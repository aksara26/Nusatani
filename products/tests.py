"""Pengujian alur Tahap 3, termasuk Skenario 4."""

from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Product, Variety

User = get_user_model()


class CatalogAndStockTests(TestCase):
    def setUp(self):
        self.farmer = User.objects.create_user(
            username="petaniuji", password="TestPass123!", role="farmer"
        )
        self.other_farmer = User.objects.create_user(
            username="petaniuji2", password="TestPass123!", role="farmer"
        )
        self.buyer = User.objects.create_user(
            username="pembeliuji", password="TestPass123!", role="consumer"
        )
        self.variety, _created = Variety.objects.get_or_create(
            slug="sawi-putih", defaults={"name": "Sawi Putih"}
        )
        self.client.login(username="petaniuji", password="TestPass123!")

    def payload(self, **overrides):
        data = {
            "variety": self.variety.pk,
            "name": "Micro Sawi Segar",
            "description": "Panen hari ini",
            "price": "25000",
            "photo_url": "",
            "is_surplus": "",
            "available_from": date.today().isoformat(),
            "is_active": "on",
            "initial_stock": "12",
        }
        data.update(overrides)
        return data

    def test_farmer_adds_product_and_it_appears_in_catalog(self):
        """Skenario 4: petani menambah produk, pembeli melihatnya di katalog."""
        response = self.client.post(reverse("products:create"), self.payload())
        self.assertEqual(response.status_code, 302)

        product = Product.objects.get(name="Micro Sawi Segar")
        self.assertEqual(product.farmer, self.farmer)
        self.assertEqual(product.stock, 12)
        self.assertEqual(product.availability_status, "Tersedia")

        self.client.logout()
        self.client.login(username="pembeliuji", password="TestPass123!")
        catalog = self.client.get(reverse("products:catalog"))
        self.assertEqual(catalog.status_code, 200)
        self.assertContains(catalog, "Micro Sawi Segar")

    def test_surplus_marketplace_filter(self):
        self.client.post(reverse("products:create"), self.payload(is_surplus="on"))
        catalog = self.client.get(reverse("products:catalog"))
        surplus = self.client.get(reverse("products:surplus"))
        self.assertContains(catalog, "Micro Sawi Segar")
        self.assertContains(surplus, "Micro Sawi Segar")
        self.assertTrue(surplus.context["surplus_only"])
        self.assertEqual(len(surplus.context["products"]), 1)

    def test_consumer_cannot_add_product(self):
        self.client.logout()
        self.client.login(username="pembeliuji", password="TestPass123!")
        response = self.client.post(reverse("products:create"), self.payload())
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Product.objects.exists())

    def test_farmer_cannot_edit_other_farmers_product(self):
        product = Product.objects.create(
            farmer=self.other_farmer,
            variety=self.variety,
            name="Produk Petani Lain",
            price="15000",
        )
        response = self.client.get(reverse("products:update", args=[product.pk]))
        self.assertEqual(response.status_code, 403)

    def test_inventory_update_changes_stock_and_status(self):
        self.client.post(reverse("products:create"), self.payload(initial_stock="0"))
        product = Product.objects.get(name="Micro Sawi Segar")
        self.assertEqual(product.availability_status, "Stok habis")

        response = self.client.post(
            reverse("products:inventory_update", args=[product.pk]), {"quantity": 7}
        )
        self.assertEqual(response.status_code, 302)

        updated = Product.objects.get(pk=product.pk)
        self.assertEqual(updated.stock, 7)
        self.assertEqual(updated.availability_status, "Tersedia")

    def test_anonymous_user_is_redirected_to_login(self):
        self.client.logout()
        response = self.client.get(reverse("products:catalog"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)
