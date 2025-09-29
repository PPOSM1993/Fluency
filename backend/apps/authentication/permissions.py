from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Permite acceso solo al dueño del objeto.
    Ejemplo: ver o editar su propio perfil.
    """
    def has_object_permission(self, request, view, obj):
        return obj == request.user or getattr(obj, 'user', None) == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Acceso total para admins. Solo lectura para el resto.
    Ideal para recursos públicos modificables solo por admin.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.is_staff


class HasActiveMembership(permissions.BasePermission):
    """
    Permite acceso solo a usuarios con una membresía activa.
    Requiere que el modelo User tenga relación con un modelo Membership con is_active.
    """
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and hasattr(user, 'membership') and user.membership.is_active


class IsSupportAgent(permissions.BasePermission):
    """
    Permite acceso solo a usuarios con rol 'support'.
    Requiere que el modelo User tenga un campo 'role'.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, 'role', None) == 'support'


class IsVerifiedUser(permissions.BasePermission):
    """
    Permite acceso solo a usuarios verificados.
    Ideal para confirmar identidad o verificación de email.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, 'is_verified', False)


class HasRole(permissions.BasePermission):
    """
    Permite acceso a uno o más roles específicos.
    Ejemplo de uso: HasRolePermission('admin', 'staff')
    """

    def __init__(self, *allowed_roles):
        self.allowed_roles = allowed_roles

    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, 'role', None) in self.allowed_roles


# Ejemplo dinámico: definir desde la vista
# permission_classes = [HasRole('admin', 'staff')]