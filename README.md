# StudyLog

A small Django web app for logging study sessions. You enter a course, how many minutes you studied, and the date. The app then shows:

- **Weekly progress** toward a goal you set (progress bar, time remaining)
- **Day streak**: how many days in a row you've studied
- **Last 7 days**: bar chart of minutes per day
- **Per-course breakdown**: totals and percentages, with a detail page for each course
- Edit and delete sessions, plus **CSV export**

Built for the CSCE 490 Research Milestone to learn Django and the `uv` package manager.

## Tech stack

| Piece | Choice | Why |
|---|---|---|
| Language | Python 3.12+ | Team's chosen language |
| Framework | Django 6.x | Batteries included: ORM, forms, admin, migrations, CSRF |
| Package manager | [uv](https://docs.astral.sh/uv/) | Fast, makes the venv for you, `uv.lock` pins exact versions |
| Database | SQLite (dev) | Zero setup. Switch to Postgres for deployment |
| Frontend | Django templates + plain CSS | No JS build step needed |

## Running it

```bash
# 1. Install uv (once):  curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync                              # creates .venv and installs exact versions from uv.lock
uv run python manage.py migrate      # creates db.sqlite3 and tables
uv run python manage.py runserver    # open http://127.0.0.1:8000
```

Optional: `uv run python manage.py createsuperuser` to use the admin at `/admin/`.

Run the tests with `uv run python manage.py test`.

## Project layout

```
config/          project settings + root URLs
tracker/
  models.py      StudySession, WeeklyGoal, current_streak()
  forms.py       ModelForms with validation (no future dates)
  views.py       dashboard, edit, delete, course detail, goal, CSV export
  urls.py        app routes
  templates/     base layout + pages + reusable partials
  static/        style.css (includes dark mode)
  tests.py       8 unit/integration tests
```

## What I learned

- **uv**: `uv init` makes a project, `uv add django` updates `pyproject.toml` *and* `uv.lock`, and `uv run` runs commands inside the venv without activating it. Committing `uv.lock` is what keeps a teammate's install identical to mine.
- **Django request flow**: URL → view → (model/form) → template. Using Post/Redirect/Get after a form submit stops the browser from re-submitting on refresh.
- **ORM aggregation**: `values("course").annotate(Sum("minutes"))` does the GROUP BY inside the database.
- **Migrations**: when you change a model, `makemigrations` writes the change to a file, `migrate` applies it, and the files go into git.
- **Security defaults**: `{% csrf_token %}` on every POST form. Delete only accepts POST (`@require_POST`), so a link can't delete data.

## Next steps / deployment notes

For production: set `DEBUG=False`, read `SECRET_KEY` and `ALLOWED_HOSTS` from environment variables, switch to Postgres (`dj-database-url` + `psycopg`), serve static files with WhiteNoise, and run with Gunicorn. Then add user accounts so each person only sees their own sessions.
