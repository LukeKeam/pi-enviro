#!/bin/bash
cd /pi-enviro
source venv/bin/activate
gunicorn app:server -b :8050
