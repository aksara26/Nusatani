from django.urls import path

from .views import (
    NusaTaniLoginView,
    NusaTaniLogoutView,
    dashboard,
    demo_login,
    guide,
    profile,
    register,
)

app_name = "accounts"

urlpatterns = [
    path("panduan/", guide, name="guide"),
    path("daftar/", register, name="register"),
    path("login/", NusaTaniLoginView.as_view(), name="login"),
    path("demo/", demo_login, name="demo_login"),
    path("logout/", NusaTaniLogoutView.as_view(), name="logout"),
    path("profil/", profile, name="profile"),
    path("dashboard/", dashboard, name="dashboard"),
]
