from rest_framework import viewsets, permissions, generics
from rest_framework.decorators import detail_route
from authorization.serializers import UserPermissionSerializer
from authorization.serializers import UserSerializer
from authorization.serializers import PermissionRequestSerializer
from authorization.models import UserPermission
from authorization.models import UserPermissionRequest
from django.contrib.auth.models import User
from authorization.permissions import IsAssociatedUser
from pyauth0jwt.auth0authenticate import user_auth_and_jwt
from django.http import HttpResponse

from rest_framework.decorators import list_route
from rest_framework.response import Response
from datetime import datetime

import logging
logger = logging.getLogger(__name__)

@user_auth_and_jwt
def login(request):
    return HttpResponse("SENT")


def get_objects_with_permissions(requested_object_type, requesting_user, requested_user, record_id=None, item=None):
    # If a specific record is requested, confirm the requesting user either is the owner of it or
    # has MANAGE permissions on that kind of item
    if record_id is not None:
        # DRF requires we return a QuerySet
        record_resultset = requested_object_type.objects.filter(id=record_id)

        if record_resultset is None or record_resultset.count() == 0:
            return requested_object_type.objects.none()

        # There should only be one record since we searched by ID
        record = record_resultset[0]

        # Is the requesting user the owner of this record? DRF requires we preserve this as a queryset.
        if record.user.email == requesting_user.email:
            return record_resultset
        elif UserPermission.objects.filter(item=record.item, user=requesting_user, permission="MANAGE").count() >= 1:
            return record_resultset
        else:
            return requested_object_type.objects.none()

    # If an item is specified, check if the user has MANAGE permissions on that item
    elif item is not None:
        if UserPermission.objects.filter(item=item, user=requesting_user, permission="MANAGE").count() >= 1:
            # If a specific user was specified, return all permissions it has for this item
            if requested_user is not None:
                return requested_object_type.objects.filter(user__email__iexact=requested_user, item__iexact=item)
            # Otherwise, return everyone's permissions for this item
            else:
                return requested_object_type.objects.filter(item__iexact=item)
        # If this person does not have MANAGE permissions, then only return permissions for this item that they own
        else:
            return requested_object_type.objects.filter(user=requesting_user, item__iexact=item)

    # If no record ID or item was specified, then return only the objects for which the user owns
    else:
        return requested_object_type.objects.filter(user=requesting_user)


class UserPermissionViewSet(viewsets.ModelViewSet):
    """
    API View for UserPermission Model.
    """
    queryset = UserPermission.objects.all()
    serializer_class = UserPermissionSerializer
    permission_classes = (permissions.IsAuthenticated, IsAssociatedUser,)

    def get_queryset(self):

        # All the possible parameters we will accept
        record_id = self.request.query_params.get('id', None)
        item = self.request.query_params.get('item', None)
        requested_user = self.request.query_params.get('email', None)
        requesting_user = self.request.user

        return get_objects_with_permissions(UserPermission, requesting_user, requested_user, record_id, item)

    @list_route(methods=['post'])
    def create_registration_permission_record(self, request):

        grantee = request.data['grantee_email']

        logger.debug('[DEBUG][SCIAUTHZ][create_registration_permission_record] - Creating profile permission for user %s' % request.user.email)

        item_permission_string = "SciReg.n2c2.profile." + request.user.email
        object_permission = "VIEW"

        grantee_user, created = User.objects.get_or_create(username=grantee, email=grantee)

        if created:
            logger.debug('[DEBUG][SCIAUTHZ][create_registration_permission_record] - Created Grantee %s' % grantee_user)

        new_user_permission, created = UserPermission.objects.get_or_create(item=item_permission_string,
                                                                            user=grantee_user,
                                                                            permission=object_permission,
                                                                            date_updated=datetime.now())

        logger.debug('[DEBUG][SCIAUTHZ][create_registration_permission_record] - Created %s' % new_user_permission)

        serializer = self.get_serializer(new_user_permission)
        return Response(serializer.data)



class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API View for User Model.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, IsAssociatedUser,)

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(email=user.email)

class PermissionRequestsViewSet(viewsets.ModelViewSet):
    """
    API View for PermissionRequest Models.
    """
    queryset = UserPermissionRequest.objects.all()
    serializer_class = PermissionRequestSerializer
    permission_classes = (permissions.IsAuthenticated, IsAssociatedUser)

    def get_queryset(self):

        # All the possible parameters we will accept
        record_id = self.request.query_params.get('id', None)
        item = self.request.query_params.get('item', None)
        requested_user = self.request.query_params.get('email', None)
        requesting_user = self.request.user

        return get_objects_with_permissions(UserPermissionRequest, requesting_user, requested_user, record_id, item)

    def perform_create(self, serializer):
        user_email = self.request.user
        user = User.objects.get(username=user_email)
        serializer.save(user=user)


# NOTE While the IsAssociatedUser permissions here works for PUTs, they are not used for GETs. 
# Any user can GET all permissions. Is this an issue?
class PermissionRequestsChangeViewSet(viewsets.ModelViewSet):
    """
    API View for PermissionRequest Models designed for PUT requests.
    """
    queryset = UserPermissionRequest.objects.all()
    serializer_class = PermissionRequestSerializer
    permission_classes = (permissions.IsAuthenticated, IsAssociatedUser)
