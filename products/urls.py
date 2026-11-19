from django.urls import path

from . import views

app_name = "products"

urlpatterns = [
    path("", views.catalog, name="catalog"),
    path("surplus/", views.catalog, {"surplus_only": True}, name="surplus"),
    path("saya/", views.my_products, name="my_products"),
    path("tambah/", views.product_create, name="create"),
    path("<int:pk>/", views.product_detail, name="detail"),
    path("<int:pk>/ubah/", views.product_update, name="update"),
    path("<int:pk>/stok/", views.inventory_update, name="inventory_update"),
]
