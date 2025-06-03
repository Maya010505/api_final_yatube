from rest_framework import permissions


class OwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if not hasattr(obj, 'author'):
            raise AttributeError(
                f"Объект типа {type(obj)} не имеет атрибута 'author', "
                "необходимого для проверки прав доступа"
            )

        return obj.author == request.user
