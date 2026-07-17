from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class RegistrationTests(APITestCase):
    def setUp(self):
        self.url = reverse("registration-view")
        self.valid_payload = {
            "fullname": "Max Mustermann",
            "email": "max@example.com",
            "password": "supersecret123",
            "repeated_password": "supersecret123",
        }

    def test_registration_success_creates_user_and_token(self):
        response = self.client.post(self.url, self.valid_payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], "max@example.com")
        self.assertEqual(response.data["fullname"], "Max Mustermann")
        self.assertIn("token", response.data)

        user = User.objects.get(email="max@example.com")
        self.assertTrue(
            Token.objects.filter(user=user, key=response.data["token"]).exists()
        )

    def test_registration_rejects_duplicate_email(self):
        User.objects.create_user(
            username="existing", email="max@example.com", password="whatever123"
        )

        response = self.client.post(self.url, self.valid_payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.filter(email="max@example.com").count(), 1)

    def test_registration_rejects_password_mismatch(self):
        payload = {**self.valid_payload, "repeated_password": "different456"}

        response = self.client.post(self.url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email="max@example.com").exists())

    def test_registration_rejects_missing_fields(self):
        response = self.client.post(self.url, {"email": "incomplete@example.com"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
