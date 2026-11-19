from django.urls import path

from . import views

app_name = "deliveries"

urlpatterns = [
    path("siapkan/<int:pk>/", views.prepare, name="prepare"),
    path("<int:pk>/status/", views.update_status, name="update_status"),
    path("<int:pk>/", views.detail, name="detail"),
    path("", views.delivery_list, name="list"),
]
