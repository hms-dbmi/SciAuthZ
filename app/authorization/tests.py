from datetime import datetime
from furl import furl
from pprint import pprint
from unittest.mock import patch

import json

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIClient

from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse

from authorization.models import UserPermission

FAKE_ITEM_1 = "Sci.Test"
FAKE_ITEM_2 = "SciAuthZ.Test"
FAKE_ITEM_3 = "SciReg.Test"

USER_EMAIL = "user@example.com"
OTHER_USER_EMAIL = "user2@example.com"

MANAGER_EMAIL = "manager@example.com"
MANAGER_PASSWORD = "password"

class UserPermissionTest(APITestCase):
    """
    This class captures various tests related to CRUD actions on the UserPermission model. Authentication
    in SciAuthZ depends on the presence of a valid JWT in the request header, and from the username field
    in the JWT the user is determined. However, because getting a valid JWT for unit tests is complicated
    and might require exposing an Auth0 client secret here or changing our Auth0 configuration drastically,
    we can mock the username -- pretending it came from a JWT -- and force authentication without a JWT by
    logging in as a test user.
    """

    managers_permission_1 = None

    def setUp(self):
        """
        The necessary steps before tests can run.
        """

        # Create a user to force an accepted authentication on all requests. This will not necessarily
        # always be the user we want to assume is sending the requests, so the individual tests below
        # will mock the requesting user as necessary.
        manager_user = User.objects.create_user(MANAGER_EMAIL, email=MANAGER_EMAIL, password=MANAGER_PASSWORD)
        self.client.force_authenticate(user=manager_user)

        # MANAGE permissions are always created manually, so create one now.
        manage_permission = UserPermission.objects.get_or_create(
            user_email=MANAGER_EMAIL,
            item=FAKE_ITEM_1,
            permission="MANAGE"
        )

    @patch('authorization.views.get_email_from_jwt')
    def test_get_permissions_by_id(self, get_email_from_jwt):
        """
        Test GET calls to pull the permission for the given ID. This should always return
        just one record or none at all.
        """

        # Create a permission for a user for an item that the manager manages.
        perm = UserPermission.objects.create(
            user_email=USER_EMAIL,
            item=FAKE_ITEM_1,
            permission="VIEW"
        )

        f = furl("/user_permission/")
        f.args["id"] = perm.id

        # Test that the user with MANAGE permissions can access this item.
        get_email_from_jwt.return_value = MANAGER_EMAIL
        response = self.client.get(f.url)
        self.assertEqual(response.data['count'], 1)

        # Test that the user that this permission belongs to can access their own item.
        get_email_from_jwt.return_value = USER_EMAIL
        response = self.client.get(f.url)
        self.assertEqual(response.data['count'], 1)

        # Test that a user who is neither a manager nor the owner of the record does not get back this item.
        get_email_from_jwt.return_value = OTHER_USER_EMAIL
        response = self.client.get(f.url)
        self.assertEqual(response.data['count'], 0)

    @patch('authorization.views.get_email_from_jwt')
    def test_get_permissions_by_item(self, get_email_from_jwt):
        """
        Test GET calls to pull permissions for the given item.
        """

        # Create two sets of permission for the same item that the manager manages.
        perm1 = UserPermission.objects.create(
            user_email=USER_EMAIL,
            item=FAKE_ITEM_1,
            permission="VIEW"
        )
        perm2 = UserPermission.objects.create(
            user_email=OTHER_USER_EMAIL,
            item=FAKE_ITEM_2,
            permission="VIEW"
        )

        f = furl("/user_permission/")
        f.args["item"] = FAKE_ITEM_1

        # A user with MANAGE permissions should get back two results (his permission and the new one).
        get_email_from_jwt.return_value = MANAGER_EMAIL
        response = self.client.get(f.url)
        self.assertEqual(response.data['count'], 2)

        # Test that the user only sees their own permission.
        get_email_from_jwt.return_value = USER_EMAIL
        response = self.client.get(f.url)
        self.assertEqual(response.data['count'], 1)

        # Test that a request from a different user without this permission does not get anything back.
        get_email_from_jwt.return_value = OTHER_USER_EMAIL
        response = self.client.get(f.url)
        self.assertEqual(response.data['count'], 0)

    @patch('authorization.views.get_email_from_jwt')
    def test_get_permissions_by_user(self, get_email_from_jwt):
        """
        Test GET calls to pull the permission for the given user.
        """

        # Create a few permissions for a user.
        perm1 = UserPermission.objects.create(
            user_email=USER_EMAIL,
            item=FAKE_ITEM_1,
            permission="VIEW"
        )
        perm2 = UserPermission.objects.create(
            user_email=USER_EMAIL,
            item=FAKE_ITEM_2,
            permission="VIEW"
        )
        perm3 = UserPermission.objects.create(
            user_email=USER_EMAIL,
            item=FAKE_ITEM_2,
            permission="VIEW"
        )

        f = furl("/user_permission/")
        f.args["email"] = USER_EMAIL

        # The MANAGE user has access to just one of these permissions
        get_email_from_jwt.return_value = MANAGER_EMAIL
        response = self.client.get(f.url)
        self.assertEqual(response.data['count'], 1)

        # The user itself has access to all of their permissions
        get_email_from_jwt.return_value = USER_EMAIL
        response = self.client.get(f.url)
        self.assertEqual(response.data['count'], 3)

        # A random user cannot see any of these permissions
        get_email_from_jwt.return_value = OTHER_USER_EMAIL
        response = self.client.get(f.url)
        self.assertEqual(response.data['count'], 0)

    @patch('authorization.views.get_email_from_jwt')
    def test_create_view_permission_success(self, get_email_from_jwt):
        """
        Test the creation of a VIEW permission. This requires that the request come
        from someone with MANAGE permissions on the given item.
        """

        # Mock the user sending the request
        get_email_from_jwt.return_value = MANAGER_EMAIL

        f = furl("/user_permission/create_item_view_permission_record/")

        # Data for the POST payload
        data = {
            "grantee_email": USER_EMAIL,
            "item": FAKE_ITEM_1
        }

        response = self.client.post(f.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('authorization.views.get_email_from_jwt')
    def test_create_view_permission_denied(self, get_email_from_jwt):
        """
        Test an attempt to create a VIEW permission from someone who does not have
        MANAGE permissions on the given item.
        """

        # Mock the user sending the request
        get_email_from_jwt.return_value = USER_EMAIL

        f = furl("/user_permission/create_item_view_permission_record/")

        # Data for the POST payload
        data = {
            "grantee_email": USER_EMAIL,
            "item": FAKE_ITEM_1
        }

        response = self.client.post(f.url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('authorization.views.get_email_from_jwt')
    def test_remove_view_permission_success(self, get_email_from_jwt):
        """
        Tests the removal of a VIEW permission. This requires that the request come
        from someone with MANAGE permissions on the given item.
        """

        # Mock the user sending the request
        get_email_from_jwt.return_value = MANAGER_EMAIL

        # Create the permission first
        view_permission = UserPermission.objects.get_or_create(
            user_email=USER_EMAIL,
            item=FAKE_ITEM_1,
            permission="VIEW"
        )

        f = furl("/user_permission/remove_item_view_permission_record/")

        # Data for the POST payload
        data = {
            "grantee_email": USER_EMAIL,
            "item": FAKE_ITEM_1
        }

        response = self.client.post(f.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('authorization.views.get_email_from_jwt')
    def test_remove_view_permission_denied(self, get_email_from_jwt):
        """
        Tests the removal of a VIEW permission from someone who does not have
        MANAGE permissions on the given item.
        """

        # Mock the user sending the request
        get_email_from_jwt.return_value = USER_EMAIL

        # Create the permission first
        view_permission = UserPermission.objects.get_or_create(
            user_email=USER_EMAIL,
            item=FAKE_ITEM_1,
            permission="VIEW"
        )

        f = furl("/user_permission/remove_item_view_permission_record/")

        # Data for the POST payload
        data = {
            "grantee_email": USER_EMAIL,
            "item": FAKE_ITEM_1
        }

        response = self.client.post(f.url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('authorization.views.get_email_from_jwt')
    def test_create_registration_permission_record(self, get_email_from_jwt):
        """
        Tests the creation of a SciReg VIEW permission. The person making the request
        is giving the grantee permission to view their SciReg profile.
        """

        # Mock the user sending the request
        get_email_from_jwt.return_value = USER_EMAIL

        f = furl("/user_permission/create_registration_permission_record/")

        # Data for the POST payload
        data = {
            "grantee_email": MANAGER_EMAIL,
            "item": FAKE_ITEM_1
        }

        response = self.client.post(f.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
