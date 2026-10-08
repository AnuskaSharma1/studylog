from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import StudySession, WeeklyGoal, current_streak


class StudySessionTests(TestCase):
    def test_course_name_is_normalized(self):
        s = StudySession.objects.create(course="  csce   490 ", minutes=30)
        self.assertEqual(s.course, "CSCE 490")

    def test_streak_counts_consecutive_days(self):
        today = timezone.localdate()
        for i in range(3):
            StudySession.objects.create(course="MATH", minutes=20, date=today - timedelta(days=i))
        StudySession.objects.create(course="MATH", minutes=20, date=today - timedelta(days=5))
        self.assertEqual(current_streak(today), 3)

    def test_streak_survives_until_end_of_today(self):
        yesterday = timezone.localdate() - timedelta(days=1)
        StudySession.objects.create(course="MATH", minutes=20, date=yesterday)
        self.assertEqual(current_streak(), 1)

    def test_add_session_via_form(self):
        r = self.client.post(reverse("tracker:dashboard"), {
            "course": "csce 490", "minutes": 45, "date": timezone.localdate(), "notes": "hw",
        })
        self.assertRedirects(r, reverse("tracker:dashboard"))
        self.assertEqual(StudySession.objects.get().course, "CSCE 490")

    def test_future_date_rejected(self):
        r = self.client.post(reverse("tracker:dashboard"), {
            "course": "X", "minutes": 10, "date": timezone.localdate() + timedelta(days=1),
        })
        self.assertContains(r, "future")
        self.assertEqual(StudySession.objects.count(), 0)

    def test_goal_progress_shows(self):
        WeeklyGoal.objects.create(pk=1, minutes=60)
        StudySession.objects.create(course="X", minutes=60)
        r = self.client.get(reverse("tracker:dashboard"))
        self.assertContains(r, "reached")

    def test_delete_requires_post(self):
        s = StudySession.objects.create(course="X", minutes=10)
        self.assertEqual(self.client.get(reverse("tracker:delete", args=[s.pk])).status_code, 405)
        self.client.post(reverse("tracker:delete", args=[s.pk]))
        self.assertFalse(StudySession.objects.exists())

    def test_csv_export(self):
        StudySession.objects.create(course="X", minutes=10, notes="n")
        r = self.client.get(reverse("tracker:export"))
        self.assertIn("X,10,n", r.content.decode())
