from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """Проверка на принадлежность к группе модераторов"""

    def has_permission(self, request, view):
        return request.user.groups.filter(name='moderators').exists()


class IsOwner(permissions.BasePermission):
    """Проверка на владельца объекта"""

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False