from rest_framework import viewsets, permissions, generics
from authorization.serializers import UserPermissionSerializer, \
    UserSerializer, \
    AuthorizableProjectSerializer, \
    PermissionRequestSerializer, \
    DataUseAgreementSignSerializer, \
    ProjectSetupSerializer, \
    DataUseAgreementSerializer
from authorization.models import UserPermission, \
    AuthorizableProject, \
    UserPermissionRequest, \
    DataUseAgreementSign, \
    DataUseAgreement
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


class AuthorizableProjectsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API View for AuthorizableProject Model.
    """
    queryset = AuthorizableProject.objects.all()
    serializer_class = AuthorizableProjectSerializer


class ProjectSetupViewSet(generics.ListAPIView):
    """
    API View for a single project. Could probably be worked into above view.
    """
    serializer_class = ProjectSetupSerializer

    def get_queryset(self):
        project_key = self.kwargs['project_key']
        return AuthorizableProject.objects.filter(project_key=project_key)


class PermissionRequestsViewSet(viewsets.ModelViewSet):
    """
    API View for PermissionRequest Models.
    """
    queryset = UserPermissionRequest.objects.all()
    serializer_class = PermissionRequestSerializer
    permission_classes = (permissions.IsAuthenticated, IsAssociatedUser,)

    def perform_create(self, serializer):
        user_email = self.request.user
        user = User.objects.get(username=user_email)
        project = AuthorizableProject.objects.get(project_key=self.request.data['project'])
        serializer.save(user=user, project=project)

    def get_queryset(self):
        user = self.request.user
        return UserPermissionRequest.objects.filter(user=user)


class DataUseAgreementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API View for DUA
    """
    queryset = DataUseAgreement.objects.all()
    serializer_class = DataUseAgreementSerializer


class DataUseAgreementSignViewSet(viewsets.ModelViewSet):
    """
    API View for a user signing a DUA.
    """
    queryset = DataUseAgreementSign.objects.all()
    serializer_class = DataUseAgreementSignSerializer
    permission_classes = (permissions.IsAuthenticated, IsAssociatedUser,)

    def perform_create(self, serializer):
        # The user indicated in the request is the one who signs it.
        user = self.request.user
        data_use_agreement = DataUseAgreement.objects.get(name=self.request.data['data_use_agreement'])
        serializer.save(user=user, data_use_agreement=data_use_agreement)

    def get_queryset(self):
        user = self.request.user
        return DataUseAgreementSign.objects.filter(user=user)
