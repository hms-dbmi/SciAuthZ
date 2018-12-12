from datetime import datetime

from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.decorators import list_route
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from authorization.serializers import UserPermissionSerializer
from authorization.serializers import UserSerializer
from authorization.models import UserPermission
from authorization.models import UserPermissionRequest

from pyauth0jwt.auth0authenticate import user_auth_and_jwt
from pyauth0jwtrest.utils import get_email_from_request

from django.http import HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

import logging
logger = logging.getLogger(__name__)

@user_auth_and_jwt
def login(request):
    """
    Method exists only to enable access to admin panel which requires session auth.
    """
    return HttpResponse("LOGGED IN.")

def get_authorized_user_permissions(requesting_user, requested_user=None, record_id=None, item=None):
    """
    Returns a QuerySet of UserPermission records that the requesting_user is authorized to see. A request
    can include a requested_user (permissions that someone else has), a record_id (the ID of a UserPermission),
    or an item (the permission string). If the request does not include any of these parameters, only the
    permissions that pertain to the user should be returned.
    """

    if not requested_user and not record_id and not item:
        return UserPermission.objects.filter(user_email=requesting_user)

    permission_records = UserPermission.objects.all()

    # Get all the possible records the user is requesting
    if requested_user:
        permission_records = permission_records.filter(user_email=requested_user)
    if record_id:
        permission_records = permission_records.filter(id=record_id)
    if item:
        permission_records = permission_records.filter(item=item)

    # Get a list of all the items that the user manages
    manage_permissions = UserPermission.objects.filter(user_email=requesting_user, permission="MANAGE")
    managing_items = list(manage_permissions.values_list('item', flat=True).distinct())

    # Check that the user either owns the record or has MANAGE permissions on such an item
    for record in permission_records:
        if record.user_email.lower() != requesting_user.lower() and record.item not in managing_items:
            permission_records = permission_records.exclude(id=record.id)

    return permission_records

def get_email_from_jwt(request):
    """
    This function encapsulates the pyauth0jwtrest.utils.get_email_from_request() function
    to make it easier to mock it in our unit tests.
    """

    return get_email_from_request(request)

class UserPermissionViewSet(viewsets.ModelViewSet):
    """
    API View for UserPermission Model.
    """
    queryset = UserPermission.objects.all()
    serializer_class = UserPermissionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):

        # Get the username (email) from the JWT
        request_by_email = get_email_from_jwt(self.request)

        # All the possible parameters we will accept
        record_id = self.request.query_params.get('id', None)
        item = self.request.query_params.get('item', None)
        requested_user = self.request.query_params.get('email', None)

        return get_authorized_user_permissions(request_by_email, requested_user, record_id, item)

    @list_route(methods=['post'])
    def create_item_view_permission_record(self, request):
        """
        Creates a VIEW UserPermission record to a given project for a given user.
        """

        # Get the username (email) from the JWT
        request_by_email = get_email_from_jwt(self.request)

        # The person getting the VIEW permission
        grantee = request.data['grantee_email']
        item = request.data['item']
        object_permission = "VIEW"

        logger.debug('[DEBUG][SCIAUTHZ][create_item_view_permission_record] - Attempting to create VIEW permission on item %s for user %s, authorized by %s.' % (item, grantee, request_by_email))

        # If the user does not have MANAGE permissions of the item, return 401
        if UserPermission.objects.filter(item=item, user_email=request_by_email, permission="MANAGE").count() < 1:
            logger.debug('[DEBUG][SCIAUTHZ][create_item_view_permission_record] - Failed to create VIEW permission. %s is not authorized to do this.' % request_by_email)
            return Response('User is not authorized to create this permission.', status=status.HTTP_401_UNAUTHORIZED)

        # Add the permission if it does not exist
        new_user_permission, created = UserPermission.objects.get_or_create(
            item=item,
            user_email=grantee,
            permission=object_permission
        )

        logger.debug('[DEBUG][SCIAUTHZ][create_item_view_permission_record] - Sucessfully created VIEW permission for %s on %s.' % (grantee, item))

        serializer = self.get_serializer(new_user_permission)
        return Response(serializer.data)

    @list_route(methods=['post'])
    def remove_item_view_permission_record(self, request):
        """
        Removes a VIEW UserPermission record from a given user for a given project.
        """

        # Get the username (email) from the JWT
        request_by_email = get_email_from_jwt(self.request)

        # The person getting the VIEW permission
        grantee = request.data['grantee_email']
        item = request.data['item']
        object_permission = "VIEW"

        logger.debug('[DEBUG][SCIAUTHZ][remove_item_view_permission_record] - Removing VIEW permission on item %s for user %s, authorized by %s.' % (item, grantee, request_by_email))

        # If the user does not have MANAGE permissions of the item, return 401
        if UserPermission.objects.filter(item=item, user_email=request_by_email, permission="MANAGE").count() < 1:
            logger.debug('[DEBUG][SCIAUTHZ][remove_item_view_permission_record] - Failed to remove VIEW permission. %s is not authorized to do this.' % request_by_email)
            return Response('User is not authorized to remove this permission.', status=status.HTTP_401_UNAUTHORIZED)

        # Remove the permission if it exists
        permission = get_object_or_404(UserPermission, item=item, user_email=grantee, permission=object_permission)
        permission.delete()

        logger.debug('[DEBUG][SCIAUTHZ][remove_item_view_permission_record] - Removed %s' % permission)

        serializer = self.get_serializer(permission)
        return Response(serializer.data)

    @list_route(methods=['post'])
    def create_registration_permission_record(self, request):
        """
        Creates a VIEW UserPermission record for the requesting user's SciReg profile to the given user.
        Permission checks are not needed because by the nature of sending this request, the user is voluntarily
        granting someone access to the SciReg profile
        """

        # Get the username (email) from the JWT
        request_by_email = get_email_from_jwt(self.request)

        grantee = request.data['grantee_email']
        item = request.data['item']

        item_permission_string = "SciReg." + item + ".profile." + request_by_email
        object_permission = "VIEW"

        logger.debug('[DEBUG][SCIAUTHZ][create_registration_permission_record] - Creating {object} {perm} permission for user {user}.'.format(
            object=item_permission_string,
            perm=object_permission,
            user=grantee
        ))

        grantee_user, created = User.objects.get_or_create(username=grantee, email=grantee)

        if created:
            logger.debug('[DEBUG][SCIAUTHZ][create_registration_permission_record] - Created Grantee %s' % grantee_user)

        new_user_permission, created = UserPermission.objects.get_or_create(
            item=item_permission_string,
            user_email=grantee,
            permission=object_permission,
            date_updated=datetime.now()
        )

        logger.debug('[DEBUG][SCIAUTHZ][create_registration_permission_record] - Created %s' % new_user_permission)

        serializer = self.get_serializer(new_user_permission)
        return Response(serializer.data)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API View for User Model.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(email=user.email)


