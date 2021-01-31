#!/bin/bash
MIGRATIONS_DIR_PATH=$1
python manage.py db init --directory=$MIGRATIONS_DIR_PATH
python manage.py db migrate --directory=$MIGRATIONS_DIR_PATH
python manage.py db upgrade --directory=$MIGRATIONS_DIR_PATH
