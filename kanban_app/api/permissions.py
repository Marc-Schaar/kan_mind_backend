from rest_framework.permissions import SAFE_METHODS, BasePermission

from kanban_app.models import Boards


class IsLoggedIn(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsOwnerOrMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        is_member = obj.members.filter(id=user.id).exists()
        is_owner = user.id == obj.owner_id
        return is_member or is_owner


class IsOwnerToDelete(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == "DELETE":
            is_owner = request.user.id == obj.owner_id
            return is_owner
        return True


class IsMemberToCreate(BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            user = request.user
            board_id = request.data.get("board")

            exists = Boards.objects.filter(id=board_id, members__id=user.id).exists()
            return exists
        return True


class IsMemberToUpdate(BasePermission):
    def has_permission(self, request, view):
        if request.method == "PATCH" or request.method == "PUT":
            user = request.user
            board_id = request.data.get("board")

            exists = Boards.objects.filter(id=board_id, members__id=user.id).exists()
            return exists
        return True


class IsCreatorTaskrOrOwnerBoardToDelete(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == "DELETE":
            user = request.user
            is_creator = obj.creator_id == user.id
            is_owner = obj.board.owner_id == user.id
            return is_creator or is_owner
        return True


class IsMemberToCreateComment(BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            user = request.user
            task_id = request.data.get("task")

            exists = Boards.objects.filter(
                tasks__id=task_id, members__id=user.id
            ).exists()
            return exists
        return True


class IsOwnerOfCommentToDelete(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == "DELETE":
            user = request.user
            is_owner = obj.author_id == user.id
            return is_owner
        return True
