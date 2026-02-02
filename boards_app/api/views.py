from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q

from boards_app.models import Board
from boards_app.api.permissions import IsBoardMemberOrOwner, IsBoardOwner
from .serializers import (
    BoardListSerializer,
    BoardCreateUpdateSerializer,
)


class BoardViewSet(ModelViewSet):
    queryset = Board.objects.all()

    # permissions
    def get_permissions(self):
        if self.action in ["list", "create"]:
            return [IsAuthenticated()]
        if self.action in ["retrieve", "update", "partial_update"]:
            return [IsAuthenticated(), IsBoardMemberOrOwner()]
        if self.action == "destroy":
            return [IsAuthenticated(), IsBoardOwner()]
        return super().get_permissions()

    # serializers
    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return BoardListSerializer
        if self.action in ["create", "update", "partial_update"]:
            return BoardCreateUpdateSerializer
        return BoardListSerializer

    # GET /api/boards/
    def get_queryset(self):
        if self.action in ["list", "retrieve"]:
            return (
                Board.objects
                .filter(
                    Q(owner=self.request.user) |
                    Q(members=self.request.user)
                )
                .annotate(
                    member_count=Count("members", distinct=True),
                    ticket_count=Count("tasks", distinct=True),
                    tasks_to_do_count=Count(
                        "tasks",
                        filter=Q(tasks__status="to-do"),
                        distinct=True,
                    ),
                    tasks_high_prio_count=Count(
                        "tasks",
                        filter=Q(tasks__priority="high"),
                        distinct=True,
                    ),
                )
                .distinct()
            )
        return Board.objects.all()

    # POST /api/boards/
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board = serializer.save()

        board = (
            Board.objects
            .filter(id=board.id)
            .annotate(
                member_count=Count("members", distinct=True),
                ticket_count=Count("tasks", distinct=True),
                tasks_to_do_count=Count(
                    "tasks",
                    filter=Q(tasks__status="to-do"),
                    distinct=True,
                ),
                tasks_high_prio_count=Count(
                    "tasks",
                    filter=Q(tasks__priority="high"),
                    distinct=True,
                ),
            )
            .first()
        )

        return Response(
            BoardListSerializer(board, context={"request": request}).data,
            status=201
        )

    # PATCH /api/boards/{id}/
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        instance = (
            Board.objects
            .filter(id=instance.id)
            .annotate(
                member_count=Count("members", distinct=True),
                ticket_count=Count("tasks", distinct=True),
                tasks_to_do_count=Count(
                    "tasks",
                    filter=Q(tasks__status="to-do"),
                    distinct=True,
                ),
                tasks_high_prio_count=Count(
                    "tasks",
                    filter=Q(tasks__priority="high"),
                    distinct=True,
                ),
            )
            .first()
        )

        return Response(
            BoardListSerializer(instance, context={"request": request}).data
        )
