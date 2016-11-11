from rest_framework import viewsets, permissions, generics
from authorization.serializers import UserPermissionSerializer, UserSerializer
from authorization.models import UserPermission
from django.contrib.auth.models import User
from authorization.permissions import IsAssociatedUser


class UserPermissionListAPIView(generics.ListAPIView):
    base_name = "user_permission"
    permission_classes = (permissions.IsAuthenticated,
                          IsAssociatedUser,)
    serializer_class = UserPermissionSerializer

    def get_queryset(self):
        user = self.request.user
        return UserPermission.objects.filter(user=user)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer