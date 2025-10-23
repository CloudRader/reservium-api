#!/usr/bin/env bash

set -e

echo "Run apply migrations.."

PROJECT_ROOT=$(dirname "$0")/..
cd "$PROJECT_ROOT" || exit

alembic upgrade head
cd src/
echo "Migrations applied!"

exec "$@"