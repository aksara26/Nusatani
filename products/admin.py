from django.contrib import admin

from .models import Inventory, Product, Variety


@admin.register(Variety)
class VarietyAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "farmer", "variety", "price", "is_surplus", "is_active")
    list_filter = ("is_surplus", "is_active", "variety")
    search_fields = ("name", "farmer__username")
    autocomplete_fields = ("farmer", "variety")


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ("product", "quantity", "updated_at")
    search_fields = ("product__name",)
