from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

import logging
logger = logging.getLogger(__name__)

class UserPermissionRequest(models.Model):
    """
    This represents a user requesting permission to a specific project.
    """
    user = models.ForeignKey(User)
    item = models.CharField(max_length=100, blank=False, null=False, verbose_name="Item")
    date_requested = models.DateTimeField(auto_now_add=True)
    request_granted = models.BooleanField(default=False)
    date_request_granted = models.DateTimeField(default=None, null=True)

    def __str__(self):
        return '%s %s %s' % (self.user, self.item, self.request_granted)

# TODO Commented out until project manager information is stabilized
# def handle_user_permission_request_added(instance, **kwargs):
#     """
#     When a new UserPermissionRequest is added, send an email to that project's project manager
#     """

#     # Limit this action to run only on new UserPermissionRequests (not changes)
#     if kwargs['created']:

#         user_permission_request = instance
#         user = user_permission_request.user
#         project = user_permission_request.project
#         project_manager = project.project_manager

#         # Default email address if there is no project manager
#         if project_manager is None:
#             to_email = "nathaniel_bessa@hms.harvard.edu"
#         else:
#             to_email = project_manager.email

#         # Simple email message for now
#         subject = 'SciAuthz User Permission Request'
#         body = 'User ' + user.email + ' has requested access to ' + project.name + '. Please login to SciAuthZ to accept or deny this request.'
#         logger.debug(body)
        
#         # Send the email
#         msg = EmailMultiAlternatives(subject, body, settings.DEFAULT_FROM_EMAIL, [to_email])
#         msg.send()

#         logger.debug('Sent new user permission request notification to %s for project %s', to_email, project.name)

# post_save.connect(handle_user_permission_request_added, sender=UserPermissionRequest)

class UserPermission(models.Model):
    """
    This is the granting of permission to a user for a specific project.
    """
    user = models.ForeignKey(User)
    item = models.CharField(max_length=100, blank=False, null=False, verbose_name="Item")
    permission = models.CharField(max_length=100, blank=False, null=False, verbose_name="Permission")

    def __str__(self):
        return '%s %s %s' % (self.user, self.item, self.permission)
