#!/bin/bash
set -eo pipefail

echo "--> Running release script"
export PATH=/app/gettext/bin:$PATH
MANAGE_FILE=$(find . -maxdepth 3 -type f -name 'manage.py' | head -1)
MANAGE_FILE=${MANAGE_FILE:2}

echo "--> Migrating database schema"
python "$MANAGE_FILE" migrate --noinput

echo "--> Done release script"
echo ""
