#!/bin/sh
if [ ! -d "$MIGRATIONS_DIR" ]
then
    if [ -z "$(ls -A $MIGRATIONS_DIR)" ]; then
        echo "Initing db in $MIGRATIONS_DIR"
        flask db init
    fi
else
    echo "Not initing db in $MIGRATIONS_DIR"
fi

flask db migrate
flask db upgrade
flask check_initial_data
gunicorn --workers=5 --log-file=- --bind=0.0.0.0:5000 run:app