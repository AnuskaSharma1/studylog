from django import forms
from django.utils import timezone

from .models import StudySession, WeeklyGoal


class StudySessionForm(forms.ModelForm):
    class Meta:
        model = StudySession
        fields = ["course", "minutes", "date", "notes"]
        widgets = {
            "course": forms.TextInput(attrs={"placeholder": "e.g. CSCE 490", "list": "course-list"}),
            "minutes": forms.NumberInput(attrs={"min": 1, "max": 1440, "placeholder": "45"}),
            "date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.TextInput(attrs={"placeholder": "What did you work on? (optional)"}),
        }

    def clean_date(self):
        date = self.cleaned_data["date"]
        if date > timezone.localdate():
            raise forms.ValidationError("You can't log a session in the future.")
        return date


class WeeklyGoalForm(forms.ModelForm):
    class Meta:
        model = WeeklyGoal
        fields = ["minutes"]
        labels = {"minutes": "Weekly goal (minutes)"}
        widgets = {"minutes": forms.NumberInput(attrs={"min": 1})}
