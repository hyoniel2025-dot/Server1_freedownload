#!/usr/bin/env bash

# ⚡ Actualizar paquetes e instalar 7zip
apt-get update && apt-get install -y p7zip-full

# ⚡ Iniciar servidor FastAPI con Gunicorn + Uvicorn
#    main:app → archivo main.py, variable app de FastAPI
exec gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT --workers 1
