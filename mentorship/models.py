"""Pendampingan petani: materi, jadwal, evaluasi, dan riwayat kegiatan (Tahap 6)."""

from django.conf import settings
from django.db import models
from django.utils import timezone

from accounts.roles import Role


class MentorshipStatus(models.TextChoices):
    DIJADWALKAN = "dijadwalkan", "Dijadwalkan"
    SELESAI = "selesai", "Selesai"
    DIBATALKAN = "dibatalkan", "Dibatalkan"


class Mentorship(models.Model):
    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mentorships_as_farmer",
        limit_choices_to={"role": Role.FARMER.value},
        verbose_name="Petani",
    )
    mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mentorships_as_mentor",
        limit_choices_to={"role": Role.MENTOR.value},
        verbose_name="Mentor",
    )
    topic = models.CharField(max_length=150, verbose_name="Materi pembelajaran")
    description = models.TextField(blank=True, verbose_name="Detail materi")
    scheduled_at = models.DateTimeField(verbose_name="Jadwal pendampingan")
    status = models.CharField(
        max_length=16,
        choices=MentorshipStatus.choices,
        default=MentorshipStatus.DIJADWALKAN.value,
        verbose_name="Status",
    )
    evaluation = models.TextField(blank=True, verbose_name="Catatan evaluasi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui")

    class Meta:
        ordering = ["-scheduled_at"]
        verbose_name = "Pendampingan"
        verbose_name_plural = "Pendampingan"

    def __str__(self):
        return f"{self.topic} — {self.farmer.username} ({self.mentor.username})"

    @property
    def status_badge_class(self):
        return {
            MentorshipStatus.DIJADWALKAN.value: "text-bg-info",
            MentorshipStatus.SELESAI.value: "text-bg-success",
            MentorshipStatus.DIBATALKAN.value: "text-bg-danger",
        }.get(self.status, "text-bg-secondary")

    @property
    def latest_activity(self):
        return self.activities.order_by("-activity_date", "-created_at").first()


class MentorshipActivity(models.Model):
    mentorship = models.ForeignKey(
        Mentorship,
        on_delete=models.CASCADE,
        related_name="activities",
        verbose_name="Pendampingan",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mentorship_activities",
        verbose_name="Pencatat",
    )
    activity_date = models.DateTimeField(default=timezone.now, verbose_name="Waktu kegiatan")
    description = models.TextField(verbose_name="Riwayat kegiatan")
    evaluation = models.TextField(blank=True, verbose_name="Catatan evaluasi kegiatan")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat")

    class Meta:
        ordering = ["-activity_date", "-created_at"]
        verbose_name = "Kegiatan pendampingan"
        verbose_name_plural = "Kegiatan pendampingan"

    def __str__(self):
        return f"{self.mentorship.topic} — {self.activity_date:%d %b %Y %H:%M}"
