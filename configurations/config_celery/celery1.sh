#!/usr/bin/env bash

source /home/webapp/.venv/bowlero_backend/bin/activate
cd /home/webapp/bowlero_backend
exec celery worker -A bowlero_backend --loglevel=INFO -n worker1@%h