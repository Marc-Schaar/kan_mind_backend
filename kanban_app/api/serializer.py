from rest_framework import serializers
from kanban_app.models import Boards
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

    fullname = serializers.SerializerMethodField()

    def get_fullname(self, obj):
        return obj.get_full_name()


class BoardsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Boards
        exclude = []

    member_count = serializers.SerializerMethodField()
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all()
    )

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['members'] = UserSerializer(
            instance.members.all(), many=True).data
        return rep

    def get_member_count(self, obj):
        return len(obj.members.all())

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

            allowed = ['id', 'title', 'owner_id', 'members', ]
            existing = set(self.fields)
            for field_name in existing - set(allowed):
                self.fields.pop(field_name)
            self.fields = {field: self.fields[field] for field in allowed}
