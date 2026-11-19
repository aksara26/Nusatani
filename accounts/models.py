"""Model akun pengguna NusaTani."""

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

from .roles import Role


class CustomUserManager(UserManager):
    """Manager yang memastikan setiap akun memiliki peran yang valid."""

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("role", Role.CONSUMER.value)
        return super().create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("role", Role.ADMIN.value)
        return super().create_superuser(username, email, password, **extra_fields)


class CustomUser(AbstractUser):
    role = models.CharField(
        max_length=32,
        choices=Role.choices,
        default=Role.CONSUMER.value,
        db_index=True,
        verbose_name="Peran",
    )

    objects = CustomUserManager()

    class Meta(AbstractUser.Meta):
        verbose_name = "Pengguna"
        verbose_name_plural = "Pengguna"

    def __str__(self):
        return f"{self.username} — {self.get_role_display()}"
