#!/bin/bash
set -e
cd ${PROJECT_DIR}
gunicorn -c gunicorn.conf.py config.wsgi
