from django.urls import path

from . import views

app_name = "assets"

urlpatterns = [
    path("baru/", views.asset_create, name="create"),
    path("<int:pk>/ubah/", views.asset_update, name="update"),
    path("<int:pk>/hapus/", views.asset_delete, name="delete"),
    path("<int:pk>/", views.asset_detail, name="detail"),
    path("", views.asset_list, name="list"),
]
