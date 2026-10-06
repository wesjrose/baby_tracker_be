from rest_framework.permissions import BasePermission

from .models import GuardianMapping


class isGuardian(BasePermission):
    message = "You are not a guardian of this baby."

    def has_object_permission(self, request, view, obj):
        return GuardianMapping.objects.filter(baby=obj, guardian=request.user).exists()
