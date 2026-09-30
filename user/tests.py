from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

User = get_user_model()


class TokenObtainTests(APITestCase):
    def setUp(self):
        self.email = "parent@example.com"
        self.password = "s3cure-Passw0rd!"
        self.user = User.objects.create_user(email=self.email, password=self.password)

    def test_create_user_and_obtain_token_pair(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"email": self.email, "password": self.password},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        access = AccessToken(response.data["access"])
        refresh = RefreshToken(response.data["refresh"])
        self.assertEqual(str(access["user_id"]), str(self.user.pk))
        self.assertEqual(str(refresh["user_id"]), str(self.user.pk))

    def test_obtain_token_with_wrong_password_fails(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"email": self.email, "password": "wrong-password"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
