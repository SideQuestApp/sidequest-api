from rest_framework import permissions


class VerifiedUsersAccessOnly(permissions.BasePermission):
    """
    * Custom permission to allow only verified users to access certain views
    """
    def has_permission(self, request, view):
        if request.user.is_verified:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_verified:
            return True
        return False


class PremiumUsersAccessOnly(permissions.BasePermission):
    """
    * Custom permission to allow only verified users to access certain views
    """
    def has_permission(self, request, view):
        if request.user.premium is True:
            return True

    def has_object_permission(self, request, view, obj):
        if request.user.premium is True:
            return True
