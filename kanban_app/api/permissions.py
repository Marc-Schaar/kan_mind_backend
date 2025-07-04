from rest_framework.permissions import SAFE_METHODS, BasePermission

from kanban_app.models import Boards


class IsLoggedIn(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsOwnerOrMember(BasePermission):
    """
    Object-level permission to allow access only to board owners or members.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        is_member = obj.members.filter(id=user.id).exists()
        is_owner = user.id == obj.owner_id
        return is_member or is_owner


class IsOwnerToDelete(BasePermission):
    """
    Allow DELETE only for owners of the board.
    Allow all other methods.
    """

    def has_object_permission(self, request, view, obj):
        if request.method == "DELETE":
            is_owner = request.user.id == obj.owner_id
            return is_owner
        return True


class IsMemberToCreate(BasePermission):
    """
    Allow POST only if user is a member of the board specified in the request data.
    """

    def has_permission(self, request, view):
        if request.method == "POST":
            user = request.user
            board_id = request.data.get("board")

            exists = Boards.objects.filter(
                id=board_id, members__id=user.id).exists()
            return exists
        return True


class IsMemberToUpdate(BasePermission):
    """
    Allow PUT/PATCH only if user is a member of the board specified in the request data.
    """

    def has_permission(self, request, view):
        if request.method == "PATCH" or request.method == "PUT":
            user = request.user
            board_id = request.data.get("board")

            exists = Boards.objects.filter(
                id=board_id, members__id=user.id).exists()
            return exists
        return True


class IsCreatorTaskrOrOwnerBoardToDelete(BasePermission):
    """
    Allow DELETE only if user is the task creator or the owner of the board the task belongs to.
    Allow other methods for everyone.
    """

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
            task_id = view.kwargs.get("pk")

            if not task_id:
                return False  # kein Task vorhanden

            return Boards.objects.filter(
                tasks__id=task_id,
                members__id=user.id
            ).exists()

        return True


class IsOwnerOfCommentToDelete(BasePermission):
    """
    Allow DELETE on comments only if the requesting user is the author.
    Allow all other methods.
    """

    def has_object_permission(self, request, view, obj):
        if request.method == "DELETE":
            user = request.user
            is_owner = obj.author_id == user.id
            return is_owner
        return True
