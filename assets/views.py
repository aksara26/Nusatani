"""Asetku: daftar, tambah, ubah, dan hapus aset milik petani."""

from decimal import Decimal

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render

from accounts.roles import Role
from accounts.views import role_required

from .forms import AssetForm
from .models import Asset


def _owned_asset(request, pk):
    asset = get_object_or_404(Asset.objects.select_related("owner"), pk=pk)
    if asset.owner_id != request.user.pk and not request.user.is_superuser:
        raise PermissionDenied("Anda hanya dapat mengelola aset milik sendiri.")
    return asset


@role_required(Role.FARMER.value)
def asset_list(request):
    assets = Asset.objects.select_related("owner")
    if not request.user.is_superuser:
        assets = assets.filter(owner=request.user)
    assets = list(assets)

    starter_count = sum(1 for asset in assets if asset.is_starter_kit)
    ijarah_total = sum(
        (asset.ijarah_total or Decimal("0") for asset in assets),
        Decimal("0"),
    )
    return render(
        request,
        "assets/asset_list.html",
        {
            "assets": assets,
            "starter_count": starter_count,
            "ijarah_total": ijarah_total,
            "ijarah_count": sum(1 for asset in assets if asset.is_ijarah),
        },
    )


@role_required(Role.FARMER.value)
def asset_create(request):
    if request.method == "POST":
        form = AssetForm(request.POST)
        if form.is_valid():
            asset = form.save(commit=False)
            asset.owner = request.user
            asset.save()
            messages.success(request, "Aset berhasil dicatat.")
            return redirect("assets:detail", pk=asset.pk)
    else:
        form = AssetForm()
    return render(
        request,
        "assets/asset_form.html",
        {"form": form, "title": "Tambah aset", "asset": None},
    )


@role_required(Role.FARMER.value)
def asset_detail(request, pk):
    return render(request, "assets/asset_detail.html", {"asset": _owned_asset(request, pk)})


@role_required(Role.FARMER.value)
def asset_update(request, pk):
    asset = _owned_asset(request, pk)
    if request.method == "POST":
        form = AssetForm(request.POST, instance=asset)
        if form.is_valid():
            form.save()
            messages.success(request, "Data aset berhasil diperbarui.")
            return redirect("assets:detail", pk=asset.pk)
    else:
        form = AssetForm(instance=asset)
    return render(
        request,
        "assets/asset_form.html",
        {"form": form, "title": "Ubah aset", "asset": asset},
    )


@role_required(Role.FARMER.value)
def asset_delete(request, pk):
    asset = _owned_asset(request, pk)
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    asset.delete()
    messages.success(request, "Aset berhasil dihapus dari catatan.")
    return redirect("assets:list")
