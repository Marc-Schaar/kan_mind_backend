from django.db import models
from django.contrib.auth.models import User


class Boards(models.Model):
    title = models.CharField(max_length=100, default=True)
    member_count = models.PositiveIntegerField(default=True)
    ticket_count = models.PositiveIntegerField(default=True)
    task_to_do_count = models.PositiveIntegerField(default=True)
    task_high_priority_count = models.PositiveIntegerField(default=True)
    ownder_id = models.PositiveIntegerField(default=True)

    def __str__(self):
        return self.title
