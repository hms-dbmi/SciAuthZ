# SciAuthZ

This Django app is a dirt simple service to enable the most basic research project authorization.

It is assumed the user has acquired the DBMI_JWT prior to access this application, as it will be used to authenticate them and create their session for this app.

## Required Configurations

In order to verify the signature on the JWT we need the same secret as it was signed with in Auth0. You'll see the below setting which utilizes this secret.

### Auth0

~~~
JWT_AUTH = {
    'JWT_SECRET_KEY': base64.b64decode(os.environ.get("AUTH0_SECRET", ""), '-_'),
    'JWT_AUDIENCE': os.environ.get("AUTH0_CLIENT_ID"),
    'JWT_PAYLOAD_GET_USERNAME_HANDLER': 'authorization.permissions.jwt_get_username_from_payload'
}
~~~

### Running Tests
python manage.py test authorization.tests --settings SciAuthZ.test_settings