from rest_framework import viewsets, permissions, generics
from authorization.serializers import UserPermissionSerializer
from authorization.serializers import UserSerializer
from authorization.serializers import PermissionRequestSerializer
from authorization.models import UserPermission
from authorization.models import UserPermissionRequest
from django.contrib.auth.models import User
from authorization.permissions import IsAssociatedUser
from pyauth0jwt.auth0authenticate import user_auth_and_jwt
from django.http import HttpResponse

@user_auth_and_jwt
def login(request):
    return HttpResponse("SENT")

class UserPermissionListAPIView(generics.ListAPIView):
    """
    API View for UserPermission Model.
    """
    base_name = "user_permission"
    permission_classes = (permissions.IsAuthenticated, IsAssociatedUser,)
    serializer_class = UserPermissionSerializer

    def get_queryset(self):
        user = self.request.user
        return UserPermission.objects.filter(user=user)

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

    def perform_create(self, serializer):
        user_email = self.request.user
        user = User.objects.get(username=user_email)
        serializer.save(user=user)

    def get_queryset(self):
        user = self.request.user
        return UserPermissionRequest.objects.filter(user=user)
