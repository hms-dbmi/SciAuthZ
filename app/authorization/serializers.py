from authorization.models import UserPermission
from rest_framework import serializers
from django.contrib.auth.models import User


class UserPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPermission
        fields = ('id', 'user_email', 'item', 'permission', 'date_updated')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'password', 'is_superuser')
