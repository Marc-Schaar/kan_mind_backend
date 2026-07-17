from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class EmailCheckTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="max", email="max@example.com", password="supersecret123"
        )
        self.url = reverse("email-check")

    def test_returns_user_for_known_email(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url, {"email": "max@example.com"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.user.id)

    def test_returns_404_for_unknown_email(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url, {"email": "nobody@example.com"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_requires_authentication(self):
        response = self.client.get(self.url, {"email": "max@example.com"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
