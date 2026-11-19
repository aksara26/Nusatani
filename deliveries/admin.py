from django.contrib import admin

from .models import Delivery


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ("order", "courier_name", "status", "sent_at", "received_at")
    list_filter = ("status",)
    search_fields = ("order__order_number", "courier_name", "tracking_number")
    autocomplete_fields = ("order",)
