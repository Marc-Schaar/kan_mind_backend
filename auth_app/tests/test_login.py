from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class LoginTests(APITestCase):
    def setUp(self):
        self.url = reverse("login-view")
        self.user = User.objects.create_user(
            username="maxmustermann",
            email="max@example.com",
            password="supersecret123",
        )

    def test_login_success_returns_token(self):
        response = self.client.post(
            self.url, {"email": "max@example.com", "password": "supersecret123"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["user_id"], self.user.id)
        self.assertEqual(response.data["email"], "max@example.com")

    def test_login_rejects_wrong_password(self):
        response = self.client.post(
            self.url, {"email": "max@example.com", "password": "wrongpassword"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_rejects_unknown_email(self):
        response = self.client.post(
            self.url, {"email": "nobody@example.com", "password": "whatever123"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
