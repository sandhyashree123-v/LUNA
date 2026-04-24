#!/bin/sh
set -eu

cd /home/site/wwwroot/InnerVoice_Jelly

PORT_TO_USE="${PORT:-8000}"

exec gunicorn \
  -w 2 \
  -k uvicorn.workers.UvicornWorker \
  -b "0.0.0.0:${PORT_TO_USE}" \
  backend:app
