#!/bin/sh
#set -x
set -e

export FLASK_APP="geometry_service"
export SECRET_KEY="$(dd if=/dev/urandom bs=12 count=1 status=none | xxd -p -c 12)"

if [ -f "${DB_PASS_FILE}" ]; then
    DB_PASS="$(cat ${DB_PASS_FILE})"
fi
export DATABASE_URI="${DB_ENGINE}://${DB_USER}:${DB_PASS}@${DB_HOST}:${DB_PORT}/${DB_NAME}"

# Initialize database

flask init-db

# Run

exec nosetests $@
