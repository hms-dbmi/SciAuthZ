from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

import logging
logger = logging.getLogger(__name__)

class UserPermission(models.Model):
    """
    This is the granting of permission to a user for a specific project.
    """
    user_email = models.CharField(max_length=250, blank=False, null=False, verbose_name="User Email")
    item = models.CharField(max_length=100, blank=False, null=False, verbose_name="Item")
    permission = models.CharField(max_length=100, blank=False, null=False, verbose_name="Permission")
    date_updated = models.DateTimeField(blank=False, null=False, auto_now_add=True)

    def __str__(self):
        return '%s %s %s' % (self.user_email, self.item, self.permission)
