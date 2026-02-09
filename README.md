# Thuwala Website (Flask)

Quick reference to run, configure, and migrate the project.

Prerequisites
- Python 3.10+ (venv available)
- Project virtualenv (this repo contains `thuwala/` venv in development)

Environment
- Copy `.env.example` to `.env` and fill secrets before running in production.
- Required in production: `SECRET_KEY`, `SECURITY_PASSWORD_SALT`, `DATABASE_URL` (or use default SQLite).

Development (Windows)
1. Activate venv:
```powershell
call thuwala\Scripts\activate.bat
```
2. Install deps (only if you changed `requirements.txt`):
```powershell
pip install -r requirements.txt
```
3. Create `.env` from `.env.example` and set `FLASK_ENV=development`.
4. Start app:
```powershell
python app.py
```
Or run the helper script:
```powershell
start_project.bat
```

Notes
- Models, routes, and startup seeding live in `app.py` (single-file app). Avoid importing `app` in tests or tools that shouldn't trigger DB initialization.
- Default seeded admin user: username `admin`, password `Admin@2024` (created on first run if missing).
- Upload folder: `static/uploads` (configurable via `UPLOAD_FOLDER` env).

Database Schema Changes
- The app uses `db.create_all()` on startup for automatic table creation.
- For schema changes in development: delete `thuwala.db` and restart to recreate fresh.
- For production schema changes: apply manual `ALTER TABLE` SQL statements directly to your database.
- The app includes `init_or_migrate_database()` helper that attempts simple migrations automatically.

Postgres Deployment
- Run `scripts/update_for_postgres.py` to add PostgreSQL support to `config.py` and `requirements.txt`.
- Ensure `DATABASE_URL` environment variable uses the `postgresql://` scheme.
- The script will add `psycopg2-binary` to dependencies automatically.

Common commands
- Run health check: open `http://localhost:5000/health`
- Debug DB status: `http://localhost:5000/debug/db-status`

If anything in this README is unclear or you want me to add CI/deploy steps, tell me which area to expand.

## CI / Deploy (short)

Render (recommended quick deploy):
- Set environment variables in the Render dashboard: `DATABASE_URL`, `SECRET_KEY`, `SECURITY_PASSWORD_SALT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_DEFAULT_SENDER`, and `PORT`.
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 4`

Gunicorn / systemd (self-host):
- Install dependencies and export env vars (see `.env.example`).
- Run with:
```
gunicorn app:app --bind 0.0.0.0:5000 --workers 4
```
- For systemd, create a service that activates the venv and runs the Gunicorn command, exposing the `PORT` via environment.

CI Tips:
- Run `pytest` (if tests added) and `flake8`/`black` as desired before deploy.
- Database tables are created automatically on first run via `db.create_all()`.
- Use `scripts/smoke_test.py` for basic health checks after deployment.

Utility Scripts (in `scripts/` folder):
- `check_admin.py` - Verify admin user credentials
- `smoke_test.py` - Test all public pages are accessible
- `generate_favicon.py` - Generate favicon files from logo
- `generate_webp.py` - Convert images to WebP format
- `update_for_postgres.py` - Add PostgreSQL support
- `setup.py` - Initial project folder setup
