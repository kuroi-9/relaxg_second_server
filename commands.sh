#!/bin/bash

# Start the web server
daphne -b 0.0.0.0 -p 8000 rg_server.asgi:application &

# Start the celery worker
celery -A rg_server worker --loglevel=info &

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?
