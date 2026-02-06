from rest_framework.permissions import BasePermission

class IsTaskBoardMember(BasePermission):
    """
    Allows access if the user is owner or member of the task's board.
    """
    def has_object_permission(self, request, view, obj):
        board = obj.board
        return request.user == board.owner or board.members.filter(id=request.user.id).exists()
