#!/usr/bin/env bash

python manage.py migrate
if [ $? -ne 0 ]; then
    echo "Error: Database migration failed."
    exit 1
fi
python manage.py test
if [ $? -ne 0 ]; then
    echo "Error: Test failed."
    exit 1
fi
python manage.py runserver 0.0.0.0:8000
