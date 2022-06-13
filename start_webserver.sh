#!/bin/sh
cd /pi-enviro
# exec source venv/bin/activate
exec gunicorn app:server -b :8050
