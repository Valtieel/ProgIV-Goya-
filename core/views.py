from django.http import JsonResponse
from rest_framework import viewsets
from .models import Project, Task
from .serializers import ProjectSerializer, TaskSerializer


def health_check(request):
    return JsonResponse({"status": "ok", "service": "TaskFlow API"})


def health_version(request):
    return JsonResponse({"version": "0.1.0"})


class ProjectViewSet(viewsets.ModelViewSet):
    # ModelViewSet ya resuelve solo las 6 acciones del CRUD:
    # list, create, retrieve, update, partial_update, destroy
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.select_related("project").prefetch_related("tags").all()
    serializer_class = TaskSerializer