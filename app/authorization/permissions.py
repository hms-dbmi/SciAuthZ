from rest_framework import permissions
from django.contrib.auth.models import User
from .models import UserPermission

import logging
logger = logging.getLogger(__name__)

class IsAssociatedUser(permissions.BasePermission):
    """
    Custom permission to only allow users associated with an object or users with "MANAGER" permissions to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Is the user associated with the object the same as the user in the request.
        if obj.user == request.user:
            return True
        # Check to see if the user has "MANAGE" permissions on this kind of item
        else:
            if UserPermission.objects.filter(item=obj.item, user=request.user, permission="MANAGE").count() >= 1:
                return True
            else:
                return False


def jwt_get_username_from_payload(payload):
    """
    Method to create user in SciAuthZ Application if they don't exist.
    """

    logger.debug("[SCIAUTHZ][DEBUG] jwt_get_username_from_payload: attempting to authenticate user - " + payload.get('email'))

    try:
        User.objects.get(username=payload.get('email'))
    except User.DoesNotExist:

        logger.debug("[SCIAUTHZ][DEBUG] jwt_get_username_from_payload: User not found, creating.")

        user = User(username=payload.get('email'), email=payload.get('email'))
        user.save()

    return payload.get('email')

