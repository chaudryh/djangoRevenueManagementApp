#!/usr/bin/env bash

source /home/webapp/.venv/bowlero_backend/bin/activate
cd /home/webapp/bowlero_backend
exec celery -A bowlero_backend beat
