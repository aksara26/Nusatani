"""Autentikasi, panduan awal, profil, pengalihan, dan dashboard per peran."""

from decimal import Decimal
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import PermissionDenied
from django.db.models import Avg
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.decorators.cache import never_cache

from .forms import NusaTaniAuthenticationForm, ProfileForm, RegistrationForm
from .roles import ROLE_DASHBOARDS, ROLE_GUIDES, SELF_REGISTER_ROLES, Role


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
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")
    if request.GET.get("skip") == "1":
        request.session["nt_guide_seen"] = True
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
            {"icon": "🌱", "label": "Produk aktif", "value": products.filter(is_active=True).count(), "hint": "tampil di katalog"},
            {"icon": "📦", "label": "Pesanan aktif", "value": active_orders.count(), "hint": "belum selesai"},
            {"icon": "🔍", "label": "Menunggu QC", "value": orders.filter(status=OrderStatus.MENUNGGU_QC.value).count(), "hint": "perlu pemeriksaan"},
            {"icon": "🧰", "label": "Aset tercatat", "value": Asset.objects.filter(owner=user).count(), "hint": "rak, tray, alat"},
        ],
        "actions": [
            {"label": "Tambah produk", "url": reverse("products:create"), "icon": "＋", "style": "success"},
            {"label": "Pesanan masuk", "url": reverse("orders:incoming"), "icon": "📥", "style": "outline"},
            {"label": "Kelola aset", "url": reverse("assets:list"), "icon": "🧰", "style": "outline"},
            {"label": "Performaku", "url": reverse("bankku:my_performance"), "icon": "📈", "style": "outline"},
        ],
        "recent_title": "Pesanan terbaru",
        "recent": recent,
        "recent_url": reverse("orders:incoming"),
        "recent_empty": "Belum ada pesanan masuk. Produk yang aktif akan muncul di katalog pembeli.",
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
        {"icon": "📦", "label": "Pesanan aktif", "value": len(active_orders), "hint": "sedang diproses"},
        {
            "icon": "🗓️" if is_horeca else "♻️",
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
            "icon": "✅",
            "label": "Selesai",
            "value": sum(1 for order in orders if order.status == OrderStatus.SELESAI.value),
            "hint": "pesanan tuntas",
        },
        {"icon": "💳", "label": "Total belanja", "value": _rupiah(total_spend), "hint": "simulasi"},
    ]

    actions = [
        {"label": "Jelajahi katalog", "url": reverse("products:catalog"), "icon": "🛒", "style": "success"},
    ]
    if is_horeca:
        actions.append({"label": "Buat pre-order", "url": reverse("orders:preorder_create"), "icon": "🗓️", "style": "orange"})
    actions.extend(
        [
            {"label": "Produk surplus", "url": reverse("orders:surplus_create"), "icon": "♻️", "style": "outline"},
            {"label": "Pesanan saya", "url": reverse("orders:my_orders"), "icon": "📦", "style": "outline"},
            {"label": "Pengiriman", "url": reverse("deliveries:list"), "icon": "🚚", "style": "outline"},
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
            {"icon": "⏳", "label": "Antrean QC", "value": queue.count(), "hint": "menunggu diperiksa"},
            {"icon": "🔍", "label": "Diperiksa hari ini", "value": inspected.filter(inspected_at__date=today).count(), "hint": "hari ini"},
            {"icon": "✅", "label": "Lolos", "value": inspected.filter(result=QcStatus.LOLOS.value).count(), "hint": "total Anda"},
            {"icon": "⛔", "label": "Ditolak", "value": inspected.filter(result=QcStatus.DITOLAK.value).count(), "hint": "total Anda"},
        ],
        "actions": [
            {"label": "Buka antrean QC", "url": reverse("quality_control:queue"), "icon": "🔍", "style": "success"},
        ],
        "recent_title": "Antrean pemeriksaan",
        "recent": recent,
        "recent_url": reverse("quality_control:queue"),
        "recent_empty": "Antrean bersih. Produk yang diajukan petani akan muncul di sini.",
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
            {"icon": "🗓️", "label": "Jadwal aktif", "value": mentorships.filter(status=MentorshipStatus.DIJADWALKAN.value).count(), "hint": "akan datang"},
            {"icon": "✅", "label": "Selesai", "value": mentorships.filter(status=MentorshipStatus.SELESAI.value).count(), "hint": "pendampingan"},
            {"icon": "🌾", "label": "Petani dibimbing", "value": mentorships.values("farmer").distinct().count(), "hint": "petani"},
            {"icon": "📝", "label": "Catatan kegiatan", "value": MentorshipActivity.objects.filter(mentorship__mentor=user).count(), "hint": "riwayat"},
        ],
        "actions": [
            {"label": "Tambah pendampingan", "url": reverse("mentorship:create"), "icon": "＋", "style": "success"},
            {"label": "Daftar pendampingan", "url": reverse("mentorship:list"), "icon": "🗂️", "style": "outline"},
        ],
        "recent_title": "Pendampingan terbaru",
        "recent": recent,
        "recent_url": reverse("mentorship:list"),
        "recent_empty": "Belum ada jadwal pendampingan. Tambahkan satu untuk memulai.",
    }


def _bank_dashboard(user):
    from django.contrib.auth import get_user_model

    from bankku.models import EligibilityBand, FinancingAssessment

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
            {"icon": "🌾", "label": "Petani mitra", "value": farmers.count(), "hint": "terdaftar"},
            {"icon": "📊", "label": "Sudah dinilai", "value": assessments.count(), "hint": "indikator"},
            {"icon": "⭐", "label": "Potensial", "value": assessments.filter(eligibility=EligibilityBand.POTENSIAL.value).count(), "hint": "simulasi"},
            {"icon": "📈", "label": "Rata-rata skor", "value": f"{average_score:.1f}".replace(".", ","), "hint": "dari 100"},
        ],
        "actions": [
            {"label": "Buka BANKKU", "url": reverse("bankku:dashboard"), "icon": "📊", "style": "success"},
        ],
        "recent_title": "Performa petani",
        "recent": recent,
        "recent_url": reverse("bankku:dashboard"),
        "recent_empty": "Belum ada data performa petani yang dapat ditampilkan.",
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
            {"icon": "👥", "label": "Pengguna", "value": User.objects.count(), "hint": "akun terdaftar"},
            {"icon": "🌾", "label": "Petani", "value": User.objects.filter(role=Role.FARMER.value).count(), "hint": "mitra aktif"},
            {"icon": "📦", "label": "Pesanan", "value": orders.count(), "hint": "seluruh platform"},
            {"icon": "🔍", "label": "Antrean QC", "value": queue_count, "hint": "perlu diperiksa"},
        ],
        "actions": [
            {"label": "Panel admin", "url": reverse("admin:index"), "icon": "⚙️", "style": "success"},
            {"label": "Katalog", "url": reverse("products:catalog"), "icon": "🛒", "style": "outline"},
            {"label": "Semua pesanan", "url": reverse("orders:my_orders"), "icon": "📦", "style": "outline"},
            {"label": "Antrean QC", "url": reverse("quality_control:queue"), "icon": "🔍", "style": "outline"},
            {"label": "BANKKU", "url": reverse("bankku:dashboard"), "icon": "📊", "style": "outline"},
        ],
        "recent_title": "Pesanan terbaru",
        "recent": [
            _order_activity(order, f"{order.buyer.get_username()} → {order.farmer.get_username()} · ")
            for order in orders[:5]
        ],
        "recent_url": reverse("orders:my_orders"),
        "recent_empty": "Belum ada pesanan di platform.",
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
