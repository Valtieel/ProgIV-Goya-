from django.db import models

class Project(models.Model):
    # Un proyecto agrupa varias tareas (relación uno a muchos con Task)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)  # texto largo, puede quedar vacío
    created_at = models.DateTimeField(auto_now_add=True)  # se completa sola al crear

    def __str__(self):
        return self.name


class Tag(models.Model):
    # Etiqueta reutilizable entre varias tareas (ej: "urgente", "backend")
    name = models.CharField(max_length=50, unique=True)  # no puede haber dos tags iguales

    def __str__(self):
        return self.name


class Task(models.Model):
    PRIORITY_CHOICES = [("baja", "Baja"), ("media", "Media"), ("alta", "Alta")]
    STATUS_CHOICES = [
        ("pendiente", "Pendiente"),
        ("en_progreso", "En progreso"),
        ("completada", "Completada"),
    ]

    # ForeignKey = relación "muchos a uno": muchas tareas pueden pertenecer a un mismo proyecto.
    # on_delete=CASCADE: si se borra el proyecto, se borran también sus tareas.
    # related_name="tasks": permite hacer mi_proyecto.tasks.all() para ir "hacia atrás"
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="media")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="pendiente")
    due_date = models.DateField(null=True, blank=True)  # fecha límite, opcional

    # ManyToManyField: una tarea puede tener varios tags, y un tag estar en varias tareas.
    # Django crea automáticamente una tabla intermedia por detrás para esta relación.
    tags = models.ManyToManyField(Tag, blank=True, related_name="tasks")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.project.name})"