from django.contrib import admin

from .models import Asset


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "owner",
        "category",
        "quantity",
        "unit",
        "condition",
        "financing_scheme",
    )
    list_filter = ("category", "condition", "financing_scheme")
    search_fields = ("name", "owner__username", "notes")
    autocomplete_fields = ("owner",)
    readonly_fields = ("created_at", "updated_at")
