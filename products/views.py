"""Katalog produk, marketplace surplus, dan pengelolaan stok petani."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from accounts.roles import Role
from accounts.views import role_required

from .forms import InventoryForm, ProductForm
from .models import Inventory, Product


def _owned_product(request, pk):
    """Ambil produk yang hanya boleh diubah oleh petani pemiliknya."""
    product = get_object_or_404(Product, pk=pk)
    if product.farmer_id != request.user.pk and not request.user.is_superuser:
        raise PermissionDenied("Anda hanya dapat mengelola produk sendiri.")
    return product


@login_required
def catalog(request, surplus_only=False):
    """Daftar produk aktif; `surplus_only` menampilkan marketplace surplus."""
    products = Product.objects.select_related("variety", "farmer", "inventory").filter(
        is_active=True
    )
    if surplus_only:
        products = products.filter(is_surplus=True)
    return render(
        request,
        "products/catalog.html",
        {
            "products": products.order_by("name"),
            "surplus_only": surplus_only,
        },
    )


@login_required
def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.select_related("variety", "farmer", "inventory"), pk=pk
    )
    if not product.is_active and product.farmer_id != request.user.pk and not request.user.is_superuser:
        raise PermissionDenied("Produk ini tidak tersedia.")
    return render(
        request,
        "products/product_detail.html",
        {"product": product, "can_manage": product.farmer_id == request.user.pk},
    )


@role_required(Role.FARMER.value)
def my_products(request):
    """Daftar produk milik petani yang sedang login (semua produk untuk admin)."""
    products = Product.objects.select_related("variety", "inventory")
    if not request.user.is_superuser:
        products = products.filter(farmer=request.user)
    return render(
        request,
        "products/my_products.html",
        {"products": products.order_by("-created_at")},
    )


@role_required(Role.FARMER.value)
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.farmer = request.user
            product.save()
            Inventory.objects.update_or_create(
                product=product,
                defaults={"quantity": form.cleaned_data["initial_stock"]},
            )
            messages.success(request, "Produk berhasil ditambahkan dan muncul di katalog.")
            return redirect("products:detail", pk=product.pk)
    else:
        form = ProductForm()
    return render(
        request,
        "products/product_form.html",
        {"form": form, "title": "Tambah produk", "product": None},
    )


@role_required(Role.FARMER.value)
def product_update(request, pk):
    product = _owned_product(request, pk)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Produk berhasil diperbarui.")
            return redirect("products:detail", pk=product.pk)
    else:
        form = ProductForm(instance=product)
    return render(
        request,
        "products/product_form.html",
        {"form": form, "title": "Ubah produk", "product": product},
    )


@role_required(Role.FARMER.value)
def inventory_update(request, pk):
    product = _owned_product(request, pk)
    inventory, _created = Inventory.objects.get_or_create(product=product)
    if request.method == "POST":
        form = InventoryForm(request.POST, instance=inventory)
        if form.is_valid():
            form.save()
            messages.success(request, "Stok produk berhasil diperbarui.")
            return redirect("products:detail", pk=product.pk)
    else:
        form = InventoryForm(instance=inventory)
    return render(
        request,
        "products/inventory_form.html",
        {"form": form, "product": product},
    )
