#!/usr/bin/env bash

sleep 5

source /home/atu/projects/.venv/bowlero_backend/bin/activate
cd /home/atu/projects/bowlero_backend
exec flower -A bowlero_backend --port=8008
