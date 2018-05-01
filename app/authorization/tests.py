from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from authorization.models import UserPermission

from rest_framework.test import APIClient
from django.conf import settings
from pprint import pprint
from furl import furl

from datetime import datetime


TEST_USERS = {"user1":
                  {
                      "username": "test@test.com"
                  }}


class CreateUserTest(APITestCase):

    def setUp(self):
        self.superuser = User.objects.create_superuser(TEST_USERS["user1"]["username"], TEST_USERS["user1"]["username"], '')
        self.client.login(username=TEST_USERS["user1"]["username"], password='', email=TEST_USERS["user1"]["username"])

        new_permission = UserPermission.objects.get_or_create(user=self.superuser,
                                                              item="BERSON",
                                                              permission="VIEW",
                                                              date_updated=datetime.now())

        new_permission = UserPermission.objects.get_or_create(user=self.superuser,
                                                              item="N2C2",
                                                              permission="VIEW",
                                                              date_updated=datetime.now())

    def test_retrieve_all_permissions(self):

        url = "/user_permission/"
        test_user = TEST_USERS["user1"]["username"]

        f = furl(url)
        f.args["email"] = test_user

        client = APIClient()
        client.login(username=test_user, password='', email=test_user)

        response = client.get(f.url)

        # Did we get results back?
        self.assertEqual(response.json()["count"] > 0, True)

    def test_single_permission(self):
        url = "/user_permission/"
        test_user = TEST_USERS["user1"]["username"]

        f = furl(url)

        f.args["email"] = test_user
        f.args["item"] = "BERSON"

        client = APIClient()
        client.login(username=test_user, password='', email=test_user)

        response = client.get(f.url)

        # Did we get the Berson result back?
        self.assertEqual(response.json()["results"][0]["item"], "BERSON")

    def test_has_permission(self):
        # "SciReg.n2c2.profile." + request.user.email
        # VIEW
        url = "/authorization_requests/get_queryset/"
        url = "/user_permission/"
        client = APIClient()
        client.login(username=TEST_USERS["user1"]["username"],password='', email=TEST_USERS["user1"]["username"])
        response = client.get(url + "?email=%s" % TEST_USERS["user1"]["username"])

        # pprint(vars(response))
        pprint(response.json()["results"])

        self.assertEqual(1, 1)

    def test_create_authorization_request(self):

        url = "/authorization_requests/"

        client = APIClient()
        client.login(username=TEST_USERS["user1"]["username"], password='', email=TEST_USERS["user1"]["username"])
        response = client.post(url, {"user": TEST_USERS["user1"]["username"], "item": "BERSON"})

        self.assertEqual(response.status_code, 201)
