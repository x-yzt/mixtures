#!/bin/ash

set -emo pipefail

echo "--> Running release script"

echo "--> Migrating database schema"
python manage.py migrate --noinput
