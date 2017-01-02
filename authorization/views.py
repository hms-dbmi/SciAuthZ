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


class UserPermissionListAPIView(generics.ListAPIView):
    base_name = "user_permission"
    permission_classes = (permissions.IsAuthenticated,IsAssociatedUser,)
    serializer_class = UserPermissionSerializer

    def get_queryset(self):
        user = self.request.user
        return UserPermission.objects.filter(user=user)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class AuthorizableProjectsViewSet(viewsets.ModelViewSet):
    queryset = AuthorizableProject.objects.all()
    serializer_class = AuthorizableProjectSerializer


class ProjectSetupViewSet(generics.ListAPIView):
    serializer_class = ProjectSetupSerializer

    def get_queryset(self):
        project_key = self.kwargs['project_key']
        return AuthorizableProject.objects.filter(project_key=project_key)


class PermissionRequestsViewSet(viewsets.ModelViewSet):
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


class DataUseAgreementViewSet(viewsets.ModelViewSet):
    queryset = DataUseAgreement.objects.all()
    serializer_class = DataUseAgreementSerializer


class DataUseAgreementSignViewSet(viewsets.ModelViewSet):
    queryset = DataUseAgreementSign.objects.all()
    serializer_class = DataUseAgreementSignSerializer
    permission_classes = (permissions.IsAuthenticated, IsAssociatedUser,)

    def perform_create(self, serializer):
        user = self.request.user
        data_use_agreement = DataUseAgreement.objects.get(name=self.request.data['data_use_agreement'])
        serializer.save(user=user, data_use_agreement=data_use_agreement)

    def get_queryset(self):
        user = self.request.user
        return DataUseAgreementSign.objects.filter(user=user)
