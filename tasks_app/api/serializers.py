from django.contrib.auth import get_user_model
from rest_framework import serializers

from boards_app.models import Board
from tasks_app.models import Task, Comment

User = get_user_model()


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "fullname"]


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer used for:
    - GET /api/tasks/{task_id}/comments/
    - POST /api/tasks/{task_id}/comments/

    return:
    {
        "id": 1,
        "created_at": "...",
        "author": "Max Mustermann",
        "content": "..."
    }
    """
    author = serializers.CharField(source="author.fullname", read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "created_at", "author", "content"]
        read_only_fields = ["id", "created_at", "author"]


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for creating, updating and displaying tasks.
    Handles assignee/reviewer as user IDs in requests
    and nested user objects in responses.
    """
    assignee = UserPublicSerializer(read_only=True)
    reviewer = UserPublicSerializer(read_only=True)

    assignee_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)
    reviewer_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)

    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "reviewer",
            "assignee_id",
            "reviewer_id",
            "due_date",
            "comments_count",
        ]

    def validate_board(self, value: Board):
        user = self.context["request"].user
        if not (value.owner_id == user.id or value.members.filter(id=user.id).exists()):
            raise serializers.ValidationError("You must be a member of this board.")
        return value

    def _validate_user_is_board_member(self, board: Board, user_id):
        if user_id is None:
            return None
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")

        if not (board.owner_id == user.id or board.members.filter(id=user.id).exists()):
            raise serializers.ValidationError("Assignee/Reviewer must be member of the board.")
        return user

    def create(self, validated_data):
        """Creates a new task and assigns assignee/reviewer if provided."""
        assignee_id = validated_data.pop("assignee_id", None)
        reviewer_id = validated_data.pop("reviewer_id", None)

        board = validated_data["board"]
        assignee = self._validate_user_is_board_member(board, assignee_id)
        reviewer = self._validate_user_is_board_member(board, reviewer_id)

        task = Task.objects.create(
            created_by=self.context["request"].user,
            assignee=assignee,
            reviewer=reviewer,
            **validated_data,
        )
        return task

    def update(self, instance, validated_data):
        """Updates task fields. Board field cannot be changed."""
        if "board" in validated_data:
            validated_data.pop("board")

        assignee_id = validated_data.pop("assignee_id", None) if "assignee_id" in validated_data else "keep"
        reviewer_id = validated_data.pop("reviewer_id", None) if "reviewer_id" in validated_data else "keep"

        for field, value in validated_data.items():
            setattr(instance, field, value)

        board = instance.board
        if assignee_id != "keep":
            instance.assignee = self._validate_user_is_board_member(board, assignee_id)
        if reviewer_id != "keep":
            instance.reviewer = self._validate_user_is_board_member(board, reviewer_id)

        instance.save()
        return instance


    comments_count = serializers.IntegerField(read_only=True)
