from django.db.models import Count, Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from boards_app.models import Board
from .permissions import IsBoardMemberOrOwner, IsBoardOwner
from .serializers import BoardCreateUpdateSerializer, BoardDetailSerializer, BoardListSerializer


class BoardViewSet(ModelViewSet):
    """
    CRUD endpoints for boards.

    Access rules:
    - list/create: authenticated users
    - retrieve/update: board member or owner
    - delete: owner only
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()

        # annotate counts for list/create responses
        return qs.annotate(
            member_count=Count("members", distinct=True),
            ticket_count=Count("tasks", distinct=True),
            tasks_to_do_count=Count("tasks", filter=Q(tasks__status="to-do"), distinct=True),
            tasks_high_prio_count=Count("tasks", filter=Q(tasks__priority="high"), distinct=True),
        )

    def get_serializer_class(self):
        if self.action in ["list"]:
            return BoardListSerializer
        if self.action in ["retrieve"]:
            return BoardDetailSerializer
        return BoardCreateUpdateSerializer

    def get_permissions(self):
        if self.action == "destroy":
            return [IsAuthenticated(), IsBoardOwner()]
        if self.action in ["retrieve", "partial_update"]:
            return [IsAuthenticated(), IsBoardMemberOrOwner()]
        return [IsAuthenticated()]
