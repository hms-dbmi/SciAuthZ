from authorization.models import UserPermission, AuthorizableProject, UserPermissionRequest, DataUseAgreementSign, DataUseAgreement
from rest_framework import serializers
from django.contrib.auth.models import User
from django.db import models
import os


class UserPermissionSerializer(serializers.ModelSerializer):
    project = serializers.SlugRelatedField(slug_field='project_key', read_only=True)
    user = serializers.SlugRelatedField(slug_field='username', read_only=False, queryset=User.objects.all())

    class Meta:
        model = UserPermission
        fields = ('id', 'user', 'project', 'permission')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'password', 'is_superuser')


class AuthorizableProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthorizableProject
        fields = ('id', 'name', 'project_key', 'permission_scheme', 'dua_required')


class DataUseAgreementSerializer(serializers.ModelSerializer):
    project = serializers.SlugRelatedField(slug_field='project_key', read_only=True)
    agreement_form = serializers.SerializerMethodField()

    class Meta:
        model = DataUseAgreement
        fields = ('name', 'agreement_text', 'project', 'agreement_form')

    # If there is an agreement form file, grab the html contents
    def get_agreement_form(self, dua):
        if dua.agreement_form_file != "":
            form_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/templates/duaforms/' + dua.agreement_form_file
            return open(form_path, 'r').read()
        else:
            return dua.agreement_text


class PermissionRequestSerializer(serializers.ModelSerializer):
    project = serializers.SlugRelatedField(slug_field='project_key', read_only=True)
    user = serializers.SlugRelatedField(slug_field='username', read_only=False, queryset=User.objects.all())

    class Meta:
        model = UserPermissionRequest
        fields = ('id', 'user', 'project', 'date_requested', 'request_granted', 'date_request_granted')


class DataUseAgreementSignSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username', read_only=False, queryset=User.objects.all())
    data_use_agreement = DataUseAgreementSerializer(read_only=True)

    class Meta:
        model = DataUseAgreementSign
        fields = ('data_use_agreement', 'user', 'date_signed', 'agreement_text')


class ProjectSetupSerializer(serializers.ModelSerializer):
    dua = DataUseAgreementSerializer(source='duas', many=True)

    class Meta:
        model = AuthorizableProject
        fields = ('project_key', 'permission_scheme', 'dua_required', 'dua')
