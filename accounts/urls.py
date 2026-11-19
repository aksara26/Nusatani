from django.urls import path

from .views import NusaTaniLoginView, NusaTaniLogoutView, dashboard

app_name = "accounts"

urlpatterns = [
    path("login/", NusaTaniLoginView.as_view(), name="login"),
    path("logout/", NusaTaniLogoutView.as_view(), name="logout"),
    path("dashboard/", dashboard, name="dashboard"),
]
