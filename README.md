# Student Complaint Portal

A Django-based web application for students to submit complaints across key sections and for staff (Faculty, HOD, Admin) to review and manage them while preserving student anonymity.

## Key Features

- 20 credits granted on student registration; +5 credits for each valid complaint (wallet transactions recorded)
- 5-day cooldown per section for raising a new complaint
- Staff can see complaint details without student identity (only student department is shown)

## Features

- Student registration with enrollment number, name, phone, stream (BCA, BTech, MTech, MSc IT, MBA, BBA, MCA), and password
- Staff registration (Faculty, HOD, Admin) with college ID, name, phone, email, department, and password
- Sections: Cleaning, Teaching Faculty, Staff Behavior, Infrastructure, Student Behavior
- Complaint submission with title, description, and media upload (image/video)
- 20 credits granted on student registration; +5 credits for each valid complaint (wallet transactions recorded)
- Status workflow: Open → In Process → Closed
- Escalation levels: Class Mentor → HOD → Admin Office
- 5-day cooldown per section for raising a new complaint
- Staff can see complaint details without student identity (only student department is shown)
- Responsive and aesthetic UI with modern CSS, hover effects, gradients
- Admin site to manage users and complaints

## Tech Stack

- Python 3.13+
- Django 5
- Database: SQLite (default) or MySQL Community (via PyMySQL)
- HTML/CSS (no JS framework required)

## Project Structure

- core/ – Django project settings and URLs
- accounts/ – Custom User model and auth views
- complaints/ – Complaint models, views, URLs
- templates/ – HTML templates
- static/ – CSS and assets
- media/ – Uploaded files (during development)

## Quickstart (Windows PowerShell)

1) Create and activate virtual env, install deps

   - Already set up locally in .venv and requirements installed during scaffolding.

2) Configure environment variables

   - Copy .env.example to .env and adjust as needed.
   - By default the project uses SQLite (DB_ENGINE=sqlite3). To use MySQL, set DB_ENGINE=mysql and configure DB_* values.

3) Run migrations

   - Already executed once. To re-run (if you change models):
     .\.venv\Scripts\python manage.py makemigrations
     .\.venv\Scripts\python manage.py migrate

4) Create superuser (non-interactive example)

   - Set environment variables (replace with your values) and run:
     $env:DJANGO_SUPERUSER_USERNAME = "{{admin_username}}"
     $env:DJANGO_SUPERUSER_EMAIL = "{{admin_email}}"
     $env:DJANGO_SUPERUSER_PASSWORD = "{{admin_password}}"
     .\.venv\Scripts\python manage.py createsuperuser --noinput

5) Run the development server

     .\.venv\Scripts\python manage.py runserver

   Open http://127.0.0.1:8000

## Switching to MySQL

1) Ensure MySQL Community is installed and running.
2) Create a database (e.g., student_portal) and a user with privileges.
3) Install PyMySQL (already installed): pymysql
4) In .env, set:

   DB_ENGINE=mysql
   DB_NAME=student_portal
   DB_USER={{mysql_user}}
   DB_PASSWORD={{mysql_password}}
   DB_HOST=127.0.0.1
   DB_PORT=3306

5) Run migrations again:

   .\.venv\Scripts\python manage.py migrate

## Default URLs

- / – Home
- /register/student/ – Student registration
- /register/staff/ – Staff registration
- /login/ – Login
- /dashboard/ – User dashboard (student or staff)
- /complaints/ – List complaints (own for students, all for staff)
- /complaints/new/ – Submit new complaint

## Notes

- File uploads in development are served via Django when DEBUG=True.
- For production, configure proper static/media hosting and set ALLOWED_HOSTS in .env.
- The app preserves student anonymity for staff views by only showing the student department.
- Credits are tracked and transactions recorded for auditability.
- <img width="1920" height="1080" alt="Screenshot (5)" src="https://github.com/user-attachments/assets/32a07c14-a3f5-4e9a-9cc9-005ecbc5e2e4" />
<img width="1920" height="1080" alt="Screenshot (4)" src="https://github.com/user-attachments/assets/15120401-c28c-44e3-b017-e65ecb78f13b" />
- <img width="1920" height="1080" alt="Screenshot (3)" src="https://github.com/user-attachments/assets/802e3801-a357-4ce9-a631-182b219ce7b9" />
<img width="1920" height="1080" alt="Screenshot (2)" src="https://github.com/user-attachments/assets/670538fe-dd2f-4c87-b3c4-70f9573f2946" />
<img width="1920" height="1080" alt="Screenshot 2025-09-15 092525" src="https://github.com/user-attachments/assets/a03457e4-78cb-44cd-9cb3-0d253b626efd" />
<img width="1920" height="1080" alt="Screenshot (6)" src="https://github.com/user-attachments/assets/788583c4-e0ef-46aa-9d87-a06e67f0ccbb" />

