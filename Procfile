release: python sidequest/manage.py makemigrations --no-input
release: python sidequest/manage.py migrate --no-input

web: gunicorn sidequest.wsgi
web: python sidequest/manage.py runserver 0.0.0.0:$PORT