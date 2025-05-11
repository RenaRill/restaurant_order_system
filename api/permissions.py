from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class IsWaiter(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and getattr(request.user, 'is_waiter', False)


class IsKitchen(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and getattr(request.user, 'is_kitchen', False)


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS
