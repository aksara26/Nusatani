from django.urls import path

from . import views

app_name = "bankku"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("performaku/", views.my_performance, name="my_performance"),
]
