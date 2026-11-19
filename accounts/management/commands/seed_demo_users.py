"""Buat/perbaiki akun demo NusaTani dengan password yang pasti benar."""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from accounts.roles import Role

DEMO_PASSWORD = "password123"

DEMO_USERS = (
    ("admin", Role.ADMIN.value, True),
    ("petani1", Role.FARMER.value, False),
    ("horeca1", Role.HORECA.value, False),
    ("konsumen1", Role.CONSUMER.value, False),
    ("qc1", Role.QC.value, False),
    ("mentor1", Role.MENTOR.value, False),
    ("bank1", Role.BANK.value, False),
)


class Command(BaseCommand):
    help = "Membuat atau memperbaiki 7 akun demo agar bisa login dengan password123."

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            default=DEMO_PASSWORD,
            help=f"Password demo yang dipakai (default: {DEMO_PASSWORD}).",
        )
        parser.add_argument(
            "--check",
            action="store_true",
            help="Hanya laporkan status akun tanpa mengubahnya.",
        )

    def handle(self, *args, **options):
        password = options["password"]
        check_only = options["check"]
        User = get_user_model()
        updated = 0
        created = 0

        if check_only:
            self.stdout.write("Mode pemeriksaan (tanpa perubahan):")
            for username, _role, _is_admin in DEMO_USERS:
                user = User.objects.filter(username=username).first()
                if user is None:
                    self.stdout.write(self.style.WARNING(f"{username}: TIDAK ADA"))
                elif not user.is_active:
                    self.stdout.write(self.style.ERROR(f"{username}: NONAKTIF"))
                elif user.check_password(password):
                    self.stdout.write(self.style.SUCCESS(f"{username}: OK"))
                else:
                    self.stdout.write(self.style.ERROR(f"{username}: PASSWORD SALAH"))
            return

        for username, role, is_admin in DEMO_USERS:
            user, was_created = User.objects.update_or_create(
                username=username,
                defaults={
                    "email": f"{username}@example.com",
                    "role": role,
                    "is_staff": is_admin,
                    "is_superuser": is_admin,
                    "is_active": True,
                },
            )
            # Selalu set ulang agar hash password valid walaupun akun sudah ada.
            user.set_password(password)
            user.save(update_fields=["password"])

            valid = user.check_password(password)
            if not valid:
                self.stderr.write(self.style.ERROR(f"GAGAL: {username} tidak bisa memverifikasi password."))
                continue

            if was_created:
                created += 1
                action = "dibuat"
            else:
                updated += 1
                action = "diperbaiki"
            self.stdout.write(self.style.SUCCESS(f"{username}: {action} ({role})"))

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Selesai. {created} akun dibuat, {updated} akun diperbaiki. "
                f"Password demo: {password}"
            )
        )
