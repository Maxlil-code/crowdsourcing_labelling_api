from rest_framework import  permissions

class IsContributor(permissions.BasePermission):
    """
    Acces reservé au utilisateur ayant le role 'contributor'.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'contributor'
    
class IsValidator(permissions.BasePermission):
    """
    Acces reservé au utilisateur ayant le role 'validator'.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'validator'


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Acces en lecture pour tous les utilisateurs authentifiés.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_authenticated and request.user.role == 'admin'