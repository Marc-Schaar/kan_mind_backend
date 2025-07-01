from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS


class IsLoggedIn(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsOwnerOrMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        is_member = obj.members.filter(id=user.id).exists()
        is_owner = (user.id == obj.owner_id)
        return is_member or is_owner


class IsOwnerToDelete(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            if request.user.id == obj.owner_id:
                return True


class IsStaffOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or bool(request.user and request.user.is_staff)


class IsAdminForDeleteOrPatchAndReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        elif request.method in ['DELETE']:
            return bool(request.user and request.user.is_superuser)
        else:
            return bool(request.user and request.user.is_staff)


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        elif request.method in ['DELETE']:
            return bool(request.user and request.user.is_superuser)
        else:
            return bool(request.user and request.user == obj.user)
