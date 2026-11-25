"""Context processor untuk navigasi fitur per peran."""

from .navigation import build_role_navigation


def role_navigation(request):
    """Sediakan ``role_nav`` di semua template yang memakai base.html."""
    return {
        "role_nav": build_role_navigation(
            getattr(request, "user", None),
            getattr(request, "resolver_match", None),
        )
    }
