#bin/bash

apt-get update && apt-get install -y postgresql-client

until pg_isready -h ${DB_HOST}; do
    echo 'waiting for psql to be connectable...'
    sleep 3
done
echo "psql is connectable."

export PGPASSWORD=${DB_PASSWORD}
psql -h ${DB_HOST} -U ${DB_USER} -p 5432 -d todo -f /app/init_db/init.sql
