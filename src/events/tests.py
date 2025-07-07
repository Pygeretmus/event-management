from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from events.models import Event

User = get_user_model()


class EventAPITestCase(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create_user(username="testuser1", email="test1@example.com", password="testpass123")
        cls.user2 = User.objects.create_user(username="testuser2", email="test2@example.com", password="testpass123")

        # Создаем тестовое событие
        cls.event1 = Event.objects.create(
            title="Test Event 1",
            description="Test Description 1",
            date=timezone.now() + timedelta(days=7),
            location="Test Location 1",
            organizer=cls.user1,
        )

        cls.event2 = Event.objects.create(
            title="Test Event 2",
            description="Test Description 2",
            date=timezone.now() + timedelta(days=14),
            location="Test Location 2",
            organizer=cls.user2,
        )

        cls.list_url = reverse("event-list")

    def detail_url(self, pk):
        return reverse("event-detail", kwargs={"pk": pk})

    def test_get_event_list_unauthenticated_success(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["title"], self.event1.title)

    def test_get_event_list_authenticated_success(self):
        for user in [self.user1, self.user2]:
            self.client.force_authenticate(user=self.user1)
            response = self.client.get(self.list_url)

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), 2)

    def test_create_event_authenticated_success(self):
        self.client.force_authenticate(user=self.user1)

        data = {
            "title": "New Event",
            "description": "New Description",
            "date": (timezone.now() + timedelta(days=30)).isoformat(),
            "location": "New Location",
        }

        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 3)
        self.assertEqual(response.data["title"], "New Event")
        self.assertEqual(response.data["organizer"], str(self.user1))

    def test_create_event_unauthenticated_fail(self):
        data = {
            "title": "New Event",
            "description": "New Description",
            "date": (timezone.now() + timedelta(days=30)).isoformat(),
            "location": "New Location",
        }

        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_event_invalid_data_fail(self):
        self.client.force_authenticate(user=self.user1)

        data = {"title": "", "description": "Test Description", "date": "invalid-date", "location": "Test Location"}

        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["errors"]["title"], "This field may not be blank.")
        self.assertEqual(
            response.data["errors"]["date"],
            "Datetime has wrong format. Use one of these formats instead: YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z].",
        )

    def test_get_event_detail_success(self):
        response = self.client.get(self.detail_url(self.event1.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Event 1")
        self.assertEqual(response.data["id"], self.event1.id)

    def test_get_non_existent_event_detail_fail(self):
        response = self.client.get(self.detail_url(1000))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_event_by_organizer_success(self):
        self.client.force_authenticate(user=self.user1)

        data = {
            "title": "Updated Event Title",
            "description": "Updated Description",
            "date": (timezone.now() + timedelta(days=15)).isoformat(),
            "location": "Updated Location",
        }

        response = self.client.put(self.detail_url(self.event1.id), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated Event Title")

    def test_update_event_by_non_organizer_fail(self):
        self.client.force_authenticate(user=self.user2)

        data = {
            "title": "Updated Event Title",
            "description": "Updated Description",
            "date": (timezone.now() + timedelta(days=15)).isoformat(),
            "location": "Updated Location",
        }

        response = self.client.put(self.detail_url(self.event1.id), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_non_existent_event_fail(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.put(self.detail_url(1000))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_partial_update_event_by_organizer_success(self):
        self.client.force_authenticate(user=self.user1)

        data = {"title": "Partially Updated Title"}

        response = self.client.patch(self.detail_url(self.event1.id), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Partially Updated Title")
        self.assertEqual(response.data["description"], "Test Description 1")

    def test_partial_update_event_by_non_organizer_fail(self):
        self.client.force_authenticate(user=self.user2)

        data = {"title": "Partially Updated Title"}

        response = self.client.patch(self.detail_url(self.event1.id), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update_non_existent_event_fail(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.patch(self.detail_url(1000))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_event_by_organizer_success(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.delete(self.detail_url(self.event1.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Event.objects.count(), 1)

    def test_delete_event_by_non_organizer_fail(self):
        self.client.force_authenticate(user=self.user2)

        response = self.client.delete(self.detail_url(self.event1.id))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_non_existent_event_fail(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(self.detail_url(1000))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
