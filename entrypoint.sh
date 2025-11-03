#!/bin/sh
set -e

mkdir -p /code/db

echo "Aplicando migrations..."
python manage.py migrate --noinput

echo "Iniciando o servidor Django..."
exec "$@"
