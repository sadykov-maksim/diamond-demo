#!/bin/sh

if [ $DATABASE = "django.db.backends.postgresql" ]

then
    echo "Ожидание службы PostgreSQL..."

    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 0.1
    done

    echo "Сервис PostgreSQL запущен"
fi

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput --clear

if [ "$DJANGO_SUPERUSER_USERNAME" ]
then
    python manage.py createsuperuser \
        --noinput \
        --username "$DJANGO_SUPERUSER_USERNAME" \
        --email "$DJANGO_SUPERUSER_EMAIL"
fi

#gunicorn diamond.wsgi:application --bind 0.0.0.0:8000
gunicorn --certfile=/etc/letsencrypt/live/red-caviar-wholesale.host/fullchain.pem --keyfile=/etc/letsencrypt/live/red-caviar-wholesale.host/privkey.pem --bind 0.0.0.0:443 diamond.wsgi:application
exec "$@"