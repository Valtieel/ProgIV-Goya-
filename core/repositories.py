from .models import Task


class TaskRepository:
    # @staticmethod: el método no usa self, la clase solo agrupa funciones relacionadas
    @staticmethod
    def get_queryset():
        # select_related / prefetch_related evitan consultas de más (problema N+1)
        # order_by("-created_at"): de la tarea más nueva a la más vieja.
        # Hace falta un orden fijo para que la paginación no mezcle las páginas.
        return (
            Task.objects.select_related("project")
            .prefetch_related("tags")
            .order_by("-created_at")
        )

    @staticmethod
    def get_by_project(project_id):
        return TaskRepository.get_queryset().filter(project_id=project_id)