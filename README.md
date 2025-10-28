# Event Planner

A Flask-based web application to create and manage events with role-based access:
- Admins: create / update / delete events, view RSVP summaries.
- Users: browse events, view details, RSVP (Going / Maybe / Decline), and edit RSVPs before event start.

Live demo: https://event-planner-iixt.onrender.com 
Demo video: https://drive.google.com/file/d/1wa_mN-DR--OVhPb2GUA-gawekhTg4Bhr/view?usp=sharing 

---

## Table of contents
- Project overview
- Quick setup & installation (Windows)
- Environment variables
- Database & migrations
- Create admin user
- Run the app 
- Technologies used
- ER diagram 
- Web routes & API endpoints
- Deployment
- Notes / next steps

---

## Project overview
This project implements a small event management platform:
- Users can register, log in, view events, and RSVP (Going / Maybe / Decline).
- Admins can create, edit, and delete events and view RSVP summaries per event.
- RSVP is recorded per user per event and can be updated until the event start.

---

## Quick setup & installation (Windows)

1. Clone repository:
   ```
   git clone https://github.com/your-username/your-repo-name.git c:\Users\tanya\Desktop\event_planner
   cd c:\Users\tanya\Desktop\event_planner
   ```

2. Create & activate virtual environment and install dependencies:
   ```
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create `.env` in project root with at minimum:
   ```
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY='replace-with-secure-key'
   DATABASE_URL='postgresql://user:pass@localhost/event_planner'  # or mysql+pymysql://...
   ```

4. Initialize DB & apply migrations:
   ```
   flask db init      # only if migrations/ not present
   flask db migrate
   flask db upgrade
   ```

5. Create admin user (Flask shell):
   ```
   flask shell
   >>> from app import db
   >>> from app.models import User
   >>> admin = User(email='admin@example.com', role='Admin', name='Admin')
   >>> admin.set_password('YourStrongPassword')
   >>> db.session.add(admin); db.session.commit()
   >>> exit()
   ```

6. Run development server:
   ```
   python run.py
   ```
   Visit http://127.0.0.1:5000


---

## Environment variables
Add these keys to `.env` (example):
- FLASK_APP=run.py
- FLASK_ENV=development
- SECRET_KEY=your-secret
- DATABASE_URL=postgresql://user:pass@host/dbname
- MAIL_* (if email features added)

The project reads DATABASE_URL for SQLAlchemy.

---

## Technologies used
- Python — core language.
- Flask — server-side web framework (SSR).
- Flask-SQLAlchemy — ORM for Postgres/MySQL.
- Flask-Migrate (Alembic) — migrations.
- Flask-Login — authentication & session management.
- Flask-WTF — forms + validation + CSRF.
- Gunicorn — production WSGI server.
- pytest — testing.

Rationale: lightweight, well-documented stack good for CRUD apps with role-based auth and simple deployment to Render/Heroku.

---

## ER diagram (Mermaid)
This diagram shows relationships between User, Event, and RSVP.

```mermaid
erDiagram
    USER ||--o{ EVENT : "creates"
    USER ||--o{ RSVP : "submits"
    EVENT ||--o{ RSVP : "collects"

    USER {
        int id PK
        string email
        string password_hash
        string role
        string name
    }
    EVENT {
        int id PK
        string title
        string description
        date date
        time start_time
        time end_time
        string location
        int admin_id FK
    }
    RSVP {
        int id PK
        string status
        int user_id FK
        int event_id FK
        timestamp updated_at
    }
```

---

## Web routes & API endpoints (method, route, purpose)

Authentication
- GET, POST /register — Render registration page / create new user (default role: User).
- GET, POST /login — Render login form / authenticate user.
- GET /logout — Log out current user.

Core pages (web)
- GET / or /welcome — Public landing page.
- GET /home — Dashboard (login required). Lists upcoming events sorted by date.
- GET /my_rsvps — Shows events current user has RSVP'd to (login required).
- GET /event/<int:event_id> — Event detail page with RSVP form (login required).

Event (Admin)
- GET, POST /event/new — Create new event (Admin only).
- GET, POST /event/<int:event_id>/update — Edit event (Admin only).
- POST /event/<int:event_id>/delete — Delete event and associated RSVPs (Admin only).
- GET /event/<int:event_id>/summary — RSVP summary (Going, Maybe, Decline counts) (Admin only).

RSVP (User actions)
- POST /event/<int:event_id>/rsvp — Submit or update RSVP for current user (status in form: Going|Maybe|Decline). The server upserts to prevent duplicate entries.
- GET /api/users/<int:user_id>/rsvps — (API) Return RSVPs for a user (user or admin).

API endpoints (JSON-focused)
- GET /api/events — Return JSON list of upcoming events (sorted).
- GET /api/events/<int:event_id> — Return JSON event details.
- POST /api/events — Create event (Admin only) — JSON body: {title, description, date, start_time, end_time, location}.
- PUT /api/events/<int:event_id> — Update event (Admin only).
- DELETE /api/events/<int:event_id> — Delete event (Admin only).
- POST /api/events/<int:event_id>/rsvp — Create/update RSVP (user). Body: {status: "Going"|"Maybe"|"Decline"}.
- GET /api/events/<int:event_id>/rsvps — Admin-only RSVP summary JSON: {Going: N, Maybe: M, Decline: D}.

Notes:
- All POST/PUT endpoints validate input and require CSRF token for forms.
- RSVP creation uses upsert on (user_id, event_id) to prevent duplicates.
- Editing RSVPs allowed until event start datetime.

---

## Deployment
Recommended targets: Render, Heroku, DigitalOcean App Platform. The app is configured to use Gunicorn in production. Use environment variables on the hosting provider to set SECRET_KEY and DATABASE_URL.

Deployed application:  
 https://event-planner-iixt.onrender.com 

Demo video (required, 3–5 min) showing signup/login, role-based access, event CRUD (admin), RSVP actions (user), and RSVP summary:  
https://youtu.be/eSO8qhcfj_4

---

## Testing
Run unit and integration tests:
```
.\venv\Scripts\activate
pytest
```
Add tests in `tests/` for auth, event CRUD, and RSVP logic (duplicate prevention and upsert behavior).

---

## Notes / next steps
- Add email verification and password reset.
- Add pagination for events and caching for RSVP summaries.
- Add rate-limiting and stronger input sanitization for production.
- Add CI (GitHub Actions) to run tests and lint on push.
- If using MySQL locally, update DATABASE_URL accordingly.

