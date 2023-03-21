#!/bin/sh
# wait-for-mysql.sh

HOST="$1"
PORT="$2"

until nc -z -v -w30 $HOST $PORT
do
  echo "Waiting for database connection..."
  # wait for 1 seconds before check again
  sleep 1
done