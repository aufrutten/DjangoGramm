from rest_framework import permissions
from ...models import User


class IsOwner(permissions.BasePermission):
    """"""

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False

        list_values = list(view.kwargs.values())
        if list_values:
            profile_id = int(list_values[0])
            return bool(request.user.id == profile_id)

        return bool(request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.parser_context['kwargs'].get('profile'):
            return bool(int(request.parser_context['kwargs'].get('profile')) == int(request.user.id))
        return bool(obj.user.id == request.user.id)
