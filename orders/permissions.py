from rest_framework import permissions


def get_username(request):
    """Получение id пользователя"""
    if request.user.is_authenticated:
        user_id = request.user.id
        return user_id

class IsOwnerShop(permissions.BasePermission):
    """Правило для владельцев"""
    def has_object_permission(self, request, view, obj):
        obj = Shop.objects.get()
        return bool(request.user == obj.creator)