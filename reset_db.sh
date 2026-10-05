#!/usr/bin/env bash
#
# Clean application restart for local development.
#
#   1. Drops every table in the database configured in config/settings.py (.env)
#   2. Deletes all migration files in the project's apps
#   3. Regenerates migrations and applies them
#   4. Creates a superuser from DJANGO_SUPERUSER_EMAIL / DJANGO_SUPERUSER_PASSWORD
#      in .env
#
# THIS DESTROYS ALL DATA. Never run it against a database you care about.
#
# Usage: ./reset_db.sh [--yes]
#   --yes   skip the confirmation prompt

set -euo pipefail

cd "$(dirname "$0")"

if [[ -x .venv/bin/python ]]; then
    PYTHON=.venv/bin/python
else
    PYTHON=python
fi

ASSUME_YES=false
if [[ "${1:-}" == "--yes" ]]; then
    ASSUME_YES=true
fi

# Read the database Django is actually configured to use, so this script can't
# drift from settings.py / .env.
DB_TARGET=$("$PYTHON" manage.py shell -c '
from django.conf import settings
db = settings.DATABASES["default"]
print("{NAME} on {HOST}:{PORT} as {USER}".format(**db))
')

# Check the superuser credentials before destroying anything. settings.py loads
# .env into the environment, so they are visible here and to createsuperuser.
"$PYTHON" manage.py shell -c '
import os, sys
missing = [v for v in ("DJANGO_SUPERUSER_EMAIL", "DJANGO_SUPERUSER_PASSWORD") if not os.environ.get(v)]
if missing:
    sys.exit("Missing in .env: " + ", ".join(missing))
'

echo "This will DELETE ALL TABLES AND DATA in: $DB_TARGET"
echo "and delete every migration file in this project."

if [[ "$ASSUME_YES" != true ]]; then
    read -r -p "Type 'reset' to continue: " answer
    if [[ "$answer" != "reset" ]]; then
        echo "Aborted."
        exit 1
    fi
fi

echo "==> Dropping all tables"
"$PYTHON" manage.py shell -c '
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = current_schema()")
    tables = [row[0] for row in cursor.fetchall()]
    if tables:
        quoted = ", ".join(connection.ops.quote_name(t) for t in tables)
        cursor.execute(f"DROP TABLE IF EXISTS {quoted} CASCADE")
print(f"Dropped {len(tables)} table(s)")
'

echo "==> Deleting migration files"
# Uses -exec rm rather than -delete: -delete implies -depth, which disables -prune.
find . \( -path ./.venv -o -path ./venv -o -path ./env -o -path ./.git \) -prune -o \
    -path '*/migrations/*' \( -name '*.py' -o -name '*.pyc' \) ! -name '__init__.py' \
    -print -exec rm -f {} +
find . \( -path ./.venv -o -path ./venv -o -path ./env -o -path ./.git \) -prune -o \
    -path '*/migrations/__pycache__' -type d -print -exec rm -rf {} +

echo "==> Generating migrations"
"$PYTHON" manage.py makemigrations

echo "==> Applying migrations"
"$PYTHON" manage.py migrate

echo "==> Creating superuser"
# With --noinput, createsuperuser reads DJANGO_SUPERUSER_EMAIL and
# DJANGO_SUPERUSER_PASSWORD from the environment.
"$PYTHON" manage.py createsuperuser --noinput

echo "Done."
