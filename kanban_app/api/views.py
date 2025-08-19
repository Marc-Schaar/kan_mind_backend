from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response

from kanban_app.models import Boards, Comment, Task, User

from .permissions import (IsCreatorTaskrOrOwnerBoardToDelete, IsLoggedIn,
                          IsMemberToCreate, IsMemberToCreateComment,
                          IsMemberToUpdate, IsOwnerOfCommentToDelete,
                          IsOwnerOrMember, IsOwnerToDelete)
from .serializer import (BoardDetailSerializer, BoardListSerializer,
                         CommentSerializer, TaskDetailSerializer,
                         TaskListSerializer, UserSerializer)


class BoardListView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating boards.

    GET:
        Returns all boards where the current user is a member.

    POST:
        Creates a new board and automatically adds the creator as a member.
    """
    serializer_class = BoardListSerializer
    permission_classes = [IsLoggedIn, IsOwnerOrMember]

    def get_queryset(self):
        user = self.request.user
        return Boards.objects.filter(members=user).order_by("id")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        data = {}

        if serializer.is_valid():
            board = serializer.save(owner_id=self.request.user.id)
            board.members.add(request.user)
            data = {
                "id": board.id,
                "title": board.title,
                "member_count": len(board.members.all()),
                "ticket_count": board.ticket_count,
                "tasks_to_do_count": board.tasks_to_do_count,
                "tasks_high_prio_count": board.tasks_high_prio_count,
                "owner_id": board.owner_id,
            }
            return Response(data, status=status.HTTP_201_CREATED)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update or delete a specific board.

    get:
    Retrieve details of a board.

    put:
    Update all fields of a board.

    patch:
    Partially update fields of a board.

    delete:
    Delete a board (only allowed for the owner).
    """

    queryset = Boards.objects.all()
    serializer_class = BoardDetailSerializer
    permission_classes = [IsOwnerOrMember, IsOwnerToDelete]

    def patch(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)

        if serializer.is_valid():
            board = serializer.save()
            members_data = [
                {"id": user.id,
                 "email": user.email,
                 "fullname": user.username}
                for user in board.members.all()
            ]

            data = serializer.data
            data["members_data"] = members_data
            data.pop("members", None)

            return Response(data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskListView(generics.ListCreateAPIView):
    """
    API endpoint to list all tasks or create a new task.

    get:
    Return a list of all tasks.

    post:
    Create a new task (only members allowed).
    """

    queryset = Task.objects.all()
    serializer_class = TaskListSerializer
    permission_classes = [IsMemberToCreate]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            task = serializer.save(creator_id=self.request.user.id)
            data = {
                "id": task.id,
                "board": task.board.id,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "priority": task.priority,
                "assignee": {
                    "id": task.assignee.id,
                    "email": task.assignee.email,
                    "fullname": task.assignee.username},
                "reviewer": {
                    "id": task.reviewer.id,
                    "email": task.reviewer.email,
                    "fullname": task.reviewer.username},
                "due_date": task.due_date,
                "comments_count": task.comments.count(),
            }
            return Response(data, status=status.HTTP_201_CREATED)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update or delete a specific task.

    get:
    Retrieve task details.

    put:
    Update all task fields.

    patch:
    Partially update task fields.

    delete:
    Delete a task (only creator or board owner allowed).
    """
    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer
    permission_classes = [
        IsLoggedIn,
        IsMemberToUpdate,
        IsCreatorTaskrOrOwnerBoardToDelete,
    ]


class TaskAssignedToMeView(generics.ListAPIView):
    """
    API endpoint to list all tasks assigned to the current user.

    get:
    Return tasks where the current user is the assignee.
    """

    serializer_class = TaskListSerializer

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(assignee=user).order_by("board__id")


class TaskReviewingView(generics.ListAPIView):
    """
    API endpoint to list all tasks currently being reviewed by the user.

    get:
    Return tasks where the current user is the reviewer.
    """
    serializer_class = TaskListSerializer

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(reviewer=user).order_by("board__id")


class CommentOfTasksList(generics.ListCreateAPIView):
    """
    API endpoint to list comments for a task or create a new comment.

    get:
    Return all comments for the specified task, ordered by creation date descending.

    post:
    Create a new comment on the specified task. The author is set to the current user.
    """
    serializer_class = CommentSerializer
    permission_classes = [IsLoggedIn, IsMemberToCreateComment]

    def get_task(self):
        pk = self.kwargs.get("pk")
        return get_object_or_404(Task, pk=pk)

    def get_queryset(self):
        task = self.get_task()
        return task.comments.all().order_by("-created_at")

    def create(self, request, *args, **kwargs):
        task = self.get_task()
        serializer = self.get_serializer(data=request.data)
        data = {}

        if serializer.is_valid():
            comment = serializer.save(
                author=self.request.user, task_id=self.kwargs.get("pk")
            )
            data = {
                "id": comment.id,
                "created_at": comment.created_at,
                "author": comment.author.username,
                "content": comment.content,
            }
            return Response(data, status=status.HTTP_201_CREATED)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentOfTasksListDetail(generics.DestroyAPIView):
    """
    API endpoint to delete a specific comment of a task.

    delete:
    Delete the comment (only allowed for the comment author).
    """

    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOfCommentToDelete]

    def get_queryset(self):
        task_id = self.kwargs["task_id"]
        return Comment.objects.filter(task_id=task_id)


class EmailCheckView(generics.GenericAPIView):
    """
    API endpoint to check if a user with the given email exists.

    get:
    Return the user matching the email query parameter. Returns 404 if not found.
    """
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        email = request.query_params.get("email")
        user = User.objects.filter(email=email).first()
        if not user:
            return Response(
                {"error": "Email nicht gefunden. Die Email existiert nicht."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
