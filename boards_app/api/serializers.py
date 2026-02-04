from django.contrib.auth import get_user_model
from rest_framework import serializers
from boards_app.models import Board
from tasks_app.api.serializers import TaskSerializer

User = get_user_model()


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "fullname"]


class BoardListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing boards.
    Includes aggregated counters like members and tasks.
    """
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
    """
    Serializer for creating and updating boards.
    Handles member assignment.
    """
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=False,
    )

    class Meta:
        model = Board
        fields = ["title", "members"]

    def create(self, validated_data):
        members = validated_data.pop("members", [])
        board = Board.objects.create(
            owner=self.context["request"].user,
            **validated_data,
        )
        board.members.set(members)
        return board

    def update(self, instance, validated_data):
        members = validated_data.pop("members", None)
        instance.title = validated_data.get("title", instance.title)
        instance.save()

        if members is not None:
            instance.members.set(members)
        return instance


# class BoardDetailSerializer(serializers.ModelSerializer):
#     members = UserPublicSerializer(many=True, read_only=True)
#     tasks = serializers.SerializerMethodField()

#     class Meta:
#         model = Board
#         fields = [
#             "id",
#             "title",
#             "owner_id",
#             "members",
#             "tasks",
#         ]

#     def get_tasks(self, obj):
#         tasks = self.context.get("tasks", obj.tasks.all())
#         return TaskSerializer(tasks, many=True).data

# class BoardUpdateResponseSerializer(serializers.ModelSerializer):
#     """
#     Serializer used as response after board update.
#     """
#     owner_data = UserPublicSerializer(source="owner", read_only=True)
#     members_data = UserPublicSerializer(source="members", many=True, read_only=True)

#     class Meta:
#         model = Board
#         fields = ["id", "title", "owner_data", "members_data"]
class BoardDetailSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)
    members = UserPublicSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "owner_id",
            "members",
            "tasks",
        ]
