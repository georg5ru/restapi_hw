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


class IsModeratorOrOwner(permissions.BasePermission):
    """
    Модератор ИЛИ владелец.
    Модератор может только читать и редактировать (но не создавать/удалять).
    Владелец может всё.
    """

    def has_object_permission(self, request, view, obj):
        is_moderator = request.user.groups.filter(name='moderators').exists()

        # Модератор может только читать и редактировать
        if is_moderator:
            return request.method in permissions.SAFE_METHODS or \
                request.method in ['PUT', 'PATCH']

        # Владелец может всё
        if hasattr(obj, 'owner'):
            return obj.owner == request.user

        return False