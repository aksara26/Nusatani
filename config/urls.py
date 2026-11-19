"""Routing utama NusaTani."""

from django.contrib import admin
from django.urls import include, path

from accounts.views import home
from config.health import health

urlpatterns = [
    path("", home, name="home"),
    path("health/", health, name="health"),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("products/", include("products.urls")),
]
