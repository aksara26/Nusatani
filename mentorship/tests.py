"""Pengujian modul Mentorku: jadwal, materi, evaluasi, dan riwayat kegiatan."""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Mentorship, MentorshipActivity, MentorshipStatus

User = get_user_model()
DATETIME_FORMAT = "%Y-%m-%dT%H:%M"


class MentorshipTests(TestCase):
    def setUp(self):
        self.mentor = User.objects.create_user(
            username="mentoruji", password="password123", role="mentor"
        )
        self.farmer = User.objects.create_user(
            username="petaniuji", password="password123", role="farmer"
        )
        self.other_farmer = User.objects.create_user(
            username="petaniuji2", password="password123", role="farmer"
        )
        self.admin = User.objects.create_superuser(
            username="adminuji", password="password123", role="admin"
        )

    def scheduled_at(self):
        return (timezone.now() + timedelta(days=2)).strftime(DATETIME_FORMAT)

    def create_mentorship(self, topic="Budidaya microgreens", farmer=None, mentor=None):
        return Mentorship.objects.create(
            farmer=farmer or self.farmer,
            mentor=mentor or self.mentor,
            topic=topic,
            description="Materi dasar budidaya.",
            scheduled_at=timezone.now() + timedelta(days=2),
        )

    def test_mentor_can_create_mentorship_for_farmer(self):
        self.client.login(username="mentoruji", password="password123")
        response = self.client.post(
            reverse("mentorship:create"),
            {
                "farmer": self.farmer.pk,
                "topic": "Panen dan pengemasan",
                "description": "Teknik panen bersih.",
                "scheduled_at": self.scheduled_at(),
                "status": MentorshipStatus.DIJADWALKAN.value,
            },
        )
        self.assertEqual(response.status_code, 302)
        mentorship = Mentorship.objects.get(topic="Panen dan pengemasan")
        self.assertEqual(mentorship.mentor, self.mentor)
        self.assertEqual(mentorship.farmer, self.farmer)

    def test_farmer_cannot_create_mentorship(self):
        self.client.login(username="petaniuji", password="password123")
        response = self.client.post(
            reverse("mentorship:create"),
            {
                "farmer": self.farmer.pk,
                "topic": "Panen",
                "scheduled_at": self.scheduled_at(),
                "status": MentorshipStatus.DIJADWALKAN.value,
            },
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Mentorship.objects.exists())

    def test_farmer_sees_only_own_mentorships(self):
        own = self.create_mentorship(topic="Materi petani satu")
        self.create_mentorship(topic="Materi petani dua", farmer=self.other_farmer)

        self.client.login(username="petaniuji", password="password123")
        response = self.client.get(reverse("mentorship:list"))
        self.assertContains(response, own.topic)
        self.assertNotContains(response, "Materi petani dua")

    def test_admin_sees_all_mentorships(self):
        self.create_mentorship(topic="Materi petani satu")
        self.create_mentorship(topic="Materi petani dua", farmer=self.other_farmer)
        self.client.login(username="adminuji", password="password123")
        response = self.client.get(reverse("mentorship:list"))
        self.assertContains(response, "Materi petani satu")
        self.assertContains(response, "Materi petani dua")

    def test_activity_is_recorded_and_updates_evaluation(self):
        mentorship = self.create_mentorship()
        self.client.login(username="petaniuji", password="password123")
        response = self.client.post(
            reverse("mentorship:activity_create", args=[mentorship.pk]),
            {
                "activity_date": self.scheduled_at(),
                "description": "Praktik panen berhasil dilakukan.",
                "evaluation": "Hasil panen sesuai standar.",
            },
        )
        self.assertEqual(response.status_code, 302)

        activity = MentorshipActivity.objects.get(mentorship=mentorship)
        self.assertEqual(activity.author, self.farmer)
        self.assertEqual(activity.description, "Praktik panen berhasil dilakukan.")
        mentorship.refresh_from_db()
        self.assertEqual(mentorship.evaluation, "Hasil panen sesuai standar.")

        detail = self.client.get(reverse("mentorship:detail", args=[mentorship.pk]))
        self.assertContains(detail, "Praktik panen berhasil dilakukan.")
        self.assertContains(detail, "Hasil panen sesuai standar.")

    def test_unrelated_user_cannot_view_mentorship_detail(self):
        mentorship = self.create_mentorship()
        self.client.login(username="petaniuji2", password="password123")
        response = self.client.get(reverse("mentorship:detail", args=[mentorship.pk]))
        self.assertEqual(response.status_code, 403)

    def test_only_own_mentor_can_update_schedule(self):
        mentorship = self.create_mentorship()
        other_mentor = User.objects.create_user(
            username="mentoruji2", password="password123", role="mentor"
        )
        self.client.login(username="mentoruji2", password="password123")
        response = self.client.get(reverse("mentorship:update", args=[mentorship.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Mentorship.objects.get(pk=mentorship.pk).mentor, self.mentor)
        self.assertIsNotNone(other_mentor.pk)

    def test_mentor_can_mark_mentorship_complete(self):
        mentorship = self.create_mentorship()
        self.client.login(username="mentoruji", password="password123")
        response = self.client.post(
            reverse("mentorship:update", args=[mentorship.pk]),
            {
                "farmer": self.farmer.pk,
                "topic": mentorship.topic,
                "description": mentorship.description,
                "scheduled_at": self.scheduled_at(),
                "status": MentorshipStatus.SELESAI.value,
            },
        )
        self.assertEqual(response.status_code, 302)
        mentorship.refresh_from_db()
        self.assertEqual(mentorship.status, MentorshipStatus.SELESAI.value)
