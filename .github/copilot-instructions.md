## Purpose
Short, actionable guidance for AI coding agents working on this Flask website.

**Quick overview**: single-process Flask app (no blueprints) in `app.py`; SQLAlchemy models live in `app.py`; templates in `templates/`; static assets in `static/`.

## Architecture (big picture)
- **Main entry**: [app.py](app.py) — defines Flask app, SQLAlchemy `db`, all models, routes, and startup database seeding/initialization.
- **Config**: [config.py](config.py) — uses `python-dotenv`; `DATABASE_URL` controls DB (defaults to local SQLite `thuwala.db`).
- **UI**: Jinja templates under `templates/` (admin templates in `templates/admin/`). The app conditionally loads admin CSS/JS when request path starts with `/admin` (see [templates/base.html](templates/base.html)).
- **Static assets**: `static/` contains `css/`, `js/`, `images/`, and `uploads/` (upload folder set in config).

## Key patterns & conventions
- Single-file Flask app: expect model, route, and startup logic in `app.py` (search there first for behavioral changes).
- Admin pages are namespaced by URL prefix `/admin` and use templates under `templates/admin/` and conditional asset loading.
- DB migrations are not used. The app uses `db.create_all()` and an `init_or_migrate_database()` helper that attempts simple `ALTER TABLE` statements. Treat schema changes cautiously and prefer manual migrations for production.
- Default admin user is seeded on startup in `app.py` (username `admin`). Password in code is `Admin@2024` (note: `start_project.bat` prints a different password string — treat the code value as source of truth).

## Development workflows (how to run / debug)
- Windows quickstart: run `start_project.bat` at repo root. It activates the venv at `thuwala\Scripts\activate.bat`, installs `requirements.txt`, initializes DB, then runs `python app.py` ([start_project.bat](start_project.bat)).
- Alternate: activate your venv manually, `pip install -r requirements.txt`, then `python app.py`.
- Environment: put secrets in a `.env` file (loaded by `config.py`). Important env vars: `SECRET_KEY`, `DATABASE_URL`, `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_DEFAULT_SENDER`, `SECURITY_PASSWORD_SALT`.
- Postgres deployment helper: run [update_for_postgres.py](update_for_postgres.py) to update `config.py`/`requirements.txt`; follow its printed instructions and relocate DB init if promoting to production.

## Integration points and external dependencies
- Database: SQLAlchemy; default SQLite (`sqlite:///thuwala.db`) but accepts `DATABASE_URL` (Postgres requires `postgresql://` prefix — `update_for_postgres.py` fixes this).
- Email: `send_password_reset_email` in `app.py` uses SMTP and respects `MAIL_*` env variables; if not configured it prints a debug message and returns True (development safe path).
- Authentication: `Flask-Login` with `User` model in `app.py`.
- Other libs: see [requirements.txt](requirements.txt) — `Flask`, `Flask-SQLAlchemy`, `Flask-WTF`, `Flask-Login`, `python-dotenv`, `gunicorn`.

## What to watch for (pitfalls & guidance)
- Avoid assuming migrations: schema changes in dev may be auto-altered by `init_or_migrate_database()` but that logic is fragile — prefer recreating DB or applying manual ALTERs for production.
- Startup side-effects: importing `app` executes DB initialization and seeding (this happens inside `with app.app_context()` blocks near top of `app.py`). When editing tests or scripts, avoid importing `app` at top-level if you do not want side effects.
- Admin credentials: check `app.py` seed logic if you need to reset admin credentials; do not rely on the `start_project.bat` printed password string.
- File uploads: controlled by `UPLOAD_FOLDER` and `ALLOWED_EXTENSIONS` in `config.py` — enforce checks when adding new upload endpoints.

## Useful examples (where to change behavior)
- Add a new model or column: update `app.py` model classes and either (a) add SQL manually, (b) delete `thuwala.db` and restart for dev, or (c) implement Alembic migrations (preferred for production).
- Change admin UI: edit `templates/admin/*` and `static/css/admin.css`; admin routes are under `/admin` in `app.py`.
- SMTP/email debugging: `send_password_reset_email` logs debug when `MAIL_USERNAME`/`MAIL_PASSWORD` are missing — use that to simulate emails during dev.

## Minimal checklist for common tasks
- Running locally (Windows): double-click or run `start_project.bat`. For step-by-step: activate `thuwala` venv, `pip install -r requirements.txt`, `python app.py`.
- Add Postgres support: run `python update_for_postgres.py` and follow the printed steps.
- Finding where logic lives: search `app.py` first — models, routes, and startup logic are colocated there.

If any of these sections need more detail (deployment, test commands, or missing env values), tell me which area to expand. 
