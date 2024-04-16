echo Flushing Database
python manage.py flush
echo Migrating DB
python manage.py migrate
echo Populating Catalogue
python manage.py shell < populate/catalogue.py
echo Creating Admin Account
python manage.py createsuperuser
echo Done