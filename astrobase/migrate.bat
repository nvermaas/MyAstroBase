#python manage.py makemigrations backend_app --settings=astrobase.settings.dev
#python manage.py makemigrations transients_app --settings=astrobase.settings.dev
#python manage.py makemigrations exoplanets --settings=astrobase.settings.dev
y
python manage.py migrate --settings=astrobase.settings.dev