from django.urls import path

from . import views

app_name = "tracker"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("session/<int:pk>/edit/", views.edit_session, name="edit"),
    path("session/<int:pk>/delete/", views.delete_session, name="delete"),
    path("course/<str:course>/", views.course_detail, name="course"),
    path("goal/", views.update_goal, name="goal"),
    path("export.csv", views.export_csv, name="export"),
]
