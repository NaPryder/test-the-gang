from rest_framework.permissions import BasePermission

from common.models import Profile


class AdminOrStaffPermission(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return Profile.has_admin_role(request.user) or Profile.has_staff_role(
                request.user
            )
        return False


class CustomerAccessPermission(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return Profile.has_customer_role(request.user)
        return False

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "owner"):
            return obj.owner == request.user

        return False
