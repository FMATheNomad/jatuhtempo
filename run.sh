#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"

if ! pg_isready -q 2>/dev/null; then
    echo "Memulai PostgreSQL..."
    echo "fariz5410" | sudo -S mkdir -p /run/postgresql
    echo "fariz5410" | sudo -S chown postgres:postgres /run/postgresql
    echo "fariz5410" | sudo -S -u postgres pg_ctl -D /var/lib/postgres/data -l /tmp/pg.log start
    sleep 2
fi

cd "$DIR" && source .venv/bin/activate
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
