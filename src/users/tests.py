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


class UserAuthenticationTest(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url_token = reverse("token_obtain_pair")
        cls.url_token_refresh = reverse("token_refresh")
        cls.url_token_verify = reverse("token_verify")

        cls.existing_user_auth_data = {
            "username": "existing_user",
            "password": "strongpassword123",
        }

        existing_user_data = {
            "first_name": "Existing",
            "last_name": "user",
            "email": "test@existing.com",
        } | cls.existing_user_auth_data

        User.objects.create_user(**existing_user_data)

        cls.nonexisting_user_auth_data = {
            "username": "testuser",
            "password": "strongpassword123",
        }

    def test_authenticate_nonexistent_user_fail(self):
        response = self.client.post(self.url_token, self.nonexisting_user_auth_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {"message": "No active account found with the given credentials"})

    def test_authenticate_user_success(self):
        response = self.client.post(self.url_token, self.existing_user_auth_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.__class__.refresh = response.data["refresh"]
        self.__class__.access = response.data["access"]

    def test_verify_extistent_token_success(self):
        for key in ["refresh", "access"]:
            response = self.client.post(self.url_token_verify, {"token": getattr(self, key)}, format="json")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data, {})

    def test_refresh_with_refresh_token_success(self):
        response = self.client.post(self.url_token_refresh, {"refresh": self.refresh}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

        response = self.client.post(self.url_token_verify, {"token": response.data["access"]}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})

    def test_refresh_with_access_token_fail(self):
        response = self.client.post(self.url_token_refresh, {"refresh": self.access}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data,
            {"message": "Validation error", "errors": {"detail": "Token has wrong type", "code": "token_not_valid"}},
        )

    def test_verify_non_extistent_token_fail(self):
        response = self.client.post(self.url_token_verify, {"token": "Test"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data,
            {"message": "Validation error", "errors": {"detail": "Token is invalid", "code": "token_not_valid"}},
        )
