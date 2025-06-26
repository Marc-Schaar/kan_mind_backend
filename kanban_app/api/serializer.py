from rest_framework import serializers
from kanban_app.models import Boards


class BoardsSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Boards
        exclude = []

    def get_member_count(self, obj):
        return obj.members.count()

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
