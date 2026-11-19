from django.contrib import admin

from .models import Order, OrderItem, PaymentRecord


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "buyer", "farmer", "order_type", "status", "total", "created_at")
    list_filter = ("status", "order_type")
    search_fields = ("order_number", "buyer__username", "farmer__username")
    autocomplete_fields = ("buyer", "farmer")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "unit_price", "qc_result")
    list_filter = ("qc_result",)
    search_fields = ("order__order_number", "product__name")


@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = ("order", "status", "paid_amount", "updated_at")
    list_filter = ("status",)
    search_fields = ("order__order_number",)
