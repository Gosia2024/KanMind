from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from boards_app.models import Board
from tasks_app.models import Task, Comment

User = get_user_model()


class TaskTests(APITestCase):
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
        self.other = User.objects.create_user(
            email="other@test.com",
            fullname="Other",
            password="OtherPass123!",
        )

        self.owner_token = Token.objects.create(user=self.owner)
        self.member_token = Token.objects.create(user=self.member)
        self.other_token = Token.objects.create(user=self.other)

        # board
        self.board = Board.objects.create(
            title="Board",
            owner=self.owner,
        )
        self.board.members.add(self.member)

        # task
        self.task = Task.objects.create(
            board=self.board,
            title="Task 1",
            description="Desc",
            status="to-do",
            priority="high",
            assignee=self.member,
            reviewer=self.owner,
            created_by=self.owner,
        )

        # urls
        self.tasks_url = "/api/tasks/"
        self.task_detail_url = f"/api/tasks/{self.task.id}/"
        self.assigned_to_me_url = "/api/tasks/assigned-to-me/"
        self.reviewing_url = "/api/tasks/reviewing/"
        self.comments_url = f"/api/tasks/{self.task.id}/comments/"

    # --------------------
    # GET /api/tasks/assigned-to-me/
    # --------------------
    def test_assigned_to_me_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.member_token.key)

        response = self.client.get(self.assigned_to_me_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_assigned_to_me_unauthenticated(self):
        response = self.client.get(self.assigned_to_me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --------------------
    # GET /api/tasks/reviewing/
    # --------------------
    def test_reviewing_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.owner_token.key)

        response = self.client.get(self.reviewing_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_reviewing_unauthenticated(self):
        response = self.client.get(self.reviewing_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --------------------
    # POST /api/tasks/
    # --------------------
    def test_create_task_success(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.owner_token.key)

        response = self.client.post(
            self.tasks_url,
            {
                "board": self.board.id,
                "title": "New Task",
                "description": "Test",
                "status": "review",
                "priority": "medium",
                "assignee_id": self.member.id,
                "reviewer_id": self.owner.id,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "New Task")

    def test_create_task_forbidden_not_board_member(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.other_token.key)

        response = self.client.post(
            self.tasks_url,
            {
                "board": self.board.id,
                "title": "Fail Task",
                "status": "to-do",
                "priority": "low",
            },
        )

        self.assertIn(
    response.status_code,
    [status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN]
)


    # --------------------
    # PATCH /api/tasks/{id}/
    # --------------------
    def test_update_task_success(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.member_token.key)

        response = self.client.patch(
            self.task_detail_url,
            {"status": "done"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "done")

    def test_update_task_forbidden(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.other_token.key)

        response = self.client.patch(
            self.task_detail_url,
            {"status": "done"},
        )

        self.assertIn(
    response.status_code,
    [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
)


    # --------------------
    # DELETE /api/tasks/{id}/
    # --------------------
    def test_delete_task_owner(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.owner_token.key)

        response = self.client.delete(self.task_detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())

    def test_delete_task_forbidden(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.member_token.key)

        response = self.client.delete(self.task_detail_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --------------------
    # COMMENTS
    # --------------------
    def test_create_comment_success(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.member_token.key)

        response = self.client.post(
            self.comments_url,
            {"content": "New comment"},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["content"], "New comment")

    def test_delete_comment_only_author(self):
        comment = Comment.objects.create(
            task=self.task,
            author=self.member,
            content="Test comment",
        )

        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.member_token.key)

        response = self.client.delete(
            f"/api/tasks/{self.task.id}/comments/{comment.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

