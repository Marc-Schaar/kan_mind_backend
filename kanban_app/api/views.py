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
                    "assignee": task.assignee.id,
                    "reviewer": task.reviewer.id,
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
    permission_classes = [IsMemberToCreateComment]

    def get_task(self):
        pk = self.kwargs.get("pk")
        return get_object_or_404(Task, pk=pk)

    def get_queryset(self):
        pk = self.kwargs.get("pk")
        task = Task.objects.get(pk=pk)
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
                "author": comment.author.id,
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


class EmailCheckView(generics.ListAPIView):
    """
    API endpoint to check if a user with the given email exists.

    get:
    Return the user(s) matching the email query parameter. Returns 404 if none found.
    """
    serializer_class = UserSerializer

    def get_queryset(self):
        email = self.request.query_params.get("email", None)
        return User.objects.filter(email=email)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        if not queryset:
            return Response(
                {"error": " Email nicht gefunden. Die Email exestiert nicht."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(serializer.data, status=status.HTTP_200_OK)
