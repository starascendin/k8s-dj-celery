	#!/bin/bash

	container_name="supabase_db_aininjas_local"
	username="postgres"
	database_name="postgres"
	table_name="django_migrations"
	output_file_path="/host/path/to/20230101010101_django_migrations.sql"

	docker exec -t $$container_name pg_dump -U $$username -F p $$database_name -t $$table_name -f $$output_file_path
