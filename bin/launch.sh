#!/bin/bash
set -eo pipefail

echo "--> Running launch script"
export PATH=/app/gettext/bin:$PATH
MANAGE_FILE=$(find . -maxdepth 3 -type f -name 'manage.py' | head -1)
MANAGE_FILE=${MANAGE_FILE:2}

# Changes made to the filesystem in fly.io release commands are not
# persistent, hence staticfiles collection runs just before gunicorn
# starts
echo "--> Collecting static files"
python "$MANAGE_FILE" collectstatic --noinput

echo "--> Running web server"
gunicorn -b :8080 mixtures.wsgi
