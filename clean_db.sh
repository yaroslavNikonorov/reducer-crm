#!/bin/bash

rm db.sqlite3

rm -rf crm/migrations/

find ./ -name "__pycache__" -exec rm -r '{}' +;

./manage.py migrate

./manage.py makemigrations crm


./manage.py migrate
./manage.py createinitialrevisions

./manage.py migrate
