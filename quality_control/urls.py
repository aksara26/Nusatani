from django.urls import path

from . import views

app_name = "quality_control"

urlpatterns = [
    path("<int:pk>/periksa/", views.inspect, name="inspect"),
    path("pesanan/<int:pk>/ajukan/", views.submit_to_qc, name="submit_to_qc"),
    path("", views.queue, name="queue"),
]
