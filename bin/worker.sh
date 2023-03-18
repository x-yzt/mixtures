#!/bin/bash
set -eo pipefail

echo "--> Running worker launch script"
export PATH=/app/gettext/bin:$PATH
MANAGE_FILE=$(find . -maxdepth 3 -type f -name 'manage.py' | head -1)
MANAGE_FILE=${MANAGE_FILE:2}

echo "--> Running task worker"
python "$MANAGE_FILE" run_huey
