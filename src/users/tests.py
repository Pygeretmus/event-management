from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class UserCreateUserViewTest(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = reverse("user-create")
        cls.existing_user_data = {
            "username": "existing_user",
            "first_name": "Existing",
            "last_name": "user",
            "email": "test@existing.com",
            "password": "strongpassword123",
        }
        cls.data = {
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "password": "strongpassword123",
        }
        cls.existing_user = User.objects.create(**cls.existing_user_data)

    def test_create_user_success(self):
        response = self.client.post(self.url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.last()

        for key in ["username", "first_name", "last_name", "email"]:
            self.assertEqual(getattr(user, key), self.data[key])

        self.assertTrue(user.check_password("strongpassword123"))

    def test_create_existing_user_fail(self):

        data = self.existing_user_data.copy()
        data["username"] = "Test"

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "message": "Validation error",
                "errors": {
                    "email": "user with this email address already exists.",
                },
            },
        )

        data = self.existing_user_data.copy()
        data["email"] = "Test@test.com"

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "message": "Validation error",
                "errors": {
                    "username": "A user with that username already exists.",
                },
            },
        )

    def test_create_user_without_fields_fail(self):

        for key in self.data:

            data = self.data.copy()
            del data[key]

            response = self.client.post(self.url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                response.data,
                {
                    "message": "Validation error",
                    "errors": {
                        key: "This field is required.",
                    },
                },
            )
