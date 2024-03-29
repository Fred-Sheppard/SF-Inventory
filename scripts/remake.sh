#!/bin/bash
echo 'Reverting migrations'
python manage.py migrate app zero
echo 'Deleting old migrations'
rm app/migrations/*.py
touch app/migrations/__init__.py
echo 'Running makemigrations'
python manage.py makemigrations
echo "Migrating models"
python manage.py migrate
echo "Entering sample data"
python manage.py shell < scripts/sample_data.py
