from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from kanban_app.models import Boards


class BoardListTests(APITestCase):
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

        self.url = reverse("board-list")

    def test_list_requires_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_only_returns_boards_where_user_is_member(self):
        self.client.force_authenticate(self.member)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.board.id)

    def test_list_empty_for_outsider(self):
        self.client.force_authenticate(self.outsider)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_create_board_sets_owner_and_adds_creator_as_member(self):
        self.client.force_authenticate(self.outsider)
        response = self.client.post(
            self.url, {"title": "New Board", "members": [self.member.id]}
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["owner_id"], self.outsider.id)

        board = Boards.objects.get(id=response.data["id"])
        member_ids = set(board.members.values_list("id", flat=True))
        self.assertEqual(member_ids, {self.outsider.id, self.member.id})

    def test_create_board_requires_title(self):
        self.client.force_authenticate(self.outsider)
        response = self.client.post(self.url, {"members": []})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class BoardDetailTests(APITestCase):
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

        self.url = reverse("board-detail", args=[self.board.id])

    def test_retrieve_allowed_for_member(self):
        self.client.force_authenticate(self.member)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Team Board")

    def test_retrieve_denied_for_non_member(self):
        self.client.force_authenticate(self.outsider)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_unknown_board_returns_404(self):
        self.client.force_authenticate(self.owner)
        response = self.client.get(reverse("board-detail", args=[999999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_updates_title_for_member(self):
        self.client.force_authenticate(self.member)
        response = self.client.patch(
            self.url,
            {"title": "Renamed Board", "members": [self.owner.id, self.member.id]},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.board.refresh_from_db()
        self.assertEqual(self.board.title, "Renamed Board")

    def test_delete_denied_for_non_owner_member(self):
        self.client.force_authenticate(self.member)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Boards.objects.filter(id=self.board.id).exists())

    def test_delete_allowed_for_owner(self):
        self.client.force_authenticate(self.owner)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Boards.objects.filter(id=self.board.id).exists())
