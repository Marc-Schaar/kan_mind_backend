
from rest_framework import viewsets
from kanban_app.models import Boards
from .serializer import BoardsSerializer
from rest_framework.response import Response
from rest_framework import status


class BoardViewset(viewsets.ModelViewSet):

    queryset = Boards.objects.all()
    serializer_class = BoardsSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        data = {}

        if serializer.is_valid():
            board = serializer.save(owner_id=self.request.user.id)
            board.members.add(self.request.user)
            data = {
                'id': board.id,
                'title': board.title,
                'member_count': len(board.members.all()),
                'ticket_count': board.ticket_count,
                'tasks_to_do_count': board.tasks_to_do_count,
                'tasks_high_prio_count': board.tasks_high_prio_count,
                'owner_id': board.owner_id,

            }
            return Response(data, status=status.HTTP_201_CREATED, )

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
