from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class UserProfileTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="max", email="max@example.com", password="supersecret123"
        )
        self.other = User.objects.create_user(
            username="erika", email="erika@example.com", password="supersecret123"
        )

    def test_profile_list_requires_authentication(self):
        response = self.client.get(reverse("userprofile-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_list_returns_all_users(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse("userprofile-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_profile_detail_returns_user(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse("userprofile-detail", args=[self.other.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "erika@example.com")

    def test_profile_detail_unknown_id_returns_404(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse("userprofile-detail", args=[999999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
