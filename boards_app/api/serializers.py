from django.contrib.auth import get_user_model
from rest_framework import serializers

from boards_app.models import Board

User = get_user_model()


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "fullname"]


class BoardListSerializer(serializers.ModelSerializer):
    """Serializer for GET /api/boards/{id}/ (board + members)."""
    member_count = serializers.IntegerField(read_only=True)
    ticket_count = serializers.IntegerField(read_only=True)
    tasks_to_do_count = serializers.IntegerField(read_only=True)
    tasks_high_prio_count = serializers.IntegerField(read_only=True)
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "member_count",
            "ticket_count",
            "tasks_to_do_count",
            "tasks_high_prio_count",
            "owner_id",
        ]


class BoardCreateUpdateSerializer(serializers.ModelSerializer):
    members = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
    )

    class Meta:
        model = Board
        fields = ["title", "members"]

    def validate_members(self, value):
        # ensure all users exist
        if not value:
            return []
        existing = set(User.objects.filter(id__in=value).values_list("id", flat=True))
        missing = [user_id for user_id in value if user_id not in existing]
        if missing:
            raise serializers.ValidationError(f"Invalid user ids: {missing}")
        return value

    def create(self, validated_data):
        members_ids = validated_data.pop("members", [])
        board = Board.objects.create(owner=self.context["request"].user, **validated_data)
        if members_ids:
            board.members.set(members_ids)
        return board

    def update(self, instance, validated_data):
        members_ids = validated_data.pop("members", None)
        instance.title = validated_data.get("title", instance.title)
        instance.save()

        if members_ids is not None:
            instance.members.set(members_ids)
        return instance


class BoardDetailSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)
    members = UserPublicSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ["id", "title", "owner_id", "members"]
