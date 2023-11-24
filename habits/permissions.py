from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    message = "Вы не владелец записи"

    def has_object_permission(self, request, view, obj):
        if request.user == obj.owner:
            return True
        return False


class IsModerator(BasePermission):
    message = "Вы не являетесь модератором"

    def has_permission(self, request, view):
        if request.user.groups.filter(name='Модератор').exists():
            return True
        return False
