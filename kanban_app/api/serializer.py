from rest_framework import serializers
from kanban_app.models import Boards, Task
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

    fullname = serializers.SerializerMethodField()

    def get_fullname(self, obj):
        return obj.get_full_name()


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status',
                  'priority', 'assignee', 'reviewer', 'due_date']


class BoardListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Boards
        fields = ['id', 'title', 'member_count', 'ticket_count',
                  'tasks_to_do_count', 'tasks_high_prio_count', 'owner_id', 'members']

    member_count = serializers.SerializerMethodField()
    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, write_only=True)

    def get_member_count(self, obj):
        return len(obj.members.all())


class BoardDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Boards
        fields = ['id', 'title', 'owner_id', 'members']

    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all())

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['members'] = UserSerializer(
            instance.members.all(), many=True).data
        return rep
