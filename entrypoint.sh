#!/bin/bash
set -e

# Run migrations
alembic upgrade head

# Start the application
exec "$@"
