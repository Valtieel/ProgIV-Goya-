from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# El router genera automáticamente todas las URLs del CRUD (list, detail, etc.)
# para cada ViewSet que registremos, sin escribirlas una por una a mano.
router = DefaultRouter()
router.register(r"projects", views.ProjectViewSet, basename="project")
router.register(r"tasks", views.TaskViewSet, basename="task")

urlpatterns = [
    path("health/", views.health_check, name="health_check"),
    path("health/version/", views.health_version, name="health_version"),
    path("", include(router.urls)),
]