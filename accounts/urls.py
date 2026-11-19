from django.urls import path

from .views import (
    NusaTaniLoginView,
    NusaTaniLogoutView,
    dashboard,
    guide,
    profile,
)

app_name = "accounts"

urlpatterns = [
    path("panduan/", guide, name="guide"),
    path("login/", NusaTaniLoginView.as_view(), name="login"),
    path("logout/", NusaTaniLogoutView.as_view(), name="logout"),
    path("profil/", profile, name="profile"),
    path("dashboard/", dashboard, name="dashboard"),
]
