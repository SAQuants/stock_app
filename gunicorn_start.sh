#!/bin/bash
# copied from https://dylancastillo.co/fastapi-nginx-gunicorn/

NAME=stock_app_be
DIR=/home/azureuser/stock_app_be
# USER=fastapi-user
# GROUP=fastapi-user
WORKERS=3
WORKER_CLASS=uvicorn.workers.UvicornWorker
VENV=$DIR/venv/bin/activate
BIND=unix:$DIR/run/gunicorn.sock
LOG_LEVEL=error

cd $DIR
source $VENV

exec gunicorn main:app \
  --name $NAME \
  --workers $WORKERS \
  --worker-class $WORKER_CLASS \
  --bind=$BIND \
  --log-level=$LOG_LEVEL \
  --log-file=-

#  --user=$USER \
#  --group=$GROUP \
