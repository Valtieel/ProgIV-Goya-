from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Project
from .repositories import TaskRepository
from .serializers import ProjectSerializer, TaskSerializer
from .services import ProjectService, TaskService


def health_check(request):
    return JsonResponse({"status": "ok", "service": "TaskFlow API"})


def health_version(request):
    return JsonResponse({"version": "0.1.0"})


class ProjectViewSet(viewsets.ModelViewSet):
    # order_by("id") para que la paginación tenga un orden estable
    queryset = Project.objects.all().order_by("id")
    serializer_class = ProjectSerializer

    # detail=True: opera sobre un proyecto puntual -> GET /api/projects/<id>/summary/
    @action(detail=True, methods=["get"])
    def summary(self, request, pk=None):
        project = self.get_object()  # devuelve 404 si el proyecto no existe
        resumen = ProjectService.project_summary(project)
        return Response(resumen)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = TaskRepository.get_queryset()
    serializer_class = TaskSerializer

    # Filtros exactos, orden y búsqueda parcial (lista blanca de campos permitidos)
    filterset_fields = ["status", "priority", "project"]
    ordering_fields = ["due_date", "created_at", "priority"]
    search_fields = ["title", "description"]

    # detail=True: opera sobre una tarea puntual -> POST /api/tasks/<id>/complete/
    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        task = self.get_object()
        TaskService.mark_completed(task)
        return Response(self.get_serializer(task).data)

    # detail=False: opera sobre la colección -> GET /api/tasks/overdue/
    @action(detail=False, methods=["get"])
    def overdue(self, request):
        tasks = TaskService.tasks_overdue(self.get_queryset())
        # Las @action manuales no paginan solas, así que lo hacemos a mano
        page = self.paginate_queryset(tasks)
        if page is not None:
            return self.get_paginated_response(self.get_serializer(page, many=True).data)
        return Response(self.get_serializer(tasks, many=True).data)