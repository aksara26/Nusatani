"""Autentikasi, pengalihan, dan dashboard per peran."""

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.decorators.cache import never_cache

from .roles import ROLE_DASHBOARDS, Role


class NusaTaniLoginView(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        """Arahkan ke tujuan `next` yang valid, jika tidak ke dashboard."""
        return self.get_redirect_url() or reverse("accounts:dashboard")


class NusaTaniLogoutView(LogoutView):
    next_page = reverse_lazy("accounts:login")


def home(request):
    """Halaman awal: dashboard untuk pengguna login, login untuk lainnya."""
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")
    return redirect("accounts:login")


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
