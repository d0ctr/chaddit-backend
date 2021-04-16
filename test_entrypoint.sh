#!/bin/sh
flask db init
flask db migrate
flask db upgrade
flask check_initial_data
coverage run -m unittest discover
coverage report
coverage html
flask clear_data
rm -rf migrations