"""Dashboard BANKKU dan ringkasan performa untuk petani."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.shortcuts import render

from accounts.roles import Role
from accounts.views import role_required
from orders.models import Order

from .models import FarmerPerformance, FinancingAssessment

User = get_user_model()


def _build_rows(farmers):
    """Hitung ulang performa dan indikator agar dashboard selalu mutakhir."""
    rows = []
    for farmer in farmers:
        performance, _ = FarmerPerformance.objects.get_or_create(farmer=farmer)
        performance.recalculate()
        assessment, _ = FinancingAssessment.objects.get_or_create(performance=performance)
        assessment.recalculate()
        rows.append(
            {
                "farmer": farmer,
                "performance": performance,
                "assessment": assessment,
            }
        )
    return rows


@role_required(Role.BANK.value)
def dashboard(request):
    farmers = User.objects.filter(role=Role.FARMER.value).order_by("username")
    rows = _build_rows(farmers)

    selected_id = request.GET.get("petani")
    selected_row = next(
        (row for row in rows if str(row["farmer"].pk) == selected_id),
        rows[0] if rows else None,
    )
    orders = []
    if selected_row:
        orders = (
            Order.objects.filter(farmer=selected_row["farmer"])
            .select_related("buyer")
            .prefetch_related("items")
        )

    return render(
        request,
        "bankku/dashboard.html",
        {
            "rows": rows,
            "selected_row": selected_row,
            "orders": orders,
            "farmers": farmers,
            "farmer_count": len(rows),
            "total_orders": sum(row["performance"].total_orders for row in rows),
            "total_value": sum(
                (row["performance"].total_order_value for row in rows), Decimal("0")
            ),
        },
    )


@role_required(Role.FARMER.value)
def my_performance(request):
    performance, _ = FarmerPerformance.objects.get_or_create(farmer=request.user)
    performance.recalculate()
    assessment, _ = FinancingAssessment.objects.get_or_create(performance=performance)
    assessment.recalculate()
    orders = (
        Order.objects.filter(farmer=request.user)
        .select_related("buyer")
        .prefetch_related("items")
    )
    return render(
        request,
        "bankku/my_performance.html",
        {
            "performance": performance,
            "assessment": assessment,
            "orders": orders,
        },
    )
