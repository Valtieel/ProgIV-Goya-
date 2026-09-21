from rest_framework import serializers
from .models import Project, Task, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]  # exponemos solo estos dos campos en el JSON


class TaskSerializer(serializers.ModelSerializer):
    # Sobreescribimos el campo automático de "tags" para que devuelva el objeto
    # completo serializado (id + name), en vez de solo una lista de IDs.
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = [
            "id", "project", "title", "description",
            "priority", "status", "due_date", "tags", "created_at",
        ]


class ProjectSerializer(serializers.ModelSerializer):
    # Anidamos las tareas del proyecto: cada proyecto va a traer su lista completa de tasks
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ["id", "name", "description", "tasks", "created_at"]