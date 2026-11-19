"""Alur inti transaksi: buat pesanan, pantau status, dan catat pembayaran simulasi."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from accounts.roles import Role
from accounts.views import role_required
from products.models import Inventory

from .forms import OrderForm, OrderStatusForm, PaymentForm
from .models import Order, OrderItem, OrderType, PaymentRecord


def _order_queryset():
    return Order.objects.select_related("buyer", "farmer", "payment").prefetch_related(
        "items__product"
    )


def _get_order(request, pk):
    order = get_object_or_404(_order_queryset(), pk=pk)
    permitted = (
        request.user.is_superuser
        or request.user.pk in {order.buyer_id, order.farmer_id}
        or request.user.role == Role.QC.value
    )
    if not permitted:
        raise PermissionDenied("Anda tidak memiliki akses ke pesanan ini.")
    return order


def _get_farmer_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.farmer_id != request.user.pk and not request.user.is_superuser:
        raise PermissionDenied("Anda hanya dapat mengelola pesanan yang ditujukan kepada Anda.")
    return order


def _create_order(request, order_type):
    if request.method == "POST":
        form = OrderForm(request.POST, order_type=order_type)
        if form.is_valid():
            product = form.cleaned_data["product"]
            quantity = form.cleaned_data["quantity"]
            inventory = Inventory.objects.filter(product=product).first()
            if order_type == OrderType.SURPLUS.value and (
                not inventory or inventory.quantity < quantity
            ):
                form.add_error("quantity", "Stok tidak mencukupi. Silakan kurangi jumlah.")
            else:
                with transaction.atomic():
                    if order_type == OrderType.SURPLUS.value:
                        inventory.quantity -= quantity
                        inventory.save(update_fields=["quantity"])
                    order = Order.objects.create(
                        buyer=request.user,
                        farmer=product.farmer,
                        order_type=order_type,
                        needed_by=form.cleaned_data["needed_by"],
                        notes=form.cleaned_data["notes"],
                    )
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        unit_price=product.price,
                    )
                    PaymentRecord.objects.create(order=order)
                messages.success(request, "Pesanan berhasil dicatat.")
                return redirect("orders:detail", pk=order.pk)
    else:
        form = OrderForm(order_type=order_type)

    title = "Buat Pre-order" if order_type == OrderType.PREORDER.value else "Pesan Produk Surplus"
    return render(
        request,
        "orders/order_form.html",
        {"form": form, "title": title, "order_type": order_type},
    )


@role_required(Role.HORECA.value)
def preorder_create(request):
    return _create_order(request, OrderType.PREORDER.value)


@role_required(Role.HORECA.value, Role.CONSUMER.value)
def surplus_create(request):
    return _create_order(request, OrderType.SURPLUS.value)


@role_required(Role.HORECA.value, Role.CONSUMER.value)
def my_orders(request):
    orders = _order_queryset()
    if not request.user.is_superuser:
        orders = orders.filter(buyer=request.user)
    return render(request, "orders/my_orders.html", {"orders": orders})


@role_required(Role.FARMER.value)
def incoming_orders(request):
    orders = _order_queryset()
    if not request.user.is_superuser:
        orders = orders.filter(farmer=request.user)
    return render(request, "orders/incoming_orders.html", {"orders": orders})


@login_required
def order_detail(request, pk):
    order = _get_order(request, pk)
    is_farmer = order.farmer_id == request.user.pk or request.user.is_superuser
    return render(
        request,
        "orders/order_detail.html",
        {
            "order": order,
            "is_farmer": is_farmer,
            "status_form": OrderStatusForm(order=order, is_admin=request.user.is_superuser),
        },
    )


@role_required(Role.FARMER.value)
def update_status(request, pk):
    order = _get_farmer_order(request, pk)
    if request.method == "POST":
        form = OrderStatusForm(
            request.POST, order=order, is_admin=request.user.is_superuser
        )
        if form.is_valid():
            new_status = form.cleaned_data["status"]
            try:
                order.transition_to(new_status)
            except ValueError as exc:
                form.add_error("status", str(exc))
            else:
                messages.success(request, "Status pesanan diperbarui.")
                return redirect("orders:detail", pk=order.pk)
    else:
        form = OrderStatusForm(order=order, is_admin=request.user.is_superuser)
    return render(
        request,
        "orders/status_form.html",
        {"form": form, "order": order, "status_label": order.get_status_display()},
    )


@role_required(Role.FARMER.value)
def update_payment(request, pk):
    order = _get_farmer_order(request, pk)
    payment, _created = PaymentRecord.objects.get_or_create(order=order)
    if request.method == "POST":
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            form.save()
            messages.success(request, "Catatan pembayaran simulasi diperbarui.")
            return redirect("orders:detail", pk=order.pk)
    else:
        form = PaymentForm(instance=payment)
    return render(
        request,
        "orders/payment_form.html",
        {"form": form, "order": order},
    )
