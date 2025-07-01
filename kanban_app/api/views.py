
from rest_framework import generics, status
from rest_framework.response import Response
from kanban_app.models import Boards, Task, Comment, User
from .serializer import BoardListSerializer, BoardDetailSerializer, TaskListSerializer, TaskDetailSerializer, CommentSerializer, UserSerializer
from .permissions import IsLoggedIn, IsOwnerOrMember, IsOwnerToDelete, IsMemberToCreate, IsMemberToUpdate, IsCreatorTaskrOrOwnerBoardToDelete, IsMemberToCreateComment, IsOwnerOfCommentToDelete
from django.shortcuts import get_object_or_404


class BoardListView(generics.ListCreateAPIView):
    serializer_class = BoardListSerializer
    permission_classes = [IsLoggedIn, IsOwnerOrMember]

    def get_queryset(self):
        user = self.request.user
        return Boards.objects.filter(members=user).order_by('id')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        data = {}

        if serializer.is_valid():
            board = serializer.save(owner_id=self.request.user.id)
            board.members.add(request.user)
            data = {
                'id': board.id,
                'title': board.title,
                'member_count': len(board.members.all()),
                'ticket_count': board.ticket_count,
                'tasks_to_do_count': board.tasks_to_do_count,
                'tasks_high_prio_count': board.tasks_high_prio_count,
                'owner_id': board.owner_id,
            }
            return Response(data, status=status.HTTP_201_CREATED)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Boards.objects.all()
    serializer_class = BoardDetailSerializer
    permission_classes = [IsOwnerOrMember, IsOwnerToDelete]


class TaskListView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskListSerializer
    permission_classes = [IsMemberToCreate]


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer
    permission_classes = [IsLoggedIn, IsMemberToUpdate,
                          IsCreatorTaskrOrOwnerBoardToDelete]


class TaskAssignedToMeView(generics.ListAPIView):
    serializer_class = TaskListSerializer

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(assignee=user).order_by('board__id')


class TaskReviewingView(generics.ListAPIView):
    serializer_class = TaskListSerializer

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(reviewer=user).order_by('board__id')


class CommentOfTasksList(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsMemberToCreateComment]

    def get_task(self):
        pk = self.kwargs.get('pk')
        return get_object_or_404(Task, pk=pk)

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        task = Task.objects.get(pk=pk)
        return task.comments.all().order_by('-created_at')

    def create(self, request, *args, **kwargs):
        task = self.get_task()
        serializer = self.get_serializer(data=request.data)
        data = {}

        if serializer.is_valid():
            comment = serializer.save(
                author=self.request.user, task_id=self.kwargs.get('pk'))
            data = {
                'id': comment.id,
                'created_at': comment.created_at,
                'author': comment.author.id,
                'content': comment.content,

            }
            return Response(data, status=status.HTTP_201_CREATED)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentOfTasksListDetail(generics.DestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOfCommentToDelete]

    def get_queryset(self):
        task_id = self.kwargs['task_id']
        return Comment.objects.filter(task_id=task_id)


class EmailCheckView(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        email = self.request.query_params.get('email', None)
        return User.objects.filter(email=email)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        if not queryset:
            return Response({"error": " Email nicht gefunden. Die Email exestiert nicht."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.data, status=status.HTTP_200_OK)
