from django.db import models

# Create your models here.


class Boards(models.Model):
    title = models.CharField(max_length=100),
    member_count = models.PositiveIntegerField(default=0),
    ticket_count = models.PositiveIntegerField(default=0),
    task_to_do_count = models.PositiveIntegerField(default=0),
    task_high_priority_count = models.PositiveIntegerField(default=0),
    ownder_id = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title
