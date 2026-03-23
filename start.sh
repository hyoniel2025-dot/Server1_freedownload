#!/usr/bin/env bash

# instalar 7zip
apt-get update && apt-get install -y p7zip-full

# iniciar servidor con Gunicorn + Uvicorn
exec gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT --workers 1