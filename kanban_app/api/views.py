
from rest_framework import viewsets
from kanban_app.models import Boards
from .serializer import BoardsSerializer


class BoardViewset(viewsets.ModelViewSet):
    queryset = Boards.objects.all()
    serializer_class = BoardsSerializer
