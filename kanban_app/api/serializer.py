from rest_framework import serializers
from kanban_app.models import Boards
from django.contrib.auth.models import User


class UserSimpleSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class BoardsSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)
        view = self.context.get('view')

        if view and view.action == 'list':
            allowed = ['id', 'title', 'member_count',
                       'ticket_count', 'tasks_to_do_count', 'tasks_high_prio_count', 'owner_id']
            existing = set(self.fields)
            for field_name in existing - set(allowed):
                self.fields.pop(field_name)
        elif view and view.action == 'retrieve':
            # Für Einschränkung aktivieren
            # allowed = ['id', 'title', 'member_count',
            #            'ticket_count', 'tasks_to_do_count', 'tasks_high_prio_count', 'owner_id']
            # existing = set(self.fields)
            # for field_name in existing - set(allowed):
            #     self.fields.pop(field_name)
            pass

    members = UserSimpleSerializer(many=True, read_only=True)
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Boards
        exclude = []

    def get_member_count(self, obj):
        return obj.members.count()
