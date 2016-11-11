from django.db import models

from django.contrib.auth.models import User


class UserPermission(models.Model):
    user = models.ForeignKey(User)
    project = models.CharField(max_length=100, blank=False, null=False, verbose_name="Project")
    permission = models.CharField(max_length=100, blank=False, null=False, verbose_name="Permission")
