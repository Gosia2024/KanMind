from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    AssignedToMeView,
    ReviewingView,
    TaskViewSet,
    TaskCommentListCreateView,
    TaskCommentDeleteView,
)

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="tasks")
urlpatterns = [
    path("tasks/assigned-to-me/", AssignedToMeView.as_view(), name="tasks-assigned-to-me"),
    path("tasks/reviewing/", ReviewingView.as_view(), name="tasks-reviewing"),
    path("", include(router.urls)),
    path("tasks/<int:task_id>/comments/", TaskCommentListCreateView.as_view(), name="task-comments"),
    path("tasks/<int:task_id>/comments/<int:comment_id>/", TaskCommentDeleteView.as_view(), name="task-comment-delete"),
]
