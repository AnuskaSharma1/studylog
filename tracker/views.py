import csv
from datetime import timedelta

from django.contrib import messages
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import StudySessionForm, WeeklyGoalForm
from .models import StudySession, WeeklyGoal, current_streak


def fmt_minutes(total):
    hours, mins = divmod(total or 0, 60)
    return f"{hours}h {mins}m" if hours else f"{mins}m"


def last_7_days():
    """Minutes studied on each of the last 7 days, oldest first, scaled for a bar chart."""
    today = timezone.localdate()
    start = today - timedelta(days=6)
    totals = dict(
        StudySession.objects.filter(date__gte=start)
        .values_list("date")
        .annotate(total=Sum("minutes"))
    )
    days = [(start + timedelta(days=i)) for i in range(7)]
    peak = max([totals.get(d, 0) for d in days] + [1])
    return [
        {
            "label": d.strftime("%a"),
            "minutes": totals.get(d, 0),
            "pct": round(100 * totals.get(d, 0) / peak),
        }
        for d in days
    ]


def dashboard(request):
    if request.method == "POST":
        form = StudySessionForm(request.POST)
        if form.is_valid():
            s = form.save()
            messages.success(request, f"Logged {s.minutes} minutes of {s.course}.")
            return redirect("tracker:dashboard")
    else:
        form = StudySessionForm()

    today = timezone.localdate()
    week_start = today - timedelta(days=today.weekday())  # Monday
    week_total = (
        StudySession.objects.filter(date__gte=week_start).aggregate(t=Sum("minutes"))["t"] or 0
    )
    goal = WeeklyGoal.get()
    by_course = (
        StudySession.objects.values("course")
        .annotate(total=Sum("minutes"), count=Count("id"))
        .order_by("-total")
    )
    grand_total = sum(c["total"] for c in by_course) or 1
    for c in by_course:
        c["pretty"] = fmt_minutes(c["total"])
        c["pct"] = round(100 * c["total"] / grand_total)

    context = {
        "form": form,
        "goal_form": WeeklyGoalForm(instance=goal),
        "sessions": StudySession.objects.all()[:15],
        "courses": by_course,
        "known_courses": [c["course"] for c in by_course],
        "week_total": fmt_minutes(week_total),
        "goal": fmt_minutes(goal.minutes),
        "goal_pct": min(100, round(100 * week_total / goal.minutes)),
        "goal_met": week_total >= goal.minutes,
        "remaining": fmt_minutes(max(0, goal.minutes - week_total)),
        "streak": current_streak(today),
        "chart": last_7_days(),
    }
    return render(request, "tracker/dashboard.html", context)


def edit_session(request, pk):
    session = get_object_or_404(StudySession, pk=pk)
    form = StudySessionForm(request.POST or None, instance=session)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Session updated.")
        return redirect("tracker:dashboard")
    return render(request, "tracker/edit.html", {"form": form, "session": session})


@require_POST
def delete_session(request, pk):
    session = get_object_or_404(StudySession, pk=pk)
    session.delete()
    messages.info(request, "Session deleted.")
    return redirect("tracker:dashboard")


def course_detail(request, course):
    sessions = StudySession.objects.filter(course=course.upper())
    stats = sessions.aggregate(total=Sum("minutes"), count=Count("id"))
    avg = (stats["total"] or 0) // (stats["count"] or 1)
    return render(
        request,
        "tracker/course.html",
        {
            "course": course.upper(),
            "sessions": sessions,
            "total": fmt_minutes(stats["total"]),
            "count": stats["count"],
            "avg": fmt_minutes(avg),
        },
    )


@require_POST
def update_goal(request):
    form = WeeklyGoalForm(request.POST, instance=WeeklyGoal.get())
    if form.is_valid():
        form.save()
        messages.success(request, "Weekly goal updated.")
    else:
        messages.error(request, "Goal must be a positive number of minutes.")
    return redirect("tracker:dashboard")


def export_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="study_sessions.csv"'
    writer = csv.writer(response)
    writer.writerow(["date", "course", "minutes", "notes"])
    for s in StudySession.objects.order_by("date"):
        writer.writerow([s.date, s.course, s.minutes, s.notes])
    return response
