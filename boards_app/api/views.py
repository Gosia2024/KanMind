from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count

from boards_app.models import Board
from boards_app.api.permissions import IsBoardMemberOrOwner, IsBoardOwner
from .serializers import (
    BoardListSerializer,
    BoardDetailSerializer,
    BoardCreateUpdateSerializer,
    BoardUpdateResponseSerializer,
)
from django.db import models


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

    #  serializers
    def get_serializer_class(self):
        if self.action == "list":
            return BoardListSerializer

        if self.action == "retrieve":
            return BoardDetailSerializer

        if self.action in ["create", "update", "partial_update"]:
            return BoardCreateUpdateSerializer

        return BoardDetailSerializer

    #  update response
    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        serializer = BoardUpdateResponseSerializer(
            self.get_object(),
            context={"request": request},
        )
        return Response(serializer.data)

    # retrieve with comments_count
    def retrieve(self, request, *args, **kwargs):
        board = self.get_object()
        
        serializer = self.get_serializer(board)
        return Response(serializer.data)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        board = serializer.save()

        # annotate board to match documentation response
        board = (
            Board.objects
            .filter(id=board.id)
            .annotate(
                member_count=Count("members", distinct=True),
                ticket_count=Count("tasks", distinct=True),
                tasks_to_do_count=Count(
                    "tasks",
                    filter=models.Q(tasks__status="to-do"),
                    distinct=True,
                ),
                tasks_high_prio_count=Count(
                    "tasks",
                    filter=models.Q(tasks__priority="high"),
                    distinct=True,
                ),
            )
            .first()
        )

        response_serializer = BoardListSerializer(
            board,
            context={"request": request},
        )

        return Response(response_serializer.data, status=201)
