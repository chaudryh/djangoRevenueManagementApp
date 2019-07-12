#!/usr/bin/env bash

sleep 5

source /home/webapp/.venv/bowlero_backend/bin/activate
cd /home/webapp/bowlero_backend
exec flower -A bowlero_backend --port=8008
