from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from boards_app.models import Board

User = get_user_model()


class BoardTests(APITestCase):
    def setUp(self):
        # users
        self.owner = User.objects.create_user(
            email="owner@test.com",
            fullname="Owner",
            password="OwnerPass123!",
        )
        self.member = User.objects.create_user(
            email="member@test.com",
            fullname="Member",
            password="MemberPass123!",
        )
        self.other_user = User.objects.create_user(
            email="other@test.com",
            fullname="Other",
            password="OtherPass123!",
        )

        self.owner_token = Token.objects.create(user=self.owner)
        self.member_token = Token.objects.create(user=self.member)
        self.other_token = Token.objects.create(user=self.other_user)

        # board
        self.board = Board.objects.create(
            title="Test Board",
            owner=self.owner,
        )
        self.board.members.add(self.member)

        self.boards_url = "/api/boards/"
        self.board_detail_url = f"/api/boards/{self.board.id}/"

    # --------------------
    # GET /api/boards/
    # --------------------
    def test_board_list_authenticated(self):
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + self.owner_token.key
        )

        response = self.client.get(self.boards_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_board_list_unauthenticated(self):
        response = self.client.get(self.boards_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --------------------
    # POST /api/boards/
    # --------------------
    def test_create_board_success(self):
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + self.owner_token.key
        )

        response = self.client.post(
            self.boards_url,
            {
                "title": "New Board",
                "members": [self.member.id],
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "New Board")

    def test_create_board_unauthenticated(self):
        response = self.client.post(
            self.boards_url,
            {"title": "Fail Board"},
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --------------------
    # GET /api/boards/{id}/
    # --------------------
    def test_board_detail_owner(self):
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + self.owner_token.key
        )

        response = self.client.get(self.board_detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.board.title)

    def test_board_detail_member(self):
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + self.member_token.key
        )

        response = self.client.get(self.board_detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_board_detail_forbidden(self):
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + self.other_token.key
        )

        response = self.client.get(self.board_detail_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --------------------
    # PATCH /api/boards/{id}/
    # --------------------
    def test_update_board_title(self):
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + self.owner_token.key
        )

        response = self.client.patch(
            self.board_detail_url,
            {"title": "Changed title"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Changed title")

    # --------------------
    # DELETE /api/boards/{id}/
    # --------------------
    def test_delete_board_owner(self):
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + self.owner_token.key
        )

        response = self.client.delete(self.board_detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Board.objects.filter(id=self.board.id).exists())

    def test_delete_board_not_owner(self):
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + self.member_token.key
        )

        response = self.client.delete(self.board_detail_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)



