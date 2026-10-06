from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Baby, BabyEvent, GuardianMapping

User = get_user_model()


class CreateBabyTests(APITestCase):
    def setUp(self):
        self.url = reverse("baby")
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


class CreateEventTests(APITestCase):
    def setUp(self):
        self.email = "parent@example.com"
        self.password = "s3cure-Passw0rd!"
        self.user = User.objects.create_user(email=self.email, password=self.password)
        self.baby = Baby.objects.create(name="Charlie")
        GuardianMapping.objects.create(baby=self.baby, guardian=self.user)
        self.url = reverse("event", kwargs={"baby_id": self.baby.pk})
        self.base_payload = {
            "created_at": "2026-10-06T08:30:00Z",
            "notes": "All went well",
        }

    def authenticate(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"email": self.email, "password": self.password},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def assert_event_created(self, event_type, data):
        self.authenticate()

        response = self.client.post(
            self.url,
            {"type": event_type, **self.base_payload, "data": data},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        event = BabyEvent.objects.get()
        self.assertEqual(event.baby, self.baby)
        self.assertEqual(event.type, event_type)
        self.assertEqual(event.created_at, self.base_payload["created_at"])
        self.assertEqual(event.notes, self.base_payload["notes"])
        # print(f"The sent data is:\n{data}")
        # print(f"The obj data is:\n{event.data}")
        self.assertEqual(event.data, data)

    def test_create_event_without_credentials_is_rejected(self):
        response = self.client.post(
            self.url,
            {"type": "diaper", **self.base_payload, "data": {"contents": "wet"}},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(BabyEvent.objects.exists())

    def test_create_event_for_baby_user_is_not_guardian_of_is_rejected(self):
        other_baby = Baby.objects.create(name="Not Mine")
        other_guardian = User.objects.create_user(
            email="other.parent@example.com", password=self.password
        )
        GuardianMapping.objects.create(baby=other_baby, guardian=other_guardian)
        self.authenticate()

        response = self.client.post(
            reverse("event", kwargs={"baby_id": other_baby.pk}),
            {"type": "diaper", **self.base_payload, "data": {"contents": "wet"}},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(BabyEvent.objects.exists())

    def test_create_bottle_feed_event(self):
        self.assert_event_created("bottle_feed", {"amount": 120, "contents": "formula"})

    def test_create_bottle_feed_event_without_amount_is_rejected(self):
        self.authenticate()

        response = self.client.post(
            self.url,
            {
                "type": "bottle_feed",
                **self.base_payload,
                "data": {"contents": "formula"},
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("amount", response.data["data"])
        self.assertFalse(BabyEvent.objects.exists())

    def test_create_breast_feed_event(self):
        self.assert_event_created("breast_feed", {"left_time": 10, "right_time": 15})

    def test_create_diaper_event(self):
        self.assert_event_created(
            "diaper",
            {
                "contents": "dirty",
                "colour": "yellow",
                "composition": "mushy",
                "blowout": False,
                "diaper_rash": True,
            },
        )
