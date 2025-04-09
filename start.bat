@echo off

echo Starting...
python manage.py makemigrations app
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
