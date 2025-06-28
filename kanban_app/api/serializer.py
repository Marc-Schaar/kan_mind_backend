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
    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        source='assignee', queryset=User.objects.all(), write_only=True, required=False, allow_null=True)
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source='reviewer', queryset=User.objects.all(), write_only=True, required=False, allow_null=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description', 'status', 'priority',
            'assignee', 'reviewer', 'assignee_id', 'reviewer_id',
            'due_date', 'comments_count'
        ]

    def get_comments_count(self, obj):
        return obj.comments.count()


class BoardListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Boards
        fields = ['id', 'title', 'member_count', 'ticket_count',
                  'tasks_to_do_count', 'tasks_high_prio_count', 'owner_id', 'members']

    member_count = serializers.SerializerMethodField()
    members = UserSerializer(many=True, read_only=True)
    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True,)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['members'] = UserSerializer(
            instance.members.all(), many=True).data
        return rep

    def get_member_count(self, obj):
        return len(obj.members.all())


class BoardDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Boards
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']

    members = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all()
    )
    tasks = TaskSerializer(many=True, read_only=True)

    def update(self, instance, validated_data):
        members = validated_data.pop('members', None)
        instance.title = validated_data.get('title', instance.title)
        instance.owner_id = validated_data.get('owner_id', instance.owner_id)
        instance.save()
        return instance
