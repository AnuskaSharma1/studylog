from datetime import timedelta

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class StudySession(models.Model):
    """One block of time the user spent studying a course."""

    course = models.CharField(max_length=60)
    minutes = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(24 * 60)]
    )
    date = models.DateField(default=timezone.localdate)
    notes = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.course}: {self.minutes} min on {self.date}"

    def save(self, *args, **kwargs):
        # Normalize course names so "csce 490" and "CSCE 490 " group together.
        self.course = " ".join(self.course.split()).upper()
        super().save(*args, **kwargs)


class WeeklyGoal(models.Model):
    """Single-row table holding the user's weekly study goal in minutes."""

    minutes = models.PositiveIntegerField(default=600, validators=[MinValueValidator(1)])

    @classmethod
    def get(cls):
        goal, _ = cls.objects.get_or_create(pk=1)
        return goal


def current_streak(today=None):
    """Number of consecutive days (ending today or yesterday) with at least one session."""
    today = today or timezone.localdate()
    days = set(StudySession.objects.values_list("date", flat=True))
    day = today if today in days else today - timedelta(days=1)
    streak = 0
    while day in days:
        streak += 1
        day -= timedelta(days=1)
    return streak
