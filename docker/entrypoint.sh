#!/usr/bin/env sh
set -e

# Wait for DB if using Postgres
if [ -n "$DATABASE_URL" ]; then
  echo "Waiting for database..."
  python - <<'PY'
import sys, time
import os
import django
from django.db import connections
from django.db.utils import OperationalError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

db_conn = connections['default']
for i in range(60):
    try:
        db_conn.cursor()
        print('Database ready')
        sys.exit(0)
    except OperationalError:
        print('Database unavailable, waiting...')
        time.sleep(1)
print('Database not available after waiting', file=sys.stderr)
sys.exit(1)
PY
fi

# Run migrations and collect static
python manage.py migrate --noinput
python manage.py collectstatic --no-input

exec "$@"


