from rest_framework import serializers
from kanban_app.models import Boards


class BoardsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Boards
        fields = ['id', 'title']
