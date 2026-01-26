from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


User = get_user_model()


class AuthenticationTests(APITestCase):
    def setUp(self):
        self.registration_url = "/api/registration/"
        self.login_url = "/api/login/"
        self.email_check_url = "/api/email-check/"

        self.user_data = {
            "fullname": "Test User",
            "email": "test@example.com",
            "password": "StrongPass123!",
            "repeated_password": "StrongPass123!",
        }

        self.user = User.objects.create_user(
            email="existing@example.com",
            fullname="Existing User",
            password="ExistingPass123!",
        )
        self.token = Token.objects.create(user=self.user)

    # --------------------
    # REGISTRATION
    # --------------------
    def test_registration_success(self):
        response = self.client.post(self.registration_url, self.user_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["email"], self.user_data["email"])
        self.assertTrue(User.objects.filter(email=self.user_data["email"]).exists())

    def test_registration_password_mismatch(self):
        data = self.user_data.copy()
        data["repeated_password"] = "WrongPassword123!"

        response = self.client.post(self.registration_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("repeated_password", response.data)

    def test_registration_email_already_exists(self):
        data = self.user_data.copy()
        data["email"] = "existing@example.com"

        response = self.client.post(self.registration_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    # --------------------
    # LOGIN
    # --------------------
    def test_login_success(self):
        response = self.client.post(
            self.login_url,
            {
                "email": "existing@example.com",
                "password": "ExistingPass123!",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["email"], "existing@example.com")

    def test_login_invalid_password(self):
        response = self.client.post(
            self.login_url,
            {
                "email": "existing@example.com",
                "password": "WrongPassword!",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --------------------
    # EMAIL CHECK
    # --------------------
    def test_email_check_authenticated_success(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

        response = self.client.get(
            self.email_check_url, {"email": "existing@example.com"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "existing@example.com")

    def test_email_check_unauthenticated(self):
        response = self.client.get(
            self.email_check_url, {"email": "existing@example.com"}
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_email_check_not_found(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

        response = self.client.get(
            self.email_check_url, {"email": "doesnotexist@example.com"}
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

