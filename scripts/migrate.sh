#!/bin/bash

echo "Reverting Migrations"
python manage.py migrate app zero
echo "Migrating models"
python manage.py migrate
echo "Entering sample data"
python manage.py shell < scripts/sample_data.py
