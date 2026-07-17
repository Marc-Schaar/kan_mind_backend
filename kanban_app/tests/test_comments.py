from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from kanban_app.models import Boards, Comment, Task


class CommentListTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner", email="owner@example.com", password="supersecret123"
        )
        self.member = User.objects.create_user(
            username="member", email="member@example.com", password="supersecret123"
        )
        self.outsider = User.objects.create_user(
            username="outsider", email="outsider@example.com", password="supersecret123"
        )

        self.board = Boards.objects.create(title="Team Board", owner=self.owner)
        self.board.members.add(self.owner, self.member)

        self.task = Task.objects.create(
            board=self.board, title="Do something", creator=self.owner
        )
        self.comment = Comment.objects.create(
            task=self.task, author=self.owner, content="First comment"
        )

        self.url = reverse("task-comments", args=[self.task.id])

    def test_list_requires_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_denied_for_non_member(self):
        self.client.force_authenticate(self.outsider)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_returns_comments_for_member(self):
        self.client.force_authenticate(self.member)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["content"], "First comment")

    def test_list_unknown_task_returns_404(self):
        self.client.force_authenticate(self.member)
        response = self.client.get(reverse("task-comments", args=[999999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_comment_success(self):
        self.client.force_authenticate(self.member)
        response = self.client.post(self.url, {"content": "New comment"})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["author"], self.member.username)
        self.assertTrue(
            Comment.objects.filter(task=self.task, content="New comment").exists()
        )

    def test_create_comment_denied_for_non_member(self):
        self.client.force_authenticate(self.outsider)
        response = self.client.post(self.url, {"content": "Sneaky comment"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CommentDeleteTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner", email="owner@example.com", password="supersecret123"
        )
        self.member = User.objects.create_user(
            username="member", email="member@example.com", password="supersecret123"
        )

        self.board = Boards.objects.create(title="Team Board", owner=self.owner)
        self.board.members.add(self.owner, self.member)

        self.task = Task.objects.create(
            board=self.board, title="Do something", creator=self.owner
        )
        self.comment = Comment.objects.create(
            task=self.task, author=self.member, content="Delete me"
        )

        self.url = reverse(
            "task-comments-detail", args=[self.task.id, self.comment.id]
        )

    def test_delete_allowed_for_author(self):
        self.client.force_authenticate(self.member)
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())

    def test_delete_denied_for_non_author(self):
        self.client.force_authenticate(self.owner)
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Comment.objects.filter(id=self.comment.id).exists())
