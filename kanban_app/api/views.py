
from rest_framework import viewsets
from kanban_app.models import Boards
from .serializer import BoardsSerializer


class BoardViewset(viewsets.ModelViewSet):

    queryset = Boards.objects.all()
    serializer_class = BoardsSerializer

    def perform_create(self, serializer):
        serializer.save(owner_id=self.request.user.id)
