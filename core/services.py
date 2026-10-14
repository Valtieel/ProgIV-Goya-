import requests
from django.core.cache import cache
from django.db.models import Count
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import Task
from .repositories import TaskRepository


class TaskService:
    @staticmethod
    def mark_completed(task: Task) -> Task:
        # Misma regla de negocio que TaskSerializer.validate (Clase 4)
        # La repetimos acá porque la acción "complete" no pasa por el serializer
        if not task.due_date:
            raise ValidationError(
                "No se puede marcar una tarea como completada sin fecha límite registrada."
            )
        task.status = "completada"
        task.save(update_fields=["status"])  # actualiza solo la columna status
        return task

    @staticmethod
    def tasks_overdue(queryset=None):
        # Si no nos pasan un queryset, partimos de todas las tareas
        if queryset is None:
            queryset = TaskRepository.get_queryset()
        today = timezone.now().date()
        # due_date__lt = "menor que hoy"; excluimos las que ya están completadas
        return queryset.filter(due_date__lt=today).exclude(status="completada")


class ProjectService:
    @staticmethod
    def project_summary(project) -> dict:
        # Una sola consulta: agrupa las tareas del proyecto por status y cuenta cada grupo
        # Devuelve algo como [{"status": "pendiente", "total": 2}, ...]
        filas = project.tasks.values("status").annotate(total=Count("id"))

        # Arrancamos con los tres estados en 0, así el resultado siempre
        # los incluye aunque el proyecto no tenga tareas en alguno de ellos
        resumen = {"pendiente": 0, "en_progreso": 0, "completada": 0}

        # Pisamos los ceros con los totales reales que devolvió la consulta
        for fila in filas:
            resumen[fila["status"]] = fila["total"]

        return resumen


class HolidayService:
    API_URL = "https://date.nager.at/api/v3/PublicHolidays/{year}/AR"

    @classmethod
    def get_holidays(cls, year: int) -> list[str]:
        cache_key = f"holidays_{year}"
        cached = cache.get(cache_key)
        # Si ya está en la caché (aunque sea lista vacía), la usamos y no vamos a la red
        if cached is not None:
            return cached

        try:
            # timeout=5: si la API externa no responde, nos rendimos a los 5 segundos
            response = requests.get(cls.API_URL.format(year=year), timeout=5)
            response.raise_for_status()  # lanza excepción si el estado es 4xx/5xx
            dates = [item["date"] for item in response.json()]
            cache.set(cache_key, dates, timeout=60 * 60 * 24)  # 24 horas
        except (requests.RequestException, ValueError, KeyError):
            # Si falla, devolvemos lista vacía y la guardamos solo 5 minutos
            dates = []
            cache.set(cache_key, dates, timeout=60 * 5)

        return dates

    @classmethod
    def is_holiday(cls, some_date) -> bool:
        return str(some_date) in cls.get_holidays(some_date.year)