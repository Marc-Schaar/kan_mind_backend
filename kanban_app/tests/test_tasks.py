from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from kanban_app.models import Boards, Task


class TaskListTests(APITestCase):
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

        self.other_board = Boards.objects.create(title="Other Board", owner=self.outsider)
        self.other_board.members.add(self.outsider)

        self.task = Task.objects.create(
            board=self.board,
            title="Do something",
            creator=self.owner,
            assignee=self.member,
            reviewer=self.owner,
        )
        Task.objects.create(
            board=self.other_board,
            title="Unrelated task",
            creator=self.outsider,
            assignee=self.outsider,
            reviewer=self.outsider,
        )

        self.url = reverse("task-list")

    def test_list_requires_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_only_returns_tasks_of_own_boards(self):
        self.client.force_authenticate(self.member)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task_ids = {task["id"] for task in response.data}
        self.assertEqual(task_ids, {self.task.id})

    def test_create_task_requires_board_id(self):
        self.client.force_authenticate(self.member)
        response = self.client.post(self.url, {"title": "No board given"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_task_unknown_board_returns_404(self):
        self.client.force_authenticate(self.member)
        response = self.client.post(
            self.url,
            {
                "board": 999999,
                "title": "Ghost board task",
                "assignee_id": self.member.id,
                "reviewer_id": self.owner.id,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_task_denied_for_non_member(self):
        self.client.force_authenticate(self.outsider)
        response = self.client.post(
            self.url,
            {
                "board": self.board.id,
                "title": "Sneaky task",
                "assignee_id": self.member.id,
                "reviewer_id": self.owner.id,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_task_success_for_member(self):
        self.client.force_authenticate(self.member)
        response = self.client.post(
            self.url,
            {
                "board": self.board.id,
                "title": "New task",
                "assignee_id": self.member.id,
                "reviewer_id": self.owner.id,
                "priority": "high",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "New task")
        self.assertEqual(response.data["assignee"]["id"], self.member.id)
        self.assertTrue(
            Task.objects.filter(board=self.board, title="New task").exists()
        )


class TaskDetailTests(APITestCase):
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
            board=self.board,
            title="Do something",
            creator=self.member,
            assignee=self.member,
            reviewer=self.owner,
        )

        self.url = reverse("task-detail", args=[self.task.id])

    def test_retrieve_requires_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_updates_status_for_board_member(self):
        self.client.force_authenticate(self.owner)
        response = self.client.patch(self.url, {"status": "done"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, "done")

    def test_patch_denied_for_non_member(self):
        self.client.force_authenticate(self.outsider)
        response = self.client.patch(self.url, {"status": "done"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_allowed_for_creator(self):
        self.client.force_authenticate(self.member)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())

    def test_delete_allowed_for_board_owner(self):
        self.client.force_authenticate(self.owner)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())

    def test_delete_denied_for_other_member(self):
        other_member = User.objects.create_user(
            username="other_member",
            email="other_member@example.com",
            password="supersecret123",
        )
        self.board.members.add(other_member)

        self.client.force_authenticate(other_member)
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Task.objects.filter(id=self.task.id).exists())


class TaskAssignedAndReviewingTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner", email="owner@example.com", password="supersecret123"
        )
        self.member = User.objects.create_user(
            username="member", email="member@example.com", password="supersecret123"
        )

        self.board = Boards.objects.create(title="Team Board", owner=self.owner)
        self.board.members.add(self.owner, self.member)

        self.assigned_task = Task.objects.create(
            board=self.board,
            title="Assigned to member",
            creator=self.owner,
            assignee=self.member,
            reviewer=self.owner,
        )
        self.reviewing_task = Task.objects.create(
            board=self.board,
            title="Reviewed by member",
            creator=self.owner,
            assignee=self.owner,
            reviewer=self.member,
        )

    def test_assigned_to_me_returns_only_own_assignments(self):
        self.client.force_authenticate(self.member)
        response = self.client.get(reverse("task-assigned-to-me"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task_ids = {task["id"] for task in response.data}
        self.assertEqual(task_ids, {self.assigned_task.id})

    def test_reviewing_returns_only_own_reviews(self):
        self.client.force_authenticate(self.member)
        response = self.client.get(reverse("task-reviewing"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task_ids = {task["id"] for task in response.data}
        self.assertEqual(task_ids, {self.reviewing_task.id})

    def test_assigned_to_me_requires_authentication(self):
        response = self.client.get(reverse("task-assigned-to-me"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
