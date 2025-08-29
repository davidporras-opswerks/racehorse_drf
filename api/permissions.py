from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrSelf(BasePermission):
    """
    Allow access if the user is admin or accessing their own object.
    """
    def has_object_permission(self, request, view, obj):
        # Allow safe methods (GET, HEAD, OPTIONS)
        if request.method in SAFE_METHODS:
            return True
        # Allow admin
        if request.user.is_staff:
            return True
        # Allow user to modify their own account
        return obj == request.user
