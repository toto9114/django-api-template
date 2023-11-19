#!/usr/bin/env bash
PROJECT_NAME=django-api-template/backend

docker run -it --rm \
  -p 5000:5000 \
 ${PROJECT_NAME} "${@:1}"
