from django.db import models
from django.contrib.auth.models import User


class Boards(models.Model):
    title = models.CharField(max_length=100, default=True)
    members = models.ManyToManyField(User, related_name='boards')
    ticket_count = models.PositiveIntegerField(editable=False, default=True)
    tasks_to_do_count = models.PositiveIntegerField(
        editable=False, default=True)
    tasks_high_prio_count = models.PositiveIntegerField(
        editable=False, default=True)
    owner_id = models.IntegerField(editable=False)

    def __str__(self):
        return self.title


class Task(models.Model):
    board = models.ForeignKey(
        Boards, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, default='')
    priority = models.CharField(max_length=20, default='low')

    assignee = models.ForeignKey(User, null=True, blank=True,
                                 related_name='assigned_tasks', on_delete=models.SET_NULL)
    reviewer = models.ForeignKey(User, null=True, blank=True,
                                 related_name='review_tasks', on_delete=models.SET_NULL)

    due_date = models.DateTimeField(null=True, blank=True)


class Comment(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()

    def __str__(self):
        return f'Comment by {self.author} on {self.task.title}'
