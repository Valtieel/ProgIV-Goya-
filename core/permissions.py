from rest_framework import permissions

from .services import MembershipService


class IsProjectAdminOrReadOnly(permissions.BasePermission):
    """
    Cualquier miembro del proyecto puede leer.
    Solo un admin del proyecto puede modificar (editar o borrar).
    Sirve tanto para Task (obj.project) como para Project (obj).
    """

    # Solo se ejecuta cuando la vista trabaja sobre un objeto que ya existe
    # (ver, editar o borrar /api/tasks/5/). En un POST de creación NO se llama,
    # por eso la creación se verifica aparte, en perform_create.
    def has_object_permission(self, request, view, obj):
        # Una Task tiene .project; un Project es "su propio" proyecto
        project = obj.project if hasattr(obj, "project") else obj

        # SAFE_METHODS = GET, HEAD y OPTIONS: alcanza con ser miembro
        if request.method in permissions.SAFE_METHODS:
            return MembershipService.is_member(request.user, project)

        # PUT, PATCH, DELETE y el POST de la acción complete: hace falta ser admin
        return MembershipService.is_admin(request.user, project)