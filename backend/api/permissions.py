from rest_framework import permissions


class IsSubscribed(permissions.BasePermission):
    """Разрешает только подписчикам."""

    def has_permission(self, request, view):
        return view.action == 'subscribe'
