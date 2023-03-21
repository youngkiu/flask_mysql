#!/bin/bash
MIGRATIONS_DIR_PATH=$1
flask db init --directory=$MIGRATIONS_DIR_PATH
flask db migrate --directory=$MIGRATIONS_DIR_PATH
flask db upgrade --directory=$MIGRATIONS_DIR_PATH
