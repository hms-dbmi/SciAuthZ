from rest_framework import permissions
from django.contrib.auth.models import User

import logging
logger = logging.getLogger(__name__)


class IsAssociatedUser(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Is the user associated with the object the same as the user in the request.
        return obj.user == request.user


def jwt_get_username_from_payload(payload):
    """
    Method to create user in SciAuthZ Application if they don't exist.
    """

    print("Attempting to Authenticate User - " + payload.get('email'))

    try:
        User.objects.get(username=payload.get('email'))
    except User.DoesNotExist:

        print("User not found, creating.")

        user = User(username=payload.get('email'), email=payload.get('email'))
        user.is_staff = True
        user.is_superuser = True
        user.save()

    return payload.get('email')

