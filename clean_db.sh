#!/bin/bash

rm db.sqlite3

rm -rf crm/migrations/

./manage.py migrate

./manage.py makemigrations crm


./manage.py migrate
./manage.py createinitialrevisions

./manage.py migrate
