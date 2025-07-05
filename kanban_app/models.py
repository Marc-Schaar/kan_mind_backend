from django.contrib.auth.models import User
from django.db import models


class Boards(models.Model):
    title = models.CharField(max_length=100, blank=False, null=False)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owned_boards", default=None
    )
    members = models.ManyToManyField(User, related_name="boards")
    member_count = models.IntegerField(default=0)
    ticket_count = models.IntegerField(default=0)
    tasks_to_do_count = models.IntegerField(default=0)
    tasks_high_prio_count = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class Task(models.Model):
    STATUS_CHOICES = [
        ("to-do", "To Do"),
        ("in-progress", "In Progress"),
        ("review", "Review"),
        ("done", "Done"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    board = models.ForeignKey(
        Boards, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(choices=STATUS_CHOICES, default="to-do")
    priority = models.CharField(choices=PRIORITY_CHOICES, default="low")
    assignee = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="assigned_tasks",
        on_delete=models.SET_NULL,
    )
    reviewer = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="review_tasks",
        on_delete=models.SET_NULL,
    )
    due_date = models.DateField(null=True, blank=True)
    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_tasks"
    )


def __str__(self):
    return self.title


class Comment(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()

    def __str__(self):
        return f"Comment by {self.author} on {self.task.title}"
