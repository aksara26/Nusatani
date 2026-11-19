"""Autentikasi, panduan awal, profil, pengalihan, dan dashboard per peran."""

from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.decorators.cache import never_cache

from .forms import NusaTaniAuthenticationForm, ProfileForm, RegistrationForm
from .roles import ROLE_DASHBOARDS, ROLE_GUIDES, SELF_REGISTER_ROLES, Role


class NusaTaniLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = NusaTaniAuthenticationForm
    redirect_authenticated_user = True

    def get_initial(self):
        initial = super().get_initial()
        suggested = self.request.GET.get("username", "").strip()
        if suggested:
            initial["username"] = suggested[:150]
        return initial

    def get_success_url(self):
        """Arahkan ke tujuan `next` yang valid, jika tidak ke dashboard."""
        return self.get_redirect_url() or reverse("accounts:dashboard")


class NusaTaniLogoutView(LogoutView):
    next_page = reverse_lazy("accounts:login")


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
            "role_label": request.user.get_role_display(),
        },
    )
