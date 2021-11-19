#!/bin/bash

set -eo pipefail
shopt -s nullglob

# Formatting
if [ "$1" = "format" ]; then
    echo "formatting style..."
    black ./api
    exit
fi

# Linting
if [ "$1" =  "lint" ]; then
    echo "Verifying style..."
    black ./api --check --diff
    flake8 ./api
    exit
fi

# Database setup
if [ -z ${DB_URL+x} ]; then
  echo "DB_URL needs to be defined!"
  exit
fi

echo "Upgrading the database..."
cd /api
alembic upgrade head

cd -
if [ "$1" = "create_admin" ]; then
  echo "Creating an admin user..."
  python /api/create_admin.py
else
  echo "Starting the API..."
  exec "$@"
fi
