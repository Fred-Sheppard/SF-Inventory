#!/bin/bash
echo Flushing Database
python manage.py flush --noinput
echo 'Reverting migrations'
python manage.py migrate app zero
echo 'Deleting old migrations'
rm app/migrations/*.py
touch app/migrations/__init__.py
echo 'Running makemigrations'
python manage.py makemigrations
echo "Migrating models"
python manage.py migrate
echo Populating Catalogue
python manage.py shell < populate/catalogue.py
echo Creating Admin Account
python manage.py createsuperuser
echo Done
