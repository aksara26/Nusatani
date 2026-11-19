"""Penyiapan dan pembaruan status pengiriman simulasi."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.roles import Role
from accounts.views import role_required
from orders.models import Order, OrderStatus

from .forms import DeliveryForm
from .models import Delivery, DeliveryStatus


def _owned_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.farmer_id != request.user.pk and not request.user.is_superuser:
        raise PermissionDenied("Anda hanya dapat mengelola pengiriman pesanan Anda sendiri.")
    return order


@role_required(Role.FARMER.value)
def prepare(request, pk):
    """Siapkan pengiriman hanya jika pesanan sudah lolos QC."""
    order = _owned_order(request, pk)
    if order.status != OrderStatus.QC_LOLOS.value or not order.qc_ready:
        messages.error(request, "Produk belum lolos QC sehingga belum boleh disiapkan untuk dikirim.")
        return redirect("orders:detail", pk=order.pk)

    if request.method == "POST":
        form = DeliveryForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                order.transition_to(OrderStatus.SIAP_DIKIRIM.value)
                delivery = form.save(commit=False)
                delivery.order = order
                delivery.save()
            messages.success(request, "Pengiriman disiapkan. Pesanan siap diserahkan ke kurir.")
            return redirect("deliveries:detail", pk=delivery.pk)
    else:
        form = DeliveryForm()
    return render(
        request,
        "deliveries/delivery_form.html",
        {"form": form, "order": order},
    )


@login_required
def detail(request, pk):
    delivery = get_object_or_404(
        Delivery.objects.select_related("order__buyer", "order__farmer"), pk=pk
    )
    order = delivery.order
    permitted = (
        request.user.is_superuser
        or request.user.pk in {order.buyer_id, order.farmer_id}
        or request.user.role == Role.QC.value
    )
    if not permitted:
        raise PermissionDenied("Anda tidak memiliki akses ke pengiriman ini.")
    return render(
        request,
        "deliveries/delivery_detail.html",
        {
            "delivery": delivery,
            "order": order,
            "is_farmer": order.farmer_id == request.user.pk or request.user.is_superuser,
        },
    )


@role_required(Role.FARMER.value)
def update_status(request, pk):
    delivery = get_object_or_404(Delivery.objects.select_related("order"), pk=pk)
    _owned_order(request, delivery.order_id)
    order = delivery.order
    action = request.POST.get("action")

    with transaction.atomic():
        if (
            action == "dikirim"
            and delivery.status == DeliveryStatus.DISIAPKAN.value
            and order.status == OrderStatus.SIAP_DIKIRIM.value
        ):
            delivery.status = DeliveryStatus.DIKIRIM.value
            delivery.sent_at = timezone.now()
            delivery.save(update_fields=["status", "sent_at", "updated_at"])
            order.transition_to(OrderStatus.DALAM_PENGIRIMAN.value)
            messages.success(request, "Pesanan ditandai sedang dikirim.")
        elif (
            action == "diterima"
            and delivery.status == DeliveryStatus.DIKIRIM.value
            and order.status == OrderStatus.DALAM_PENGIRIMAN.value
        ):
            delivery.status = DeliveryStatus.DITERIMA.value
            delivery.received_at = timezone.now()
            delivery.save(update_fields=["status", "received_at", "updated_at"])
            order.transition_to(OrderStatus.SELESAI.value)
            messages.success(request, "Pesanan ditandai selesai diterima.")
        else:
            messages.error(request, "Perubahan status pengiriman tidak valid.")

    return redirect("deliveries:detail", pk=delivery.pk)


@role_required(Role.FARMER.value, Role.HORECA.value, Role.CONSUMER.value)
def delivery_list(request):
    deliveries = Delivery.objects.select_related("order__buyer", "order__farmer")
    if request.user.role == Role.FARMER.value and not request.user.is_superuser:
        deliveries = deliveries.filter(order__farmer=request.user)
    elif not request.user.is_superuser:
        deliveries = deliveries.filter(order__buyer=request.user)
    return render(request, "deliveries/delivery_list.html", {"deliveries": deliveries})
