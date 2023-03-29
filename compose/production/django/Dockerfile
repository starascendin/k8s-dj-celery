ARG PYTHON_VERSION=3.10.5-slim-bullseye



# define an alias for the specfic python version used in this file.
FROM python:${PYTHON_VERSION} as python

# Python build stage
FROM python as python-build-stage
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=1.3.1

ARG BUILD_ENVIRONMENT=production

# Install apt packages
RUN apt-get update && apt-get install --no-install-recommends -y \
  # dependencies for building Python packages
  build-essential \
  # psycopg2 dependencies
  libpq-dev \
  ffmpeg

# # Requirements are installed here to ensure they will be cached.
COPY poetry.lock pyproject.toml ./
# COPY ./requirements .

# # Create Python Dependency and Sub-Dependency Wheels.
# RUN pip wheel --wheel-dir /usr/src/app/wheels  \
#   -r ${BUILD_ENVIRONMENT}.txt


# Install Poetry
RUN pip install "poetry==$POETRY_VERSION"

# Install Data Science stuff
RUN pip install --no-cache-dir psycopg2 psycopg2-binary

# BL: Install project dependencies
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi


# Python 'run' stage
FROM python-build-stage as python-run-stage

ARG BUILD_ENVIRONMENT=production
ARG APP_HOME=/app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV BUILD_ENV ${BUILD_ENVIRONMENT}

WORKDIR ${APP_HOME}

# RUN mkdir $APP_HOME/staticfiles
# RUN mkdir $APP_HOME/mediafiles

# RUN addgroup --system django \
#     && adduser --system --ingroup django django


# # Install required system dependencies
# RUN apt-get update && apt-get install --no-install-recommends -y \
#   # psycopg2 dependencies
#   libpq-dev \
#   # Translations dependencies
#   gettext \
#   # cleaning up unused files
#   && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
#   && rm -rf /var/lib/apt/lists/*

# # All absolute dir copies ignore workdir instruction. All relative dir copies are wrt to the workdir instruction
# # copy python dependency wheels from python-build-stage
# COPY --from=python-build-stage /usr/src/app/wheels  /wheels/

# # use wheels to install python dependencies
# RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/* \
#   && rm -rf /wheels/


COPY ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint


COPY ./compose/production/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start



COPY ./compose/production/django/celery/worker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker
RUN chmod +x /start-celeryworker


COPY ./compose/production/django/celery/beat/start /start-celerybeat
RUN sed -i 's/\r$//g' /start-celerybeat
RUN chmod +x /start-celerybeat


COPY ./compose/production/django/celery/flower/start /start-flower
RUN sed -i 's/\r$//g' /start-flower
RUN chmod +x /start-flower


# copy application code to WORKDIR
COPY . ${APP_HOME}
# RUN python ${APP_HOME}/manage.py collectstatic --noinput

# # make django owner of the WORKDIR directory as well.
# RUN ${APP_HOME}


# RUN chmod -R 755 /app/staticfiles
# RUN chown django:django /app/staticfiles

# USER django

ENTRYPOINT ["/entrypoint"]
