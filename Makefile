SHELL := /bin/bash

source_local_env:
	bash -c "set -a && source .local.env"

run_local_django:
	source .local.env && export DJANGO_READ_DOT_ENV_FILE=True && python manage.py migrate && python manage.py runserver_plus 0.0.0.0:5000

run_local_celery:
	source .local.env && export DJANGO_READ_DOT_ENV_FILE=True && bash compose/local/django/celery/worker/start

run_local_flower:
	bash -c "set -a && source .local.env" && export DJANGO_READ_DOT_ENV_FILE=True && bash compose/local/django/celery/flower/start

run_local_beat:
	source .local.env && export DJANGO_READ_DOT_ENV_FILE=True && bash compose/local/django/celery/beat/start

run_local_all: run_local_django run_local_celery run_local_flower run_local_beat

# Run this to get all local services running
run_docker_up:
	docker-compose up -d

# When you add a package with Poetry, run this to rebuild and restart the containers
run_docker_stop_build_up:
	docker-compose down && docker-compose up -d --build

run_remote_sb_docker_stop_build_up:
	docker-compose down && docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d --build

dco_prod_down:
	docker-compose -f prod.yml down

dco_prod_up:
	docker-compose -f prod.yml up -d
dco_all_env_down:
	docker-compose -f prod.yml -f docker-compose.dev.yml -f docker-compose.dev_remote.yml down

dco_all_env_up:
	docker-compose -f prod.yml -f docker-compose.dev.yml -f docker-compose.dev_remote.yml up -d


sb_start:
	supabase start
sb_stop:
	supabase stop --backup

create_django_migration:
	./scripts/dump_postgres_table.sh

generate_openapi:
	npx @openapitools/openapi-generator-cli generate  -i https://api.ikigaidojo.ninja/api/openapi.json  -g typescript-fetch  -o generated-client  --additional-properties=supportsES6=true --skip-validate-spec