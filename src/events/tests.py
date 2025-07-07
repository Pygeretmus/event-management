from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from events.models import Event, EventRegistration

User = get_user_model()


class EventAPITestCase(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create_user(username="testuser1", email="test1@example.com", password="testpass123")
        cls.user2 = User.objects.create_user(username="testuser2", email="test2@example.com", password="testpass123")
        cls.now = timezone.now()

        cls.event1 = Event.objects.create(
            title="Music Fest",
            description="Outdoor concert",
            date=cls.now + timedelta(days=5),
            location="New York",
            organizer=cls.user1,
        )
        cls.event2 = Event.objects.create(
            title="Art Expo",
            description="Gallery exhibit",
            date=cls.now + timedelta(days=10),
            location="Paris",
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
            self.client.force_authenticate(user=user)
            response = self.client.get(self.list_url)

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), 2)

    def test_get_search_by_location_success(self):
        response = self.client.get(self.list_url + "?search=paris")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["location"].lower(), "paris")

    def test_get_search_by_title_success(self):
        response = self.client.get(self.list_url + "?search=EXPO")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn("EXPO", response.data[0]["title"].upper())

    def test_get_search_by_organizer_success(self):
        response = self.client.get(self.list_url + f"?search={self.user1.username}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["organizer"], str(self.user1))

    def test_get_filter_by_date_success(self):
        start = (self.now + timedelta(days=6)).strftime("%Y-%m-%dT%H:%M:%S")
        end = (self.now + timedelta(days=15)).strftime("%Y-%m-%dT%H:%M:%S")

        response = self.client.get(self.list_url + f"?end_date={end}&start_date={start}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Art Expo")

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
        self.assertEqual(response.data["title"], "Music Fest")
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
        self.assertEqual(response.data["description"], "Outdoor concert")

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


class EventRegistrationAPITestCase(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create_user(username="testuser1", email="test1@example.com", password="testpass123")
        cls.user2 = User.objects.create_user(username="testuser2", email="test2@example.com", password="testpass123")
        cls.user3 = User.objects.create_user(username="testuser3", email="test3@example.com", password="testpass123")

        cls.event = Event.objects.create(
            title="Test Event 1",
            description="Test Description 1",
            date=timezone.now() + timedelta(days=7),
            location="Test Location 1",
            organizer=cls.user1,
        )

        EventRegistration.objects.create(user=cls.user3, event=cls.event)

    def register_url(self, pk):
        return reverse("event-register", kwargs={"pk": pk})

    def test_register_organiser_fail(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.register_url(self.event.id))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_register_user_success(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(self.register_url(self.event.id))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {"detail": "Registration successful."})

    def test_register_registered_user_fail(self):
        self.client.force_authenticate(user=self.user3)
        response = self.client.post(self.register_url(self.event.id))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "message": "Validation error",
                "errors": {"non_field_errors": "You are already registered for this event."},
            },
        )

    def test_register_unauthorized_fail(self):
        response = self.client.post(self.register_url(self.event.id))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
