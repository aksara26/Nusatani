from django.contrib import admin

from .models import QualityInspection


@admin.register(QualityInspection)
class QualityInspectionAdmin(admin.ModelAdmin):
    list_display = (
        "order_item",
        "inspector",
        "result",
        "visual_ok",
        "cleanliness_ok",
        "freshness_ok",
        "weight_ok",
        "inspected_at",
    )
    list_filter = ("result", "visual_ok", "cleanliness_ok", "freshness_ok", "weight_ok")
    search_fields = ("order_item__order__order_number", "order_item__product__name")
    autocomplete_fields = ("inspector", "order_item")
