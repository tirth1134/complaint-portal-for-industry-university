# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

Repository: Student Complaint Portal (Django)

Overview
- Purpose: Web app for students to submit complaints; staff (Faculty, HOD, Admin) review/manage with student anonymity preserved.
- Stack: Python 3.13+, Django 5, SQLite by default, optional MySQL, python-dotenv for .env loading.
- Apps: accounts (custom user and auth flows), complaints (complaint lifecycle), core (project settings/urls).

Environment & Configuration
- Copy .env.example to .env and adjust values as needed. Key envs:
  - DEBUG, ALLOWED_HOSTS
  - DB_ENGINE: sqlite3 (default) or mysql
  - If DB_ENGINE=mysql, also set DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT.
- Virtualenv: repo assumes .venv exists locally. Activate before running commands.
  - PowerShell (Windows): .\.venv\Scripts\Activate.ps1
  - Bash/zsh (Linux/macOS): source .venv/bin/activate
- Database drivers:
  - SQLite: built-in, no extra driver.
  - MySQL: install a compatible driver (e.g., mysqlclient or PyMySQL) and ensure DB credentials in .env are valid.

Common Commands (PowerShell shown; replace interpreter with python on Unix)
- Run development server
  - .\.venv\Scripts\python manage.py runserver
  - Opens http://127.0.0.1:8000
- Migrations
  - Make migrations after model changes: .\.venv\Scripts\python manage.py makemigrations
  - Apply migrations: .\.venv\Scripts\python manage.py migrate
- Create superuser (non-interactive)
  - $env:DJANGO_SUPERUSER_USERNAME = "{{admin_username}}"
  - $env:DJANGO_SUPERUSER_EMAIL = "{{admin_email}}"
  - $env:DJANGO_SUPERUSER_PASSWORD = "{{admin_password}}"
  - .\.venv\Scripts\python manage.py createsuperuser --noinput
- Run tests
  - All tests: .\.venv\Scripts\python manage.py test -v 2
  - Single app: .\.venv\Scripts\python manage.py test complaints -v 2
  - Single test (dotted path): .\.venv\Scripts\python manage.py test complaints.tests:TestClassName.test_method -v 2
- Linting/formatting
  - No linter/formatter config is present in this repo.

High-Level Architecture
- Authentication & Users (accounts app)
  - Custom user model (accounts.User) extends AbstractUser; configured via AUTH_USER_MODEL in core/settings.py.
  - Roles: STUDENT, FACULTY, HOD, ADMIN; additional fields include phone, department, enrollment_number (students), stream, credits, last_complaint_at, college_id (staff).
  - Registration flows:
    - Students register with enrollment_number; stored as username; initial credits=20.
    - Staff register with college_id; stored as username; role chosen from staff roles.
  - Login/logout: standard Django auth; redirects configured in settings (LOGIN_URL=/login/, LOGIN_REDIRECT_URL=/dashboard/).
  - Dashboard view renders student vs staff dashboards based on role.

- Complaints Domain (complaints app)
  - Core models:
    - Complaint: student FK to accounts.User; category (Cleaning/Faculty/Staff/Infra/Student), title/description, optional media upload, status (Open/In Process/Closed), level (Class/HOD/Admin), is_valid flag, timestamps.
    - ValidationLog: records staff validations with reviewer, valid flag, note, timestamp.
    - CreditTransaction: audit trail for credit changes (e.g., +5 for valid complaint).
  - Key invariants & flows:
    - Creation: Only STUDENT role can create complaints. Enforces a 5-day cooldown per category (checked against last complaint in that category).
    - Anonymity: For staff viewers, complaint_detail exposes only the student’s department, not identity.
    - Validation: Staff (FACULTY/HOD/ADMIN) can validate a complaint; marking valid awards +5 credits to the student and logs the transaction.
    - Status/Level updates: Staff can update status and escalation level.

- Routing & Integration
  - core/urls.py mounts:
    - '' → accounts.urls (home, registration, login/logout, dashboard)
    - 'complaints/' → complaints.urls (list/create/detail/validate/status)
  - Templates: settings include BASE_DIR/templates and app templates (APP_DIRS=True).
  - Static/Media:
    - STATICFILES_DIRS=[static], STATIC_ROOT=staticfiles; MEDIA_ROOT=media; MEDIA_URL=/media/.
    - During DEBUG=True, media served via Django (see core/urls.py).

MySQL Configuration Notes
- In .env set DB_ENGINE=mysql and provide DB_NAME/USER/PASSWORD/HOST/PORT.
- Ensure the database exists and the user has privileges.
- Install a MySQL driver in the active venv if not present (e.g., pip install mysqlclient or pip install pymysql) and run migrations again.

Admin
- Django admin enabled at /admin/ (django.contrib.admin installed). Use a superuser to manage users and complaints.

Source-of-Truth Pointers
- Quickstart, default URLs, and feature overview: README.md
- Environment template: .env.example
- Project settings: core/settings.py
- URL wiring: core/urls.py, accounts/urls.py, complaints/urls.py
- Domain models & logic: accounts/models.py, complaints/models.py, complaints/views.py
