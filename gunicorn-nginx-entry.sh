#!/bin/bash

/vault/vault auth $ONETIME_TOKEN

DJANGO_SECRET=$(/vault/vault read -field=value $VAULT_PATH/django_secret)
AUTH0_DOMAIN_VAULT=$(/vault/vault read -field=value $VAULT_PATH/auth0_domain)
AUTH0_CLIENT_ID_VAULT=$(/vault/vault read -field=value $VAULT_PATH/auth0_client_id)
AUTH0_SECRET_VAULT=$(/vault/vault read -field=value $VAULT_PATH/auth0_secret)

MYSQL_USERNAME_VAULT=$(/vault/vault read -field=value $VAULT_PATH/mysql_username)
MYSQL_PASSWORD_VAULT=$(/vault/vault read -field=value $VAULT_PATH/mysql_pw)
MYSQL_HOST_VAULT=$(/vault/vault read -field=value $DB_VAULT_PATH/mysql_host)
MYSQL_PORT_VAULT=$(/vault/vault read -field=value $VAULT_PATH/mysql_port)

export SECRET_KEY=$DJANGO_SECRET
export AUTH0_DOMAIN=$AUTH0_DOMAIN_VAULT
export AUTH0_CLIENT_ID=$AUTH0_CLIENT_ID_VAULT
export AUTH0_SECRET=$AUTH0_SECRET_VAULT

export MYSQL_USERNAME=$MYSQL_USERNAME_VAULT
export MYSQL_PASSWORD=$MYSQL_PASSWORD_VAULT
export MYSQL_HOST=$MYSQL_HOST_VAULT
export MYSQL_PORT=$MYSQL_PORT_VAULT

SSL_KEY=$(/vault/vault read -field=value $VAULT_PATH/ssl_key)
SSL_CERT_CHAIN=$(/vault/vault read -field=value $VAULT_PATH/ssl_cert_chain)

echo $SSL_KEY | base64 -d >> /etc/nginx/ssl/server.key
echo $SSL_CERT_CHAIN | base64 -d >> /etc/nginx/ssl/server.crt

cd /app/

python manage.py migrate
python manage.py collectstatic --no-input
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('$FIRST_ADMIN_EMAIL', '$FIRST_ADMIN_EMAIL', '')" || echo "Super User already exists."

/etc/init.d/nginx restart

gunicorn SciAuthZ.wsgi:application -b 0.0.0.0:8004