# Permission classes for API views and role-based access control.
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsPortfolioOwnerOrReadOnly(BasePermission):
    # Only portfolio superuser can mutate; public can read.
    message = "Only the portfolio owner can change items."

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_superuser


class IsPortfolioOwnerOrEditorOrReadOnly(BasePermission):
    # Superuser has full access; Editor group can PUT/PATCH; public can read.
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return (
            request.method in ("PUT", "PATCH")
            and request.user.groups.filter(name="Editor").exists()
        )
