from django.contrib.auth.models import User
from rest_framework import serializers

from kanban_app.models import Boards, Comment, Task


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for Django User model.
    Provides 'id', 'email' and 'fullname' fields.
    """
    class Meta:
        model = User
        fields = ["id", "email", "fullname"]

    fullname = serializers.SerializerMethodField()

    def get_fullname(self, obj):
        return obj.username if obj.get_full_name() else obj.username


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model.
    Includes author name as a string, creation date and content.
    """

    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["id", "created_at", "author", "content"]

    def get_author(self, obj):
        return obj.author.get_full_name() or obj.author.username


class TaskListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing tasks.
    Includes assignee and reviewer info and count of comments.
    Supports writing assignee_id and reviewer_id.
    """
    assignee = UserSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        source="assignee", queryset=User.objects.all(), write_only=True
    )
    reviewer = UserSerializer(read_only=True)
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source="reviewer", queryset=User.objects.all(), write_only=True
    )
    comments_count = serializers.SerializerMethodField()
    creator = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "assignee_id",
            "reviewer",
            "reviewer_id",
            "due_date",
            "comments_count",
            "creator"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")
        if request and request.method in ["GET"]:
            self.fields.pop("creator", None)

    def get_comments_count(self, obj):
        return obj.comments.count()


class TaskDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for a single task.
    Includes nested assignee, reviewer, and comments.
    Comments field is excluded on update requests (PUT/PATCH).
    """
    assignee = UserSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        source="assignee", queryset=User.objects.all(), write_only=True
    )
    reviewer = UserSerializer(read_only=True)
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source="reviewer", queryset=User.objects.all(), write_only=True
    )
    comments = CommentSerializer(many=True, read_only=True)
    creator = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "assignee_id",
            "reviewer",
            "reviewer_id",
            "due_date",
            "comments",
            "creator"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")
        if request and request.method in ["GET"]:
            self.fields.pop("creator", None)

        if request and request.method in ["PUT", "PATCH"]:
            self.fields.pop("comments", None)


class BoardListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing boards.
    Supports writing members by their user IDs.
    Returns member count, ticket count, todo tasks count, and high priority tasks count.
    """
    class Meta:
        model = Boards
        fields = [
            "id",
            "title",
            "member_count",
            "ticket_count",
            "tasks_to_do_count",
            "tasks_high_prio_count",
            "owner_id",
            "members",
        ]

    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, write_only=True
    )
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    def get_member_count(self, obj):
        return len(obj.members.all())

    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status="to-do").count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority="high").count()


class BoardDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for a single board.
    Includes owner info and list of tasks.
    Adjusts fields dynamically based on request method.
    """
    title = serializers.CharField()
    owner_id = serializers.IntegerField(read_only=True)
    owner_data = UserSerializer(read_only=True, source="owner")
    tasks = TaskListSerializer(many=True, read_only=True)

    class Meta:
        model = Boards
        fields = ["id", "title", "owner_id", "owner_data", "members", "tasks"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")
        if request and request.method == "GET":
            self.fields.pop("owner_data", None)

        if request and request.method == "PUT" or request.method == "PATCH":
            self.fields.pop("owner_id", None)
            self.fields.pop("tasks", None)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["members"] = UserSerializer(instance.members.all(), many=True).data
        return rep
