set -eo pipefail

# The post_compile hook is run by heroku-buildpack-python
indent() {
   RE="s/^/       /"
   [ $(uname) == "Darwin" ] && sed -l "$RE" || sed -u "$RE"
}

echo "-----> Running post-compile hook"

export PATH=/app/gettext/bin:$PATH
MANAGE_FILE=$(find . -maxdepth 3 -type f -name 'manage.py' | head -1)
MANAGE_FILE=${MANAGE_FILE:2}

echo "-----> Compiling translation files"

# Workaround to compile only dictionaries of this project, skipping deps.
python "$MANAGE_FILE" compilemessages 2>&1 | indent

echo "-----> Migrating database schema"

python "$MANAGE_FILE" migrate --noinput

echo "-----> Done post-compile hook"
echo ""
