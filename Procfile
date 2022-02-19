release: python manage.py rename_app statistics statisticscore && python manage.py migrate --noinput
web: gunicorn eypstats.wsgi --log-file -
