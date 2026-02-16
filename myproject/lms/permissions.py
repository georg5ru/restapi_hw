from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """Проверка на принадлежность к группе модераторов"""

    def has_permission(self, request, view):
        return request.user.groups.filter(name='moderators').exists()


class ModeratorCanViewAndEditOnly(permissions.BasePermission):
    """
    Модератор может просматривать и редактировать,
    но не может создавать и удалять
    """

    def has_permission(self, request, view):
        # Проверяем, является ли пользователь модератором
        is_moderator = request.user.groups.filter(name='moderators').exists()

        if not is_moderator:
            return False

        # Модератор может только читать и обновлять
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.method == 'PUT' or request.method == 'PATCH':
            return True

        # Создание и удаление запрещено
        return False


class IsModeratorOrOwner(permissions.BasePermission):
    """Модератор или владелец объекта"""

    def has_object_permission(self, request, view, obj):
        # Проверка на модератора
        if request.user.groups.filter(name='moderators').exists():
            # Модератор может читать и редактировать, но не удалять и не создавать
            if request.method in permissions.SAFE_METHODS:
                return True
            if request.method in ['PUT', 'PATCH']:
                return True
            return False

        # Проверка на владельца
        if hasattr(obj, 'owner'):
            return obj.owner == request.user

        return False