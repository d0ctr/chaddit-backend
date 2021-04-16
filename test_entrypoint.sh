#!/bin/sh
flask db init > /dev/null
flask db migrate > /dev/null
flask db upgrade > /dev/null
flask check_initial_data > /dev/null
coverage run -m unittest discover
coverage report
coverage html
flask clear_data