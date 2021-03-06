#!/bin/sh
if [ ! -d "$MIGRATIONS_DIR" ]
then
    if [ -z "$(ls -A $MIGRATIONS_DIR)" ]; then
        echo "Initing db in $MIGRATIONS_DIR"
        flask db init
    fi
else
    if [ -z "$(ls -A $MIGRATIONS_DIR)" ]; then
        echo "Initing db in $MIGRATIONS_DIR"
        flask db init
    else
        echo "Not initing db in $MIGRATIONS_DIR"
    fi
fi

flask db migrate
flask db upgrade
flask check_initial_data
gunicorn --log-file=- --bind=${1:-0.0.0.0}:${2:-5000} run:app