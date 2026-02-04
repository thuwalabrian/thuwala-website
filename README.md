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

Database migrations (recommended)
- Alembic is included for migrations. Workflow:
```powershell
# generate migration (autogenerate reads models from app)
alembic revision --autogenerate -m "describe change"
# apply
alembic upgrade head
```
- If not using Alembic, apply manual ALTER statements on your DB. The app contains a fragile `init_or_migrate_database()` helper but prefer explicit migrations for production.

Postgres deployment notes
- `update_for_postgres.py` can update `config.py` and `requirements.txt` to include `psycopg2-binary` and `alembic`. Ensure `DATABASE_URL` uses the `postgresql://` scheme.

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

CI tips:
- Run `pytest` (if tests added) and `flake8`/`black` as desired before deploy.
- Run Alembic migrations during deploy: `alembic upgrade head` after the app dependencies are installed and env vars are set.
