#!/bin/ash

set -emo pipefail

echo "--> Running launch script"

echo "--> Running task worker in background"
python manage.py run_huey &

echo "--> Running web server"
gunicorn -b :8080 --workers 1 mixtures.wsgi
