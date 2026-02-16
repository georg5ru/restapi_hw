from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """Проверка на принадлежность к группе модераторов"""

    def has_permission(self, request, view):
        return request.user.groups.filter(name='moderators').exists()


class IsOwnerOrModerator(permissions.BasePermission):
    """Владелец объекта или модератор"""

    def has_object_permission(self, request, view, obj):
        # Проверка на модератора
        if request.user.groups.filter(name='moderators').exists():
            return True

        # Проверка на владельца
        if hasattr(obj, 'owner'):
            return obj.owner == request.user

        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Владелец может редактировать, остальные только читать"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if hasattr(obj, 'owner'):
            return obj.owner == request.user

        return False