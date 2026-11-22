"""Autentikasi, panduan awal, profil, pengalihan, dan dashboard per peran."""

from datetime import timedelta
from decimal import Decimal
from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import PermissionDenied
from django.db.models import Avg, Count
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from .forms import NusaTaniAuthenticationForm, ProfileForm, RegistrationForm
from .roles import (
    DEMO_ROLE_ACCOUNTS,
    ROLE_DASHBOARDS,
    ROLE_GUIDES,
    SELF_REGISTER_ROLES,
    Role,
)


class NusaTaniLoginView(LoginView):
    """Halaman masuk yang juga bisa dipakai untuk berganti akun.

    Sengaja tidak memakai redirect_authenticated_user agar pengguna yang sudah
    masuk tetap bisa membuka formulir dan berpindah peran tanpa logout dulu.
    """

    template_name = "registration/login.html"
    authentication_form = NusaTaniAuthenticationForm

    def get_initial(self):
        initial = super().get_initial()
        suggested = self.request.GET.get("username", "").strip()
        if suggested:
            initial["username"] = suggested[:150]
        return initial

    def get_success_url(self):
        """Arahkan ke tujuan `next` yang valid, jika tidak ke dashboard."""
        return self.get_redirect_url() or reverse("accounts:dashboard")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        requested_role = (
            self.request.POST.get("role")
            or self.request.GET.get("role")
            or ""
        ).strip()
        username = (
            self.request.POST.get("username")
            or self.request.GET.get("username")
            or ""
        ).strip()

        if requested_role not in DEMO_ROLE_ACCOUNTS:
            requested_role = next(
                (
                    config["role"]
                    for config in DEMO_ROLE_ACCOUNTS.values()
                    if config["username"].lower() == username.lower()
                ),
                Role.FARMER.value,
            )

        all_demo_roles = [c for c in DEMO_ROLE_ACCOUNTS.values() if c["role"] != Role.ADMIN.value]
        context["demo_roles"] = all_demo_roles
        context["selected_role"] = requested_role
        if requested_role in DEMO_ROLE_ACCOUNTS and requested_role != Role.ADMIN.value:
            context["selected_role_config"] = DEMO_ROLE_ACCOUNTS[requested_role]
        elif all_demo_roles:
            context["selected_role_config"] = all_demo_roles[0]
        else:
            context["selected_role_config"] = None
        context["demo_login_enabled"] = getattr(settings, "DEMO_LOGIN_ENABLED", True)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user
        name = user.get_full_name() or user.get_username()
        messages.success(
            self.request,
            f"Selamat datang, {name}. Anda masuk sebagai {user.get_role_display()}.",
        )
        return response


class NusaTaniLogoutView(LogoutView):
    next_page = reverse_lazy("accounts:login")

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        messages.success(
            request, "Anda telah keluar dari akun. Sampai jumpa kembali."
        )
        return response


@never_cache
@require_http_methods(["GET", "POST"])
def demo_login(request):
    """Masuk cepat sebagai akun demo yang dipilih dari halaman login.

    Endpoint ini sengaja hanya menerima enam role demo publik. Administrator
    tidak termasuk agar tidak bisa diakses lewat tombol demo.
    """
    from django.contrib.auth import get_user_model, login

    role = (request.POST.get("role") or request.GET.get("role") or "").strip()
    config = DEMO_ROLE_ACCOUNTS.get(role)
    if config is None or config["role"] == Role.ADMIN.value:
        messages.error(request, "Peran demo tidak dikenal. Pilih salah satu role yang tersedia.")
        return redirect("accounts:login")

    user = (
        get_user_model()
        .objects.filter(username=config["username"], is_active=True)
        .first()
    )
    if user is None:
        messages.error(
            request,
            "Akun demo belum tersedia. Jalankan `python manage.py seed_demo_users` terlebih dahulu.",
        )
        return redirect("accounts:login")

    login(request, user, backend="accounts.backends.ForgivingModelBackend")
    messages.success(
        request,
        f"Mode demo aktif: masuk sebagai {user.get_role_display()}.",
    )
    return redirect("accounts:dashboard")


def home(request):
    """Panduan dulu untuk pengguna baru, login langsung untuk yang sudah paham."""
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")
    if request.session.get("nt_guide_seen"):
        return redirect("accounts:login")
    return redirect("accounts:guide")


@never_cache
def guide(request):
    """Panduan pendaftaran sebelum login; bisa dilewati."""
    if request.GET.get("skip") == "1":
        request.session["nt_guide_seen"] = True
        if request.user.is_authenticated:
            return redirect("accounts:dashboard")
        return redirect("accounts:login")

    return render(
        request,
        "accounts/guide.html",
        {
            "guides": {
                key: ROLE_GUIDES[key] for key in SELF_REGISTER_ROLES
            },
            "assigned_roles": [
                {
                    "key": key,
                    "label": ROLE_GUIDES[key]["label"],
                    "summary": ROLE_GUIDES[key]["summary"],
                }
                for key in ROLE_GUIDES
                if key not in SELF_REGISTER_ROLES
            ],
        },
    )


@never_cache
def register(request):
    """Pendaftaran mandiri untuk peran publik, lalu diarahkan ke halaman masuk."""
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    initial = {}
    requested_role = request.GET.get("role", "")
    if requested_role in dict(RegistrationForm.ROLE_CHOICES):
        initial["role"] = requested_role

    if request.method == "POST":
        form = RegistrationForm(request.POST, initial=initial)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Pendaftaran berhasil. Silakan masuk menggunakan username dan password Anda.",
            )
            return redirect("accounts:login")
    else:
        form = RegistrationForm(initial=initial)

    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil berhasil diperbarui.")
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=request.user)
    return render(request, "accounts/profile.html", {"form": form})


def role_required(*allowed_roles):
    """Batasi akses ke peran tertentu; superuser tetap diizinkan."""

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_superuser and request.user.role not in allowed_roles:
                raise PermissionDenied("Peran Anda tidak memiliki akses ke halaman ini.")
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def _rupiah(value):
    amount = value or Decimal("0")
    return "Rp" + "{:,.0f}".format(amount).replace(",", ".")


HARI_SINGKAT = ("Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min")


def _smooth_path(points):
    """Ubah titik menjadi kurva Bezier halus untuk grafik SVG."""
    if not points:
        return ""
    if len(points) == 1:
        return f"M {points[0][0]},{points[0][1]}"

    path = f"M {points[0][0]},{points[0][1]}"
    for index in range(len(points) - 1):
        p0 = points[index - 1] if index > 0 else points[index]
        p1 = points[index]
        p2 = points[index + 1]
        p3 = points[index + 2] if index + 2 < len(points) else p2
        cp1x = p1[0] + (p2[0] - p0[0]) / 6
        cp1y = p1[1] + (p2[1] - p0[1]) / 6
        cp2x = p2[0] - (p3[0] - p1[0]) / 6
        cp2y = p2[1] - (p3[1] - p1[1]) / 6
        path += (
            f" C {cp1x:.2f},{cp1y:.2f} "
            f"{cp2x:.2f},{cp2y:.2f} {p2[0]:.2f},{p2[1]:.2f}"
        )
    return path


def _curve_chart(
    queryset,
    date_field,
    title,
    caption,
    unit="aktivitas",
    tone="green",
):
    """Bangun data kurva tujuh hari terakhir dari queryset Django."""
    today = timezone.localdate()
    start = today - timedelta(days=6)
    date_lookup = f"{date_field}__date"
    rows = (
        queryset.filter(
            **{
                f"{date_lookup}__gte": start,
                f"{date_lookup}__lte": today,
            }
        )
        .order_by()
        .values(date_lookup)
        .annotate(total=Count("pk"))
    )
    counts = {row[date_lookup]: row["total"] for row in rows}
    days = [start + timedelta(days=offset) for offset in range(7)]
    values = [counts.get(day, 0) for day in days]
    max_value = max(values) or 1

    points = []
    for index, (day, value) in enumerate(zip(days, values)):
        points.append(
            {
                # Titik diletakkan di tengah kolom agar sejajar dengan label hari.
                "x": round((index + 0.5) * 100 / 7, 2),
                "y": round(38 - (value / max_value) * 32, 2),
                "value": value,
                "short": HARI_SINGKAT[day.weekday()],
                "date": day.strftime("%d/%m"),
            }
        )

    line_path = _smooth_path([(point["x"], point["y"]) for point in points])
    total = sum(values)
    return {
        "title": title,
        "caption": caption,
        "unit": unit,
        "tone": tone,
        "kicker": "Tren 7 hari",
        "total": total,
        "average": f"{total / 7:.1f}".replace(".", ","),
        "peak": max(values),
        "points": points,
        "path": line_path,
        "area": (
            f"{line_path} L {points[-1]['x']:.2f},44 "
            f"L {points[0]['x']:.2f},44 Z"
        ),
        "has_data": total > 0,
    }


def _order_activity(order, meta_prefix=""):
    return {
        "title": order.order_number,
        "meta": f"{meta_prefix}{order.created_at:%d %b %Y}",
        "badge": order.get_status_display(),
        "badge_class": order.status_badge_class,
        "url": reverse("orders:detail", args=[order.pk]),
    }


def _farmer_dashboard(user):
    from assets.models import Asset
    from orders.models import Order, OrderStatus
    from products.models import Product

    products = Product.objects.filter(farmer=user)
    orders = Order.objects.filter(farmer=user).select_related("buyer")
    active_orders = orders.exclude(
        status__in=[OrderStatus.SELESAI.value, OrderStatus.DIBATALKAN.value]
    )

    recent = [
        _order_activity(order, f"Pembeli {order.buyer.get_username()} · ")
        for order in orders.order_by("-created_at")[:5]
    ]

    return {
        "stats": [
            {"icon": "sprout", "label": "Produk aktif", "value": products.filter(is_active=True).count(), "hint": "tampil di katalog"},
            {"icon": "package", "label": "Pesanan aktif", "value": active_orders.count(), "hint": "belum selesai"},
            {"icon": "clipboard-check", "label": "Menunggu QC", "value": orders.filter(status=OrderStatus.MENUNGGU_QC.value).count(), "hint": "perlu pemeriksaan"},
            {"icon": "archive", "label": "Aset tercatat", "value": Asset.objects.filter(owner=user).count(), "hint": "rak, tray, alat"},
        ],
        "actions": [
            {"label": "Tambah produk", "url": reverse("products:create"), "icon": "plus", "style": "success"},
            {"label": "Pesanan masuk", "url": reverse("orders:incoming"), "icon": "package", "style": "outline"},
            {"label": "Kelola aset", "url": reverse("assets:list"), "icon": "archive", "style": "outline"},
            {"label": "Performaku", "url": reverse("bankku:my_performance"), "icon": "bar-chart", "style": "outline"},
        ],
        "recent_title": "Pesanan terbaru",
        "recent": recent,
        "recent_url": reverse("orders:incoming"),
        "recent_empty": "Belum ada pesanan masuk. Produk yang aktif akan muncul di katalog pembeli.",
        "chart": _curve_chart(
            orders,
            "created_at",
            "Pesanan masuk",
            "Pesanan yang masuk ke usaha Anda dalam tujuh hari terakhir.",
            unit="pesanan",
        ),
    }


def _buyer_dashboard(user, is_horeca):
    from orders.models import Order, OrderStatus, OrderType

    orders = list(
        Order.objects.filter(buyer=user)
        .select_related("farmer")
        .prefetch_related("items")
        .order_by("-created_at")
    )
    active_orders = [
        order
        for order in orders
        if order.status not in {OrderStatus.SELESAI.value, OrderStatus.DIBATALKAN.value}
    ]
    total_spend = sum((order.total for order in orders), Decimal("0"))

    stats = [
        {"icon": "package", "label": "Pesanan aktif", "value": len(active_orders), "hint": "sedang diproses"},
        {
            "icon": "calendar" if is_horeca else "archive",
            "label": "Pre-order" if is_horeca else "Pesanan surplus",
            "value": sum(
                1
                for order in orders
                if order.order_type
                == (OrderType.PREORDER.value if is_horeca else OrderType.SURPLUS.value)
            ),
            "hint": "terjadwal" if is_horeca else "produk berlebih",
        },
        {
            "icon": "check-circle",
            "label": "Selesai",
            "value": sum(1 for order in orders if order.status == OrderStatus.SELESAI.value),
            "hint": "pesanan tuntas",
        },
        {"icon": "credit-card", "label": "Total belanja", "value": _rupiah(total_spend), "hint": "simulasi"},
    ]

    actions = [
        {"label": "Jelajahi katalog", "url": reverse("products:catalog"), "icon": "shopping-bag", "style": "success"},
    ]
    if is_horeca:
        actions.append({"label": "Buat pre-order", "url": reverse("orders:preorder_create"), "icon": "calendar", "style": "orange"})
    actions.extend(
        [
            {"label": "Produk surplus", "url": reverse("orders:surplus_create"), "icon": "sprout", "style": "outline"},
            {"label": "Pesanan saya", "url": reverse("orders:my_orders"), "icon": "package", "style": "outline"},
            {"label": "Pengiriman", "url": reverse("deliveries:list"), "icon": "truck", "style": "outline"},
        ]
    )

    return {
        "stats": stats,
        "actions": actions,
        "recent_title": "Pesanan terbaru",
        "recent": [
            _order_activity(order, f"Petani {order.farmer.get_username()} · ")
            for order in orders[:5]
        ],
        "recent_url": reverse("orders:my_orders"),
        "recent_empty": "Belum ada pesanan. Mulai dari katalog untuk memilih produk.",
        "chart": _curve_chart(
            Order.objects.filter(buyer=user),
            "created_at",
            "Pesanan Anda",
            "Pesanan yang Anda buat dalam tujuh hari terakhir.",
            unit="pesanan",
        ),
    }


def _qc_dashboard(user):
    from quality_control.models import QcStatus, QualityInspection

    queue = QualityInspection.objects.filter(
        result__in=[QcStatus.MENUNGGU.value, QcStatus.DIPERIKSA.value]
    ).select_related(
        "order_item__product", "order_item__order__farmer"
    )
    inspected = QualityInspection.objects.filter(inspector=user)
    today = timezone.localdate()

    recent = [
        {
            "title": f"{inspection.order_item.product.name} × {inspection.order_item.quantity}",
            "meta": (
                f"{inspection.order_item.order.order_number} · "
                f"{inspection.order_item.order.farmer.get_username()}"
            ),
            "badge": inspection.get_result_display(),
            "badge_class": inspection.result_badge_class,
            "url": reverse("quality_control:inspect", args=[inspection.pk]),
        }
        for inspection in queue.order_by("-created_at")[:5]
    ]

    return {
        "stats": [
            {"icon": "clipboard-check", "label": "Antrean QC", "value": queue.count(), "hint": "menunggu diperiksa"},
            {"icon": "search", "label": "Diperiksa hari ini", "value": inspected.filter(inspected_at__date=today).count(), "hint": "hari ini"},
            {"icon": "check-circle", "label": "Lolos", "value": inspected.filter(result=QcStatus.LOLOS.value).count(), "hint": "total Anda"},
            {"icon": "x", "label": "Ditolak", "value": inspected.filter(result=QcStatus.DITOLAK.value).count(), "hint": "total Anda"},
        ],
        "actions": [
            {"label": "Buka antrean QC", "url": reverse("quality_control:queue"), "icon": "search", "style": "success"},
        ],
        "recent_title": "Antrean pemeriksaan",
        "recent": recent,
        "recent_url": reverse("quality_control:queue"),
        "recent_empty": "Antrean bersih. Produk yang diajukan petani akan muncul di sini.",
        "chart": _curve_chart(
            inspected,
            "inspected_at",
            "Pemeriksaan QC",
            "Pemeriksaan yang Anda selesaikan dalam tujuh hari terakhir.",
            unit="pemeriksaan",
        ),
    }


def _mentor_dashboard(user):
    from mentorship.models import Mentorship, MentorshipActivity, MentorshipStatus

    mentorships = Mentorship.objects.filter(mentor=user).select_related("farmer")
    recent = [
        {
            "title": mentorship.topic,
            "meta": f"{mentorship.farmer.get_username()} · {mentorship.scheduled_at:%d %b %Y %H:%M}",
            "badge": mentorship.get_status_display(),
            "badge_class": mentorship.status_badge_class,
            "url": reverse("mentorship:detail", args=[mentorship.pk]),
        }
        for mentorship in mentorships.order_by("-scheduled_at")[:5]
    ]

    return {
        "stats": [
            {"icon": "calendar", "label": "Jadwal aktif", "value": mentorships.filter(status=MentorshipStatus.DIJADWALKAN.value).count(), "hint": "akan datang"},
            {"icon": "check-circle", "label": "Selesai", "value": mentorships.filter(status=MentorshipStatus.SELESAI.value).count(), "hint": "pendampingan"},
            {"icon": "users", "label": "Petani dibimbing", "value": mentorships.values("farmer").distinct().count(), "hint": "petani"},
            {"icon": "book", "label": "Catatan kegiatan", "value": MentorshipActivity.objects.filter(mentorship__mentor=user).count(), "hint": "riwayat"},
        ],
        "actions": [
            {"label": "Tambah pendampingan", "url": reverse("mentorship:create"), "icon": "plus", "style": "success"},
            {"label": "Daftar pendampingan", "url": reverse("mentorship:list"), "icon": "file-text", "style": "outline"},
        ],
        "recent_title": "Pendampingan terbaru",
        "recent": recent,
        "recent_url": reverse("mentorship:list"),
        "recent_empty": "Belum ada jadwal pendampingan. Tambahkan satu untuk memulai.",
        "chart": _curve_chart(
            MentorshipActivity.objects.filter(mentorship__mentor=user),
            "activity_date",
            "Kegiatan pendampingan",
            "Catatan kegiatan yang Anda buat dalam tujuh hari terakhir.",
            unit="kegiatan",
        ),
    }


def _bank_dashboard(user):
    from django.contrib.auth import get_user_model

    from bankku.models import EligibilityBand, FinancingAssessment
    from orders.models import Order

    User = get_user_model()
    farmers = User.objects.filter(role=Role.FARMER.value)
    assessments = FinancingAssessment.objects.select_related("performance__farmer")
    average_score = assessments.aggregate(average=Avg("total_score"))["average"] or Decimal("0")

    recent = [
        {
            "title": assessment.performance.farmer.get_username(),
            "meta": f"Skor {assessment.total_score}/100",
            "badge": assessment.get_eligibility_display(),
            "badge_class": assessment.eligibility_badge_class,
            "url": reverse("bankku:dashboard") + f"?petani={assessment.performance.farmer_id}",
        }
        for assessment in assessments.order_by("-total_score")[:5]
    ]

    return {
        "stats": [
            {"icon": "users", "label": "Petani mitra", "value": farmers.count(), "hint": "terdaftar"},
            {"icon": "bar-chart", "label": "Sudah dinilai", "value": assessments.count(), "hint": "indikator"},
            {"icon": "badge-check", "label": "Potensial", "value": assessments.filter(eligibility=EligibilityBand.POTENSIAL.value).count(), "hint": "simulasi"},
            {"icon": "bar-chart", "label": "Rata-rata skor", "value": f"{average_score:.1f}".replace(".", ","), "hint": "dari 100"},
        ],
        "actions": [
            {"label": "Buka BANKKU", "url": reverse("bankku:dashboard"), "icon": "bar-chart", "style": "success"},
        ],
        "recent_title": "Performa petani",
        "recent": recent,
        "recent_url": reverse("bankku:dashboard"),
        "recent_empty": "Belum ada data performa petani yang dapat ditampilkan.",
        "chart": _curve_chart(
            Order.objects.filter(farmer__role=Role.FARMER.value),
            "created_at",
            "Aktivitas pesanan petani",
            "Pesanan dari petani mitra dalam tujuh hari terakhir.",
            unit="pesanan",
            tone="amber",
        ),
    }


def _admin_dashboard(user):
    from django.contrib.auth import get_user_model

    from orders.models import Order
    from quality_control.models import QcStatus, QualityInspection

    User = get_user_model()
    orders = Order.objects.select_related("buyer", "farmer").order_by("-created_at")
    queue_count = QualityInspection.objects.filter(
        result__in=[QcStatus.MENUNGGU.value, QcStatus.DIPERIKSA.value]
    ).count()

    return {
        "stats": [
            {"icon": "users", "label": "Pengguna", "value": User.objects.count(), "hint": "akun terdaftar"},
            {"icon": "sprout", "label": "Petani", "value": User.objects.filter(role=Role.FARMER.value).count(), "hint": "mitra aktif"},
            {"icon": "package", "label": "Pesanan", "value": orders.count(), "hint": "seluruh platform"},
            {"icon": "clipboard-check", "label": "Antrean QC", "value": queue_count, "hint": "perlu diperiksa"},
        ],
        "actions": [
            {"label": "Panel admin", "url": reverse("admin:index"), "icon": "settings", "style": "success"},
            {"label": "Katalog", "url": reverse("products:catalog"), "icon": "shopping-bag", "style": "outline"},
            {"label": "Semua pesanan", "url": reverse("orders:my_orders"), "icon": "package", "style": "outline"},
            {"label": "Antrean QC", "url": reverse("quality_control:queue"), "icon": "search", "style": "outline"},
            {"label": "BANKKU", "url": reverse("bankku:dashboard"), "icon": "bar-chart", "style": "outline"},
        ],
        "recent_title": "Pesanan terbaru",
        "recent": [
            _order_activity(order, f"{order.buyer.get_username()} → {order.farmer.get_username()} · ")
            for order in orders[:5]
        ],
        "recent_url": reverse("orders:my_orders"),
        "recent_empty": "Belum ada pesanan di platform.",
        "chart": _curve_chart(
            orders,
            "created_at",
            "Pesanan platform",
            "Pesanan yang masuk ke seluruh platform dalam tujuh hari terakhir.",
            unit="pesanan",
        ),
    }


def _dashboard_data(user):
    builders = {
        Role.FARMER.value: _farmer_dashboard,
        Role.HORECA.value: lambda account: _buyer_dashboard(account, is_horeca=True),
        Role.CONSUMER.value: lambda account: _buyer_dashboard(account, is_horeca=False),
        Role.QC.value: _qc_dashboard,
        Role.MENTOR.value: _mentor_dashboard,
        Role.BANK.value: _bank_dashboard,
        Role.ADMIN.value: _admin_dashboard,
    }
    builder = builders.get(user.role, _farmer_dashboard)
    return builder(user)


@never_cache
@role_required(*[role.value for role in Role])
def dashboard(request):
    role_value = request.user.role
    role_config = ROLE_DASHBOARDS.get(role_value, ROLE_DASHBOARDS[Role.CONSUMER.value])
    return render(
        request,
        "accounts/dashboard.html",
        {
            "dashboard": role_config,
            "dashboard_data": _dashboard_data(request.user),
            "role_label": request.user.get_role_display(),
        },
    )
