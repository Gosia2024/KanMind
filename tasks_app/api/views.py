from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from tasks_app.models import Task, Comment
from .permissions import IsTaskBoardMember
from .serializers import TaskSerializer, CommentSerializer


class TaskViewSet(ModelViewSet):
    """
    POST /api/tasks/
    PATCH /api/tasks/{task_id}/
    DELETE /api/tasks/{task_id}/
    """
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsTaskBoardMember]

    def get_queryset(self):
        user = self.request.user
        return (
            Task.objects.filter(Q(board__owner=user) | Q(board__members=user))
            .distinct()
            .annotate(comments_count=Count("comments", distinct=True))
        )

    def destroy(self, request, *args, **kwargs):
        task = self.get_object()
        if not (task.created_by_id == request.user.id or task.board.owner_id == request.user.id):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


class AssignedToMeView(APIView):
    """
    GET /api/tasks/assigned-to-me/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Task.objects.filter(assignee=request.user).annotate(
            comments_count=Count("comments", distinct=True)
        )
        serializer = TaskSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)


class ReviewingView(APIView):
    """
    GET /api/tasks/reviewing/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Task.objects.filter(reviewer=request.user).annotate(
            comments_count=Count("comments", distinct=True)
        )
        serializer = TaskSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)


# -----------------------------
#       COMMENTS ENDPOINTS
# -----------------------------

class TaskCommentListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/tasks/<task_id>/comments/
    POST /api/tasks/<task_id>/comments/
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(
            task_id=self.kwargs["task_id"]
        ).order_by("created_at")

    def perform_create(self, serializer):
        task = get_object_or_404(Task, id=self.kwargs["task_id"])

        # User musi być członkiem boardu
        if not (task.board.owner == self.request.user or
                self.request.user in task.board.members.all()):
            raise PermissionDenied("You do not have access to this task.")

        serializer.save(
            author=self.request.user,
            task=task
        )


class TaskCommentDeleteView(generics.DestroyAPIView):
    """
    DELETE /api/tasks/<task_id>/comments/<comment_id>/
    """
    queryset = Comment.objects.all()
    lookup_url_kwarg = "comment_id"
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        task = instance.task

        
        if instance.author != self.request.user:
            raise PermissionDenied("You cannot delete this comment.")

        super().perform_destroy(instance)
