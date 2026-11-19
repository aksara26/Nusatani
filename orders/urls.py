from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("preorder/", views.preorder_create, name="preorder_create"),
    path("surplus/", views.surplus_create, name="surplus_create"),
    path("saya/", views.my_orders, name="my_orders"),
    path("masuk/", views.incoming_orders, name="incoming"),
    path("<int:pk>/", views.order_detail, name="detail"),
    path("<int:pk>/status/", views.update_status, name="update_status"),
    path("<int:pk>/pembayaran/", views.update_payment, name="update_payment"),
]
