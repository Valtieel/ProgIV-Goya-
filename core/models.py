from django.conf import settings
from django.db import models


class Project(models.Model):
    # Un proyecto agrupa varias tareas (relación uno a muchos con Task)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)  # texto largo, puede quedar vacío
    created_at = models.DateTimeField(auto_now_add=True)  # se completa sola al crear

    def __str__(self):
        return self.name


class ProjectMembership(models.Model):
    # Une a un usuario con un proyecto y le da un rol dentro de ese proyecto.
    # Así una misma persona puede ser admin en un proyecto y miembro en otro.
    ROLE_CHOICES = [("admin", "Administrador"), ("miembro", "Miembro")]

    # "Project" entre comillas: Django lo resuelve al final, sin importar el orden del archivo
    project = models.ForeignKey("Project", on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Por mínimo privilegio, el rol por defecto es "miembro" y no "admin"
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="miembro")

    class Meta:
        # La base de datos impide que un usuario tenga dos membresías en el mismo proyecto
        unique_together = ("project", "user")

    def __str__(self):
        return f"{self.user} - {self.project} ({self.role})"


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

    # Quién creó la tarea. Con las membresías ya no da acceso, queda como registro.
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tasks", null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.project.name})"


class SecurityLog(models.Model):
    # Registro de auditoría: guarda eventos sensibles (logins fallidos, accesos denegados).
    # SET_NULL: si se borra el usuario, el registro queda pero con user vacío.
    # No queremos perder el historial de seguridad porque se eliminó una cuenta.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    action = models.CharField(max_length=100)  # ej: "login_failed", "permission_denied"
    detail = models.CharField(max_length=255, blank=True)  # información extra en texto libre
    ip_address = models.GenericIPAddressField(null=True, blank=True)  # valida que sea una IP
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.created_at:%Y-%m-%d %H:%M} {self.action} ({self.ip_address})"