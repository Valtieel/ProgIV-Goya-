from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Project, Task
from .serializers import ProjectSerializer, TaskSerializer


def health_check(request):
    return JsonResponse({"status": "ok", "service": "TaskFlow API"})


def health_version(request):
    return JsonResponse({"version": "0.1.0"})


@api_view(["GET"])  # el decorador restringe esta vista a solo aceptar GET
def project_list(request):
    projects = Project.objects.all()
    # many=True porque estamos serializando varios objetos, no uno solo
    serializer = ProjectSerializer(projects, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def task_list(request):
    # select_related trae el project relacionado en la misma consulta SQL (evita N+1)
    # prefetch_related hace lo mismo pero para la relación muchos-a-muchos con tags
    tasks = Task.objects.select_related("project").prefetch_related("tags").all()
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)

@api_view(["GET"])
def project_detail(request, project_id):
    # get_object_or_404 busca el objeto por su id; si no existe, devuelve automáticamente un 404
    # en vez de que el código explote con una excepción sin manejar
    project = get_object_or_404(Project, id=project_id)
    serializer = ProjectSerializer(project)  # sin many=True porque es un solo objeto
    return Response(serializer.data)