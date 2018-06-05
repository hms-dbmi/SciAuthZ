#!/bin/bash

DJANGO_SECRET=$(aws ssm get-parameters --names $PS_PATH.django_secret --with-decryption --region us-east-1 | jq -r '.Parameters[].Value')
AUTH0_DOMAIN_VAULT=$(aws ssm get-parameters --names $PS_PATH.auth0_domain --with-decryption --region us-east-1 | jq -r '.Parameters[].Value')
AUTH0_CLIENT_ID_LIST=$(aws ssm get-parameters --names $PS_PATH.auth0_client_id_list --with-decryption --region us-east-1 | jq -r '.Parameters[].Value')
AUTH0_SECRET_VAULT=$(aws ssm get-parameters --names $PS_PATH.auth0_secret --with-decryption --region us-east-1 | jq -r '.Parameters[].Value')
AUTHENTICATION_LOGIN_URL=$(aws ssm get-parameters --names $PS_PATH.authentication_login_url --with-decryption --region us-east-1 | jq -r '.Parameters[].Value')

MYSQL_USERNAME_VAULT=$(aws ssm get-parameters --names $PS_PATH.mysql_username --with-decryption --region us-east-1 | jq -r '.Parameters[].Value')
MYSQL_PASSWORD_VAULT=$(aws ssm get-parameters --names $PS_PATH.mysql_pw --with-decryption --region us-east-1 | jq -r '.Parameters[].Value')
MYSQL_HOST_VAULT=$(aws ssm get-parameters --names $PS_PATH.mysql_host --with-decryption --region us-east-1 | jq -r '.Parameters[].Value')
MYSQL_PORT_VAULT=$(aws ssm get-parameters --names $PS_PATH.mysql_port --with-decryption --region us-east-1 | jq -r '.Parameters[].Value')

EMAIL_HOST=$(aws ssm get-parameters --names $PS_PATH.email_host --with-decryption --region us-east-1 | jq -r '.Parameters[].Value')
EMAIL_HOST_USER=$(aws ssm get-parameters --names $PS_PATH.email_host_user --with-decryption --region us-east-1 | jq -r '.Parameters[].Value')
EMAIL_HOST_PASSWORD=$(aws ssm get-parameters --names $PS_PATH.email_host_password --with-decryption --region us-east-1 | jq -r '.Parameters[].Value')
EMAIL_PORT=$(aws ssm get-parameters --names $PS_PATH.email_port --with-decryption --region us-east-1 | jq -r '.Parameters[].Value')

FIRST_ADMIN_EMAIL=$(aws ssm get-parameters --names $PS_PATH.first_admin_email --with-decryption --region us-east-1 | jq -r '.Parameters[].Value')

ALLOWED_HOSTS=$(aws ssm get-parameters --names $PS_PATH.allowed_hosts --with-decryption --region us-east-1 | jq -r '.Parameters[].Value')
RAVEN_URL=$(aws ssm get-parameters --names $PS_PATH.raven_url --with-decryption --region us-east-1 | jq -r '.Parameters[].Value')

export SECRET_KEY=$DJANGO_SECRET
export AUTH0_DOMAIN=$AUTH0_DOMAIN_VAULT
export AUTH0_CLIENT_ID_LIST=$AUTH0_CLIENT_ID_LIST
export AUTH0_SECRET=$AUTH0_SECRET_VAULT
export AUTHENTICATION_LOGIN_URL

export MYSQL_USERNAME=$MYSQL_USERNAME_VAULT
export MYSQL_PASSWORD=$MYSQL_PASSWORD_VAULT
export MYSQL_HOST=$MYSQL_HOST_VAULT
export MYSQL_PORT=$MYSQL_PORT_VAULT

export EMAIL_HOST
export EMAIL_HOST_USER
export EMAIL_HOST_PASSWORD
export EMAIL_PORT

export ALLOWED_HOSTS
export RAVEN_URL

SSL_KEY=$(aws ssm get-parameters --names $PS_PATH.ssl_key --with-decryption --region us-east-1 | jq -r '.Parameters[].Value')
SSL_CERT_CHAIN1=$(aws ssm get-parameters --names $PS_PATH.ssl_cert_chain1 --with-decryption --region us-east-1 | jq -r '.Parameters[].Value')
SSL_CERT_CHAIN2=$(aws ssm get-parameters --names $PS_PATH.ssl_cert_chain2 --with-decryption --region us-east-1 | jq -r '.Parameters[].Value')
SSL_CERT_CHAIN3=$(aws ssm get-parameters --names $PS_PATH.ssl_cert_chain3 --with-decryption --region us-east-1 | jq -r '.Parameters[].Value')

SSL_CERT_CHAIN="$SSL_CERT_CHAIN1$SSL_CERT_CHAIN2$SSL_CERT_CHAIN3"

echo $SSL_KEY | base64 -d >> /etc/nginx/ssl/server.key
echo $SSL_CERT_CHAIN | base64 -d >> /etc/nginx/ssl/server.crt

cd /app/

if [ ! -d static ]; then
    mkdir static
fi

python manage.py migrate
python manage.py collectstatic --no-input
python manage.py loaddata authorization
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('$FIRST_ADMIN_EMAIL', '$FIRST_ADMIN_EMAIL', '')" || echo "Super User already exists."

/etc/init.d/nginx restart

gunicorn SciAuthZ.wsgi:application -b 0.0.0.0:8004