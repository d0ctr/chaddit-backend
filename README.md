# If using nginx to proxy
This app uses headers with underscores, so in order to make it work set `underscores_in_headers on;` in your default server configuration (/etc/nginx/sites-available/default **by default**).

# Using environment variables
 - `FLASK_ENV` — environment type (development | production)
 - `FLASK_APP` — name of main flask app module
 - `DATABASE_URL` — database url for use with backend
 - `JWT_SECRET_KEY` — key to hash password
 - `ADMIN_PSWD` — password for admin user to be set on initial startup
 - `ADMIN_EMAIL` — email for admin user to be set on initial startup
 - `MIGRATIONS_DIR` — full or relative to current directory path to alembic migrations
 - `BACKEND_LOGS` — path where to store logs