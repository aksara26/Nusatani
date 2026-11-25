"""Navigasi fitur per peran NusaTani.

Navbar utama hanya memuat pintasan umum (beranda, katalog, panduan, dan
dashboard). Modul ini menyusun navbar sekunder berisi seluruh fitur yang
tersedia untuk peran pengguna aktif, sehingga pengguna dapat berpindah
fitur langsung tanpa kembali ke dashboard terlebih dahulu.
"""

from fnmatch import fnmatchcase

from django.urls import NoReverseMatch, reverse

from .roles import Role


def _item(label, route, icon, match=None, *, staff_only=False, superuser_only=False):
    """Satu tautan fitur beserta pola URL yang membuatnya tampil aktif."""
    return {
        "label": label,
        "route": route,
        "icon": icon,
        # Pola memakai fnmatch, mis. "deliveries:*" untuk semua halaman app.
        "match": tuple(match or (route,)),
        "staff_only": staff_only,
        "superuser_only": superuser_only,
    }


ROLE_FEATURE_MENUS = {
    Role.FARMER.value: {
        "label": "Fitur Petani",
        "items": (
            _item("Dashboard", "accounts:dashboard", "bar-chart"),
            _item(
                "Produk Saya",
                "products:my_products",
                "sprout",
                (
                    "products:my_products",
                    "products:create",
                    "products:update",
                    "products:inventory_update",
                ),
            ),
            _item(
                "Pesanan Masuk",
                "orders:incoming",
                "package",
                (
                    "orders:incoming",
                    "orders:detail",
                    "orders:update_status",
                    "orders:update_payment",
                ),
            ),
            _item("Pengiriman", "deliveries:list", "truck", ("deliveries:*",)),
            _item("Asetku", "assets:list", "archive", ("assets:*",)),
            _item(
                "Mentorku",
                "mentorship:list",
                "graduation-cap",
                (
                    "mentorship:list",
                    "mentorship:detail",
                    "mentorship:update",
                    "mentorship:activity_create",
                ),
            ),
            _item("Performaku", "bankku:my_performance", "bar-chart"),
            _item(
                "Katalog",
                "products:catalog",
                "layout-dashboard",
                ("products:catalog", "products:surplus", "products:detail"),
            ),
        ),
    },
    Role.HORECA.value: {
        "label": "Fitur HOREKA",
        "items": (
            _item("Dashboard", "accounts:dashboard", "bar-chart"),
            _item(
                "Katalog",
                "products:catalog",
                "layout-dashboard",
                ("products:catalog", "products:detail"),
            ),
            _item("Sisaku", "products:surplus", "sprout", ("products:surplus",)),
            _item("Pre-order", "orders:preorder_create", "calendar"),
            _item("Pesan Surplus", "orders:surplus_create", "shopping-bag"),
            _item(
                "Pesanan Saya",
                "orders:my_orders",
                "package",
                ("orders:my_orders", "orders:detail"),
            ),
            _item("Pengiriman", "deliveries:list", "truck", ("deliveries:*",)),
        ),
    },
    Role.CONSUMER.value: {
        "label": "Fitur Konsumen",
        "items": (
            _item("Dashboard", "accounts:dashboard", "bar-chart"),
            _item(
                "Katalog",
                "products:catalog",
                "layout-dashboard",
                ("products:catalog", "products:detail"),
            ),
            _item("Sisaku", "products:surplus", "sprout", ("products:surplus",)),
            _item("Pesan Surplus", "orders:surplus_create", "shopping-bag"),
            _item(
                "Pesanan Saya",
                "orders:my_orders",
                "package",
                ("orders:my_orders", "orders:detail"),
            ),
            _item("Pengiriman", "deliveries:list", "truck", ("deliveries:*",)),
        ),
    },
    Role.QC.value: {
        "label": "Fitur Quality Control",
        "items": (
            _item("Dashboard", "accounts:dashboard", "bar-chart"),
            _item(
                "Antrean QC",
                "quality_control:queue",
                "clipboard-check",
                ("quality_control:*", "orders:detail"),
            ),
        ),
    },
    Role.MENTOR.value: {
        "label": "Fitur Mentor",
        "items": (
            _item("Dashboard", "accounts:dashboard", "bar-chart"),
            _item(
                "Mentorku",
                "mentorship:list",
                "graduation-cap",
                (
                    "mentorship:list",
                    "mentorship:detail",
                    "mentorship:update",
                    "mentorship:activity_create",
                ),
            ),
            _item(
                "Tambah Pendampingan",
                "mentorship:create",
                "plus",
                ("mentorship:create",),
            ),
        ),
    },
    Role.BANK.value: {
        "label": "Fitur BANKKU",
        "items": (
            _item("Dashboard", "accounts:dashboard", "bar-chart"),
            _item("BANKKU", "bankku:dashboard", "landmark", ("bankku:dashboard",)),
        ),
    },
    Role.ADMIN.value: {
        "label": "Fitur Administrator",
        "items": (
            _item("Dashboard", "accounts:dashboard", "bar-chart"),
            _item(
                "Panel Admin",
                "admin:index",
                "settings",
                ("admin:*",),
                staff_only=True,
            ),
            _item(
                "Katalog",
                "products:catalog",
                "layout-dashboard",
                ("products:catalog", "products:surplus", "products:detail"),
            ),
            _item(
                "Semua Pesanan",
                "orders:my_orders",
                "package",
                ("orders:my_orders", "orders:detail"),
                superuser_only=True,
            ),
            _item(
                "Antrean QC",
                "quality_control:queue",
                "clipboard-check",
                ("quality_control:*",),
                superuser_only=True,
            ),
            _item(
                "Mentorku",
                "mentorship:list",
                "graduation-cap",
                ("mentorship:*",),
                superuser_only=True,
            ),
            _item(
                "BANKKU",
                "bankku:dashboard",
                "landmark",
                ("bankku:dashboard",),
                superuser_only=True,
            ),
            _item(
                "Pengiriman",
                "deliveries:list",
                "truck",
                ("deliveries:*",),
                superuser_only=True,
            ),
        ),
    },
}


def _current_route(resolver_match):
    """Nama rute aktif dalam bentuk ``namespace:url_name``."""
    if resolver_match is None:
        return ""
    namespace = resolver_match.namespace or ""
    url_name = resolver_match.url_name or ""
    return f"{namespace}:{url_name}" if namespace else url_name


def build_role_navigation(user, resolver_match):
    """Susun daftar tautan fitur untuk pengguna dan halaman yang sedang dibuka."""
    if user is None or not user.is_authenticated:
        return None

    role = getattr(user, "role", "") or ""
    config = ROLE_FEATURE_MENUS.get(role)
    if config is None and user.is_superuser:
        config = ROLE_FEATURE_MENUS[Role.ADMIN.value]
    if config is None:
        return None

    current = _current_route(resolver_match)
    items = []
    for item in config["items"]:
        if item["staff_only"] and not user.is_staff:
            continue
        if item["superuser_only"] and not user.is_superuser:
            continue
        try:
            url = reverse(item["route"])
        except NoReverseMatch:
            continue
        items.append(
            {
                "label": item["label"],
                "url": url,
                "icon": item["icon"],
                "active": any(
                    fnmatchcase(current, pattern) for pattern in item["match"]
                ),
            }
        )

    if not items:
        return None
    return {"label": config["label"], "items": items}
