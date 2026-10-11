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
es (`dj-database-url` + `psycopg`), serve static files with WhiteNoise, and run with Gunicorn. Then add user accounts so each person only sees their own sessions.
