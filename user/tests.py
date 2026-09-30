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


class CreateUserTests(APITestCase):
    def setUp(self):
        self.url = reverse("create-user")
        self.payload = {
            "email": "new.parent@example.com",
            "password": "s3cure-Passw0rd!",
            "first_name": "New",
            "last_name": "Parent",
        }

    def test_create_user(self):
        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], self.payload["email"])
        self.assertEqual(response.data["first_name"], self.payload["first_name"])
        self.assertEqual(response.data["last_name"], self.payload["last_name"])
        self.assertIn("id", response.data)
        self.assertNotIn("password", response.data)

        user = User.objects.get(pk=response.data["id"])
        self.assertEqual(user.email, self.payload["email"])
        self.assertNotEqual(str(user.password), self.payload["password"])
        self.assertTrue(user.check_password(self.payload["password"]))

    def test_created_user_can_obtain_token_pair(self):
        self.client.post(self.url, self.payload, format="json")

        response = self.client.post(
            reverse("token_obtain_pair"),
            {"email": self.payload["email"], "password": self.payload["password"]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_email_is_lowercased(self):
        self.payload["email"] = "New.Parent@Example.com"

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], "new.parent@example.com")

    def test_duplicate_email_is_rejected_case_insensitively(self):
        User.objects.create_user(email="new.parent@example.com", password="an0ther-Passw0rd!")
        self.payload["email"] = "NEW.PARENT@example.com"

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertEqual(User.objects.count(), 1)

    def test_weak_password_is_rejected(self):
        self.payload["password"] = "123"

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertFalse(User.objects.filter(email=self.payload["email"]).exists())

    def test_missing_email_and_password_are_rejected(self):
        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertIn("password", response.data)
