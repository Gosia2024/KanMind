from rest_framework.permissions import BasePermission

class IsBoardMemberOrOwner(BasePermission):
    """Allows access if the user is board owner or listed as a member."""
    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner or obj.members.filter(id=request.user.id).exists()

class IsBoardOwner(BasePermission):
    """Allows access only to the board owner."""
    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner
