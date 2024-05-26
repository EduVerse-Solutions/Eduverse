from rest_framework import permissions

ADMINS = ["Admin", "Super Admin"]


class IsSuperAdminOrAdmin(permissions.BasePermission):
    """
    Custom permission class that allows access to super admins and admins.
    """

    def has_permission(self, request, view):
        """
        Check if the user has permission to access the view.

        Args:
            request (HttpRequest): The request object.
            view (View): The view object.

        Returns:
            bool: True if the user has permission, False otherwise.
        """
        user = request.user
        if user.is_authenticated:

            if user.is_superuser or user.role in ADMINS:
                return True

            if (
                request.method in permissions.SAFE_METHODS
                and user.role in ADMINS
            ):
                return True


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to edit it.
    """

    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to perform the requested action on the object.

        Args:
            request (HttpRequest): The request object.
            view (View): The view object.
            obj (Any): The object being accessed.

        Returns:
            bool: True if the user has permission, False otherwise.
        """
        if (
            request.method in permissions.SAFE_METHODS
            and request.user.role in ADMINS
        ):
            return True

        if request.user.is_authenticated:
            return obj.id == request.user.id or request.user.role in ADMINS


class IsPartOfInstitution(permissions.BasePermission):
    """
    Custom permission to only allow users that are part of an institution to
    access the view.
    """

    def has_permission(self, request, view):
        """
        Check if the user has permission to access the view.

        Args:
            request (HttpRequest): The request object.
            view (View): The view object.

        Returns:
            bool: True if the user has permission, False otherwise.
        """
        user = request.user
        if user.is_superuser or (user.is_authenticated and user.institution):
            return True

        return False
