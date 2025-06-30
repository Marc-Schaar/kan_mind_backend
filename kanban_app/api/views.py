
from rest_framework import generics
from kanban_app.models import Boards, Task, Comment
from .serializer import BoardListSerializer, BoardDetailSerializer, TaskListSerializer, TaskDetailSerializer, CommentSerializer
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404


class BoardListView(generics.ListCreateAPIView):
    queryset = Boards.objects.all()
    serializer_class = BoardListSerializer

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


class TaskListView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskListSerializer


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer


class CommentOfTasksList(generics.ListCreateAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        task = Task.objects.get(pk=pk)
        return task.comments.all()

    def create(self, request, *args, **kwargs):
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

    def get_queryset(self):
        task_id = self.kwargs['task_id']
        return Comment.objects.filter(task_id=task_id)
