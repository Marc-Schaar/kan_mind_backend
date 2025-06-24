from django.db import models
from django.contrib.auth.models import User


class Boards(models.Model):
    title = models.CharField(max_length=100, default=True)
    members = models.ManyToManyField(
        User, related_name='boards', blank=True)
    ticket_count = models.PositiveIntegerField(editable=False, default=True)
    task_to_do_count = models.PositiveIntegerField(
        editable=False, default=True)
    task_high_priority_count = models.PositiveIntegerField(
        editable=False, default=True)
    owner_id = models.IntegerField(editable=False)

    def __str__(self):
        return self.title
