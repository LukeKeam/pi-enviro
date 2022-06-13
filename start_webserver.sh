#!/bin/sh
source /pi-enviro/venv/bin/activate
cd /pi-enviro
gunicorn app:server -b :8050
