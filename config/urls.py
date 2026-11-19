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
    path("orders/", include("orders.urls")),
    path("qc/", include("quality_control.urls")),
    path("deliveries/", include("deliveries.urls")),
    path("assets/", include("assets.urls")),
    path("mentorship/", include("mentorship.urls")),
]
