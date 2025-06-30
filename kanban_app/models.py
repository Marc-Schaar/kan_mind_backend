from django.db import models
from django.contrib.auth.models import User


class Boards(models.Model):
    title = models.CharField(max_length=100, default=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='owned_boards')
    members = models.ManyToManyField(User, related_name='boards')

    def __str__(self):
        return self.title


class Task(models.Model):
    STATUS_CHOICES = [
        ('to-do', 'To Do'),
        ('in-progress', 'In Progress'),
        ('review', 'Review'),
        ('done', 'Done'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    board = models.ForeignKey(
        Boards, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(choices=STATUS_CHOICES, default='to-do')
    priority = models.CharField(choices=PRIORITY_CHOICES, default='low')
    assignee = models.ForeignKey(
        User, null=True, blank=True,
        related_name='assigned_tasks',
        on_delete=models.SET_NULL
    )
    reviewer = models.ForeignKey(
        User, null=True, blank=True,
        related_name='review_tasks',
        on_delete=models.SET_NULL
    )
    due_date = models.DateTimeField(null=True, blank=True)


def __str__(self):
    return self.title


class Comment(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()

    def __str__(self):
        return f'Comment by {self.author} on {self.task.title}'
