from rest_framework import serializers
from kanban_app.models import Boards
from django.contrib.auth.models import User


class BoardsSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Boards
        exclude = []

    def get_member_count(self, obj):
        return obj.members.count()
