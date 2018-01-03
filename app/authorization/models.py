from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

import logging
logger = logging.getLogger(__name__)

class AuthorizableProject(models.Model):
    """
    An Authorizable project is the representation of a project that has the definitions for the projects privacy.
    """
    name = models.CharField(max_length=100, blank=False, null=False, verbose_name="Project Name")
    project_key = models.CharField(max_length=100, blank=False, null=False, verbose_name="Project Key")
    permission_scheme = models.CharField(max_length=100, default="PRIVATE", verbose_name="Permission Scheme")
    dua_required = models.BooleanField(default=True)

    def __str__(self):
        return '%s %s' % (self.project_key, self.name)


class UserPermissionRequest(models.Model):
    """
    This represents a user requesting permission to a specific project.
    """
    user = models.ForeignKey(User)
    project = models.ForeignKey(AuthorizableProject)
    date_requested = models.DateTimeField(auto_now_add=True)
    request_granted = models.BooleanField(default=False)
    date_request_granted = models.DateTimeField(default=None, null=True)

    def __str__(self):
        return '%s %s %s' % (self.user, self.project, self.request_granted)

# Commented out until project manager information is stabilized
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
    project = models.ForeignKey(AuthorizableProject)
    permission = models.CharField(max_length=100, blank=False, null=False, verbose_name="Permission")

    def __str__(self):
        return '%s %s %s' % (self.user, self.project, self.permission)


class DataUseAgreement(models.Model):
    """
    This is the text for the data use agreement associated with a project. The agreement_form field should be the name of the html file (with extension)
    that contains the form. This file should be in the templates/duaforms/ directory. If no form is being used, leave the field blank and instead 
    enter some text in the the agreement_text field.
    """
    name = models.CharField(max_length=100, blank=False, null=False, verbose_name="name")
    project = models.ForeignKey(AuthorizableProject, related_name='duas')
    agreement_text = models.TextField(blank=True)
    agreement_form_file = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return '%s %s' % (self.id, self.name)
    
    def clean(self):
        if self.agreement_text != "" and self.agreement_form_file != "":
            raise ValidationError('Cannot have both an agreement_text and agreement_form_file. Please choose one.')
        if self.agreement_text == "" and self.agreement_form_file == "":
            raise ValidationError('Either the agreement_text or agreement_form_file must have a value.')


class DataUseAgreementSign(models.Model):
    """
    This represents a user signing a DUA for a specific project.
    """
    data_use_agreement = models.ForeignKey(DataUseAgreement)
    user = models.ForeignKey(User)
    date_signed = models.DateTimeField(auto_now_add=True)
    agreement_text = models.TextField(blank=False)
