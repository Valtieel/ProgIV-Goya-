from django.urls import path
from . import views

urlpatterns = [
    path("health/", views.health_check, name="health_check"),
    path("health/version/", views.health_version, name="health_version"),
    path("projects/", views.project_list, name="project_list"),
    path("tasks/", views.task_list, name="task_list"),
    path("projects/<int:project_id>/", views.project_detail, name="project_detail"),
]