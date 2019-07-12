#!/usr/bin/env bash

source /home/atu/projects/.venv/bowlero_backend/bin/activate
cd /home/atu/projects/bowlero_backend
exec celery -A bowlero_backend beat
