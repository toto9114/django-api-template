ARG PYTHON_VERSION=3.11.2
FROM python:${PYTHON_VERSION}-buster

ENV PROJECT_DIR /app

RUN apt-get update && apt-get upgrade -y \
    && apt install -y sudo nginx unzip less gettext-base \
    # dependencies for building Python packages
    build-essential \
    # mysql client dependencies
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install poetry

RUN mkdir -p ${PROJECT_DIR} \
    && mkdir -p ${PROJECT_DIR}/logs \
    && useradd -u 1000 -ms /bin/bash -d /home/jihun -G sudo,staff,www-data jihun \
    && echo "jihun ALL=NOPASSWD: ALL" >> /etc/sudoers \
    && poetry config virtualenvs.create false

WORKDIR ${PROJECT_DIR}
COPY . .

RUN chmod +x ${PROJECT_DIR}/docker/run_command/* \
    && ln -s ${PROJECT_DIR}/docker/run_command/* /usr/local/bin/

RUN PIP_NO_CACHE_DIR=true poetry install --no-root --without dev \
    && chown -R jihun:jihun /app

ENV PATH=${PROJECT_DIR}:${PATH}
ENV PYTHONPATH ${PATH}

USER jihun

VOLUME ["/app/logs"]
ENTRYPOINT ["./docker/run_command/start.sh"]
