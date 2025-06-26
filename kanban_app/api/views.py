
from rest_framework import viewsets
from kanban_app.models import Boards
from .serializer import BoardsSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics


class BoardViewset(viewsets.ModelViewSet):

    queryset = Boards.objects.all()
    serializer_class = BoardsSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        headers.update({'Status-Message': 'Board wurde erfolgreich erstellt'})

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(owner_id=self.request.user.id)
