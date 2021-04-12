web: gunicorn --worker-class eventlet -w 1 run:app
init: python manage.py db init && python manage.py db migrate
upgrade: python manage.py db upgrade