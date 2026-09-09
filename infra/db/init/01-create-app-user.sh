#!/bin/bash
# Creates a non-superuser role for the app + migrations (Alembic).
# Runs once, on first container start, via /docker-entrypoint-initdb.d.
# APP_DB_USER / APP_DB_PASSWORD come from the compose environment (see postgres.yml).
set -euo pipefail

APP_DB_USER="${APP_DB_USER:-app}"
: "${APP_DB_PASSWORD:?APP_DB_PASSWORD must be set}"

psql -v ON_ERROR_STOP=1 \
     --username "$POSTGRES_USER" \
     --dbname "$POSTGRES_DB" \
     --set app_user="$APP_DB_USER" \
     --set app_password="$APP_DB_PASSWORD" \
     --set db_name="$POSTGRES_DB" <<-'EOSQL'
	-- Create the login role if it does not already exist.
	SELECT format('CREATE ROLE %I LOGIN PASSWORD %L', :'app_user', :'app_password')
	WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = :'app_user')
	\gexec

	-- Allow the role to connect to the application database.
	GRANT CONNECT ON DATABASE :"db_name" TO :"app_user";

	-- CREATE TABLE authority: USAGE + CREATE on the public schema.
	-- (Postgres 15+ no longer grants CREATE on public to PUBLIC by default.)
	GRANT USAGE, CREATE ON SCHEMA public TO :"app_user";

	-- Full DML on existing and future tables/sequences in public,
	-- so the app can create tables and then read/write them.
	GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO :"app_user";
	GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO :"app_user";
	ALTER DEFAULT PRIVILEGES IN SCHEMA public
	  GRANT ALL PRIVILEGES ON TABLES TO :"app_user";
	ALTER DEFAULT PRIVILEGES IN SCHEMA public
	  GRANT ALL PRIVILEGES ON SEQUENCES TO :"app_user";
EOSQL

echo "Role '$APP_DB_USER' is ready with CREATE privileges on schema public in '$POSTGRES_DB'."
