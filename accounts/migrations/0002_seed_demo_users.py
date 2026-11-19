"""Pastikan akun uji internal punya hash password yang valid setelah migrate."""

from django.contrib.auth.hashers import make_password
from django.db import migrations

DEMO_PASSWORD = "password123"

DEMO_USERS = (
    ("admin", "admin", True),
    ("petani1", "farmer", False),
    ("horeca1", "horeca", False),
    ("konsumen1", "consumer", False),
    ("qc1", "qc", False),
    ("mentor1", "mentor", False),
    ("bank1", "bank", False),
)


def seed_demo_users(apps, schema_editor):
    User = apps.get_model("accounts", "CustomUser")
    for username, role, is_admin in DEMO_USERS:
        user, _created = User.objects.update_or_create(
            username=username,
            defaults={
                "email": f"{username}@example.com",
                "role": role,
                "is_staff": is_admin,
                "is_superuser": is_admin,
                "is_active": True,
            },
        )
        # Model historis tidak punya method set_password(), jadi hash manual.
        user.password = make_password(DEMO_PASSWORD)
        user.save(update_fields=["password"])


def noop(apps, schema_editor):
    """Tidak menghapus akun saat migrasi dibatalkan."""
    return None


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_demo_users, noop),
    ]
