#!/bin/sh
flask db init
flask db migrate
flask db upgrade
flask clear_data
flask check_initial_data
coverage run -m unittest discover
# coverage report
# coverage html
