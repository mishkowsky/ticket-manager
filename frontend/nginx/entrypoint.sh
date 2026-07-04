#!/usr/bin/env sh
set -e

echo "Generating nginx.conf from template..."

VARS=$(env | cut -d= -f1 | sed 's/^/$/')

envsubst "$VARS" < /etc/nginx/templates/nginx.conf.template > /etc/nginx/nginx.conf

echo "Starting nginx..."
exec nginx -g "daemon off;"