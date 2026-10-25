import logging

from rest_framework import permissions

from .models import SecurityLog
from .services import MembershipService

# Mismo logger "security" de la vista de login: escribe en security.log
security_logger = logging.getLogger("security")


class IsProjectAdminOrReadOnly(permissions.BasePermission):
    """
    Cualquier miembro del proyecto puede leer.
    Solo un admin del proyecto puede modificar (editar o borrar).
    Sirve tanto para Task (obj.project) como para Project (obj).
    Cada vez que un miembro intenta modificar sin ser admin, queda registrado.
    """

    # Solo se ejecuta cuando la vista trabaja sobre un objeto que ya existe
    # (ver, editar o borrar /api/tasks/5/). En un POST de creación NO se llama.
    def has_object_permission(self, request, view, obj):
        # Una Task tiene .project; un Project es "su propio" proyecto
        project = obj.project if hasattr(obj, "project") else obj

        # SAFE_METHODS = GET, HEAD y OPTIONS: alcanza con ser miembro
        if request.method in permissions.SAFE_METHODS:
            return MembershipService.is_member(request.user, project)

        # PUT, PATCH, DELETE y el POST de la acción complete: hace falta ser admin
        if MembershipService.is_admin(request.user, project):
            return True

        # Llegamos acá solo si es miembro (si no lo fuera, get_queryset ya habría
        # respondido 404) pero no admin: se va a devolver 403, así que lo registramos
        ip = request.META.get("REMOTE_ADDR")
        detalle = f"{request.method} {request.path}"[:255]  # detail admite 255 caracteres
        SecurityLog.objects.create(
            user=request.user, action="permission_denied", detail=detalle, ip_address=ip
        )
        security_logger.warning(
            f"Permiso denegado a {request.user.username}: {detalle} desde {ip}"
        )
        return False