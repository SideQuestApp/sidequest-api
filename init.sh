#!/bin/bash

# venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# venv vars
source .env

# psql
psql -h $DB_HOST -U $DB_USER -d postgres -c "
CREATE DATABASE $DB_NAME;
"
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';

ALTER ROLE $DB_USER SET client_encoding TO 'utf8';
ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';
ALTER ROLE $DB_USER SET timezone TO 'EST';

GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
"
