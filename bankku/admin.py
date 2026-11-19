from django.contrib import admin

from .models import FarmerPerformance, FinancingAssessment


@admin.register(FarmerPerformance)
class FarmerPerformanceAdmin(admin.ModelAdmin):
    list_display = (
        "farmer",
        "total_orders",
        "completed_orders",
        "total_order_value",
        "fulfillment_rate",
        "quality_pass_rate",
        "asset_count",
        "last_calculated_at",
    )
    search_fields = ("farmer__username",)
    autocomplete_fields = ("farmer",)
    readonly_fields = ("last_calculated_at", "updated_at")


@admin.register(FinancingAssessment)
class FinancingAssessmentAdmin(admin.ModelAdmin):
    list_display = ("performance", "total_score", "eligibility", "calculated_at")
    list_filter = ("eligibility",)
    search_fields = ("performance__farmer__username",)
    autocomplete_fields = ("performance",)
    readonly_fields = ("calculated_at",)
