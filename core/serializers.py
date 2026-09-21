from datetime import date
from rest_framework import serializers
from .models import Project, Task, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class TaskSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = [
            "id", "project", "title", "description",
            "priority", "status", "due_date", "tags", "created_at",
        ]

    def validate_due_date(self, value):
        # DRF llama automáticamente a validate_<campo> para validar un campo puntual.
        # 'value' ya viene convertido al tipo Python correcto (un objeto date).
        if value and value < date.today():
            raise serializers.ValidationError("La fecha límite no puede ser en el pasado.")
        return value

    def validate(self, data):
        # validate() se ejecuta después de las validaciones individuales, con todos
        # los campos ya limpios en 'data'. Sirve para reglas que cruzan varios campos.
        if data.get("status") == "completada" and not data.get("due_date"):
            raise serializers.ValidationError(
                "No se puede marcar una tarea como completada sin fecha límite registrada."
            )

        # Nueva validación: no se puede pasar una tarea a "en_progreso" si el
        # proyecto todavía no tiene ninguna tarea marcada como "completada".
        if data.get("status") == "en_progreso":
            # El project puede venir en 'data' (creación o cambio de proyecto), o si
            # no vino en este request (ej. un PATCH que solo cambia el status),
            # lo tomamos del proyecto que ya tenía la tarea existente.
            project = data.get("project") or (self.instance.project if self.instance else None)

            if project is not None:
                tiene_completada = project.tasks.filter(status="completada").exists()
                if not tiene_completada:
                    raise serializers.ValidationError(
                        "No se puede poner una tarea en progreso si el proyecto no tiene ninguna tarea completada todavía."
                    )

        return data


class ProjectSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ["id", "name", "description", "tasks", "created_at"]