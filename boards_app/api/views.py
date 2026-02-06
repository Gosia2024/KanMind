from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q

from boards_app.models import Board
from boards_app.api.permissions import IsBoardMemberOrOwner, IsBoardOwner
from .serializers import (
    BoardDetailSerializer,
    BoardListSerializer,
    BoardCreateUpdateSerializer,
    BoardUpdateResponseSerializer,
)
from rest_framework import status


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

    # # serializers
    # def get_serializer_class(self):
    #     if self.action in ["list", "retrieve"]:
    #         return BoardListSerializer
    #     if self.action in ["create", "update", "partial_update"]:
    #         return BoardCreateUpdateSerializer
    #     return BoardListSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return BoardListSerializer
        if self.action == "retrieve":
            return BoardDetailSerializer
        if self.action in ["create", "update", "partial_update"]:
            return BoardCreateUpdateSerializer
        return BoardListSerializer


    # # GET /api/boards/
    # def get_queryset(self):
    #     if self.action in ["list", "retrieve"]:
    #         return (
    #             Board.objects
    #             .filter(
    #                 Q(owner=self.request.user) |
    #                 Q(members=self.request.user)
    #             )
    #             .annotate(
    #                 member_count=Count("members", distinct=True),
    #                 ticket_count=Count("tasks", distinct=True),
    #                 tasks_to_do_count=Count(
    #                     "tasks",
    #                     filter=Q(tasks__status="to-do"),
    #                     distinct=True,
    #                 ),
    #                 tasks_high_prio_count=Count(
    #                     "tasks",
    #                     filter=Q(tasks__priority="high"),
    #                     distinct=True,
    #                 ),
    #             )
    #             .distinct()
    #         )
    #     return Board.objects.all()
    def get_queryset(self):
    #  if self.action == "list":
    #     return (
    #         Board.objects
    #         .filter(
    #             Q(owner=self.request.user) |
    #             Q(members=self.request.user)
    #         )
    #         .annotate(
    #             member_count=Count("members", distinct=True),
    #             ticket_count=Count("tasks", distinct=True),
    #             tasks_to_do_count=Count(
    #                 "tasks",
    #                 filter=Q(tasks__status="to-do"),
    #                 distinct=True,
    #             ),
    #             tasks_high_prio_count=Count(
    #                 "tasks",
    #                 filter=Q(tasks__priority="high"),
    #                 distinct=True,
    #             ),
    #         )
    #         .distinct()
    #     )

    # DLA retrieve / update / patch / delete
    
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

    # # PATCH /api/boards/{id}/
    # def update(self, request, *args, **kwargs):
    #     partial = kwargs.pop("partial", False)
    #     instance = self.get_object()

    #     serializer = self.get_serializer(
    #         instance,
    #         data=request.data,
    #         partial=partial
    #     )
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)

    #     instance = (
    #         Board.objects
    #         .filter(id=instance.id)
    #         .annotate(
    #             member_count=Count("members", distinct=True),
    #             ticket_count=Count("tasks", distinct=True),
    #             tasks_to_do_count=Count(
    #                 "tasks",
    #                 filter=Q(tasks__status="to-do"),
    #                 distinct=True,
    #             ),
    #             tasks_high_prio_count=Count(
    #                 "tasks",
    #                 filter=Q(tasks__priority="high"),
    #                 distinct=True,
    #             ),
    #         )
    #         .first()
    #     )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        # request 
        input_serializer = BoardCreateUpdateSerializer(
            instance,
            data=request.data,
            partial=partial,
            context={"request": request},
        )
        input_serializer.is_valid(raise_exception=True)
        input_serializer.save()

        # response
        output_serializer = BoardUpdateResponseSerializer(instance)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

      
      
    def list(self, request, *args, **kwargs):
        queryset = (
        Board.objects
        .filter(
        Q(owner=request.user) |
        Q(members=request.user)
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

        serializer = BoardListSerializer(queryset, many=True)
        return Response(serializer.data)
