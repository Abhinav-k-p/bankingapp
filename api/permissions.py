from rest_framework import permissions

class IsAdminOrStaffUser(permissions.BasePermission):
    """
    Custom permission to only allow admin and staff users to access the view.
    """
    def has_permission(self, request, view):
        return request.user and (request.user.is_staff or request.user.is_superuser)

class IsCustomerUser(permissions.BasePermission):
    """
    Custom permission to only allow customer users to access the view.
    """
    def has_permission(self, request, view):
        return request.user and not (request.user.is_staff or request.user.is_superuser)
    