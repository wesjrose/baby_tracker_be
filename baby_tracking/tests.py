from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Baby, GuardianMapping

User = get_user_model()


class CreateBabyTests(APITestCase):
    def setUp(self):
        self.url = reverse("create-baby")
        self.payload = {"name": "Charlie"}
        self.email = "parent@example.com"
        self.password = "s3cure-Passw0rd!"
        self.user = User.objects.create_user(email=self.email, password=self.password)

    def authenticate(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"email": self.email, "password": self.password},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def test_create_baby_with_credentials(self):
        self.authenticate()

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], self.payload["name"])

        baby = Baby.objects.filter(name=self.payload["name"]).first()
        self.assertEqual(baby.name, self.payload["name"])
        self.assertTrue(
            GuardianMapping.objects.filter(baby=baby, guardian=self.user).exists()
        )

    def test_create_baby_without_credentials_is_rejected(self):
        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(Baby.objects.exists())
        self.assertFalse(GuardianMapping.objects.exists())
