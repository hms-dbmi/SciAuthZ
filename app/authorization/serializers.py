from authorization.models import UserPermission, UserPermissionRequest
from rest_framework import serializers
from django.contrib.auth.models import User
from django.db import models
import os

class UserPermissionSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username', read_only=False, queryset=User.objects.all())

    class Meta:
        model = UserPermission
        fields = ('id', 'user', 'item', 'permission')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'password', 'is_superuser')

class PermissionRequestSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username', read_only=False, queryset=User.objects.all())
    
    class Meta:
        model = UserPermissionRequest
        fields = ('id', 'user', 'item', 'date_requested', 'request_granted', 'date_request_granted')
