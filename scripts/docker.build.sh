#!/usr/bin/env bash
PROJECT_NAME=django-api-template/backend

docker build --network host -t ${PROJECT_NAME} .
