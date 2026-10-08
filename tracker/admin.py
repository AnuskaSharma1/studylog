from django.contrib import admin

from .models import StudySession, WeeklyGoal


@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    list_display = ("date", "course", "minutes", "notes")
    list_filter = ("course", "date")
    search_fields = ("course", "notes")


admin.site.register(WeeklyGoal)
