ARG PYTHON_VERSION=3.10.5-slim-bullseye

# define an alias for the specfic python version used in this file.
FROM python:${PYTHON_VERSION} as python

# FROM ubuntu:20.04 as python

# Python build stagew
FROM python as python-build-stage

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=1.3.1

ARG BUILD_ENVIRONMENT=local

# Install apt packages
RUN apt-get update && apt-get install --no-install-recommends -y \
  # dependencies for building Python packages
  build-essential \
  # psycopg2 dependencies
  libpq-dev \
  ffmpeg


# Install Poetry
RUN pip install "poetry==$POETRY_VERSION"

# Install Data Science stuff
RUN pip install --no-cache-dir psycopg2 psycopg2-binary

# # For playwright
# RUN apt-get update && apt-get -y install libnss3 libatk-bridge2.0-0 libdrm-dev libxkbcommon-dev libgbm-dev libasound-dev libatspi2.0-0 libxshmfence-dev libjpeg62-turbo-dev
# RUN echo "deb http://ftp.us.debian.org/debian buster main non-free" >> /etc/apt/sources.list.d/fonts.list
# RUN apt-get update && pip install playwright==1.30.0 && playwright install chromium && playwright install-deps chromium

# BL: adding poetry
# Requirements are installed here to ensure they will be cached.
COPY poetry.lock pyproject.toml ./

# BL: Install project dependencies
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi


# Python 'run' stage
FROM python-build-stage as python-run-stage

ARG BUILD_ENVIRONMENT=local
ARG APP_HOME=/app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV BUILD_ENV ${BUILD_ENVIRONMENT}

WORKDIR ${APP_HOME}


COPY ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY ./compose/local/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start


COPY ./compose/local/django/celery/worker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker
RUN chmod +x /start-celeryworker

COPY ./compose/local/django/celery/beat/start /start-celerybeat
RUN sed -i 's/\r$//g' /start-celerybeat
RUN chmod +x /start-celerybeat

COPY ./compose/local/django/celery/flower/start /start-flower
RUN sed -i 's/\r$//g' /start-flower
RUN chmod +x /start-flower


# copy application code to WORKDIR
COPY . ${APP_HOME}

ENTRYPOINT ["/entrypoint"]
