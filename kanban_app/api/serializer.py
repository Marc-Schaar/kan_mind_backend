from rest_framework import serializers
from kanban_app.models import Boards


class BoardsSerializer(serializers.ModelSerializer):

    member_count = "2"

    class Meta:
        model = Boards
        exclude = []
