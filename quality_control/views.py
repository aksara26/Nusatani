"""Antrean pemeriksaan QC dan pengajuan produk oleh petani."""

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.roles import Role
from accounts.views import role_required
from orders.models import Order, OrderStatus, QcResult

from .forms import InspectionForm
from .models import QcStatus, QualityInspection


def _apply_inspection_result(inspection):
    """Sinkronkan hasil QC ke item dan status pesanan."""
    item = inspection.order_item
    order = item.order

    if inspection.result == QcStatus.LOLOS.value:
        item.qc_result = QcResult.LOLOS.value
        item.save(update_fields=["qc_result"])
        if order.status == OrderStatus.MENUNGGU_QC.value and all(
            related.qc_result == QcResult.LOLOS.value for related in order.items.all()
        ):
            order.transition_to(OrderStatus.QC_LOLOS.value)
    elif inspection.result == QcStatus.DITOLAK.value:
        item.qc_result = QcResult.DITOLAK.value
        item.save(update_fields=["qc_result"])
        if order.can_transition_to(OrderStatus.QC_DITOLAK.value):
            order.transition_to(OrderStatus.QC_DITOLAK.value)


@role_required(Role.QC.value)
def queue(request):
    inspections = QualityInspection.objects.select_related(
        "order_item__product", "order_item__order", "order_item__order__farmer", "inspector"
    ).filter(result__in=[QcStatus.MENUNGGU.value, QcStatus.DIPERIKSA.value])
    return render(
        request,
        "quality_control/queue.html",
        {"inspections": inspections},
    )


@role_required(Role.QC.value)
def inspect(request, pk):
    inspection = get_object_or_404(
        QualityInspection.objects.select_related("order_item__product", "order_item__order"),
        pk=pk,
    )
    order = inspection.order_item.order
    if request.method == "POST":
        form = InspectionForm(request.POST, instance=inspection)
        if form.is_valid():
            inspection = form.save(commit=False)
            inspection.inspector = request.user
            if inspection.result in {QcStatus.LOLOS.value, QcStatus.DITOLAK.value}:
                inspection.inspected_at = timezone.now()
            inspection.save()
            _apply_inspection_result(inspection)
            messages.success(request, "Hasil pemeriksaan QC tersimpan.")
            return redirect("quality_control:queue")
    else:
        form = InspectionForm(instance=inspection)
    return render(
        request,
        "quality_control/inspection_form.html",
        {"form": form, "inspection": inspection, "order": order},
    )


@role_required(Role.FARMER.value)
def submit_to_qc(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.farmer_id != request.user.pk and not request.user.is_superuser:
        raise PermissionDenied("Anda hanya dapat mengajukan pesanan Anda sendiri.")
    if request.method != "POST":
        raise PermissionDenied("Gunakan tombol Ajukan ke QC.")

    if order.status != OrderStatus.DALAM_PRODUKSI.value:
        messages.error(request, "Pesanan harus berada pada status Dalam Produksi.")
    else:
        order.transition_to(OrderStatus.MENUNGGU_QC.value)
        for item in order.items.all():
            QualityInspection.objects.get_or_create(
                order_item=item,
                defaults={"notes": "Menunggu pemeriksaan petugas QC."},
            )
        messages.success(request, "Produk berhasil diajukan ke pemeriksaan kualitas.")
    return redirect("orders:detail", pk=order.pk)
