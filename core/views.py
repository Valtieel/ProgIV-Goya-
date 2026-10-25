from django.contrib.auth.models import User
from django.db import transaction
from django.http import JsonResponse
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Project, ProjectMembership
from .permissions import IsProjectAdminOrReadOnly
from .repositories import TaskRepository
from .serializers import ProjectSerializer, TaskSerializer
from .serializers_auth import RegisterSerializer
from .services import MembershipService, ProjectService, TaskService


def health_check(request):
    return JsonResponse({"status": "ok", "service": "TaskFlow API"})


def health_version(request):
    return JsonResponse({"version": "0.1.0"})


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by("id")
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsProjectAdminOrReadOnly]

    def get_queryset(self):
        # Visibilidad: cada usuario ve solo los proyectos donde es miembro.
        # Si pide uno ajeno por id, responde 404 (ni siquiera confirmamos que existe).
        return MembershipService.projects_for(self.request.user)

    def perform_create(self, serializer):
        # Quien crea el proyecto queda como su admin.
        # transaction.atomic: se guardan las dos cosas o ninguna, así nunca
        # queda un proyecto huérfano sin admin.
        with transaction.atomic():
            project = serializer.save()
            ProjectMembership.objects.create(
                project=project, user=self.request.user, role="admin"
            )

    # detail=True: opera sobre un proyecto puntual -> GET /api/projects/<id>/summary/
    @action(detail=True, methods=["get"])
    def summary(self, request, pk=None):
        project = self.get_object()  # 404 si no existe o no es miembro
        resumen = ProjectService.project_summary(project)
        return Response(resumen)

    # POST /api/projects/<id>/add_member/  con {"username": "...", "role": "miembro"}
    @action(detail=True, methods=["post"])
    def add_member(self, request, pk=None):
        # get_object() ya verifica el permiso: como es un POST, exige ser admin del
        # proyecto (403 si es miembro, 404 si ni siquiera es miembro).
        project = self.get_object()

        username = request.data.get("username")
        role = request.data.get("role", "miembro")  # por mínimo privilegio, miembro por defecto

        if not username:
            raise ValidationError({"username": "Este campo es obligatorio."})
        if role not in ("admin", "miembro"):
            raise ValidationError({"role": "El rol tiene que ser 'admin' o 'miembro'."})

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise NotFound("No existe un usuario con ese username.")

        if MembershipService.is_member(user, project):
            raise ValidationError("Ese usuario ya es miembro del proyecto.")

        membership = ProjectMembership.objects.create(project=project, user=user, role=role)
        return Response(
            {"project": project.id, "user": user.username, "role": membership.role},
            status=status.HTTP_201_CREATED,
        )


class TaskViewSet(viewsets.ModelViewSet):
    queryset = TaskRepository.get_queryset()
    serializer_class = TaskSerializer

    # Filtros exactos, orden y búsqueda parcial (lista blanca de campos permitidos)
    filterset_fields = ["status", "priority", "project"]
    ordering_fields = ["due_date", "created_at", "priority"]
    search_fields = ["title", "description"]

    # Dos capas: IsAuthenticated (¿está logueado?) y IsProjectAdminOrReadOnly (¿qué puede hacer?)
    permission_classes = [IsAuthenticated, IsProjectAdminOrReadOnly]

    def get_queryset(self):
        # Visibilidad: tareas de los proyectos donde el usuario es miembro.
        # project__memberships__user atraviesa las relaciones con doble guion bajo.
        # distinct() evita filas repetidas que puede generar el JOIN.
        return super().get_queryset().filter(
            project__memberships__user=self.request.user
        ).distinct()

    def check_project_admin(self, project):
        # Ayudante: corta con 403 si el usuario no es admin de ese proyecto
        if not MembershipService.is_admin(self.request.user, project):
            raise PermissionDenied("Solo un admin del proyecto puede crear o mover tareas en él.")

    def perform_create(self, serializer):
        # En un POST todavía no existe el objeto, así que has_object_permission
        # no se ejecuta: el rol hay que verificarlo acá a mano.
        self.check_project_admin(serializer.validated_data["project"])
        # owner queda como registro de quién creó la tarea (ya no da acceso)
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        # Caso sutil: un admin del proyecto A podría mandar {"project": B} para
        # "mudar" la tarea a un proyecto donde no es admin. Lo verificamos.
        if "project" in serializer.validated_data:
            self.check_project_admin(serializer.validated_data["project"])
        serializer.save()

    # detail=True: opera sobre una tarea puntual -> POST /api/tasks/<id>/complete/
    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        # get_object() ejecuta has_object_permission: como es POST, exige ser admin
        task = self.get_object()
        TaskService.mark_completed(task)
        return Response(self.get_serializer(task).data)

    # detail=False: opera sobre la colección -> GET /api/tasks/overdue/
    @action(detail=False, methods=["get"])
    def overdue(self, request):
        tasks = TaskService.tasks_overdue(self.get_queryset())
        page = self.paginate_queryset(tasks)
        if page is not None:
            return self.get_paginated_response(self.get_serializer(page, many=True).data)
        return Response(self.get_serializer(tasks, many=True).data)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    # AllowAny pisa el IsAuthenticated global: para registrarse todavía no hay login
    permission_classes = [permissions.AllowAny]