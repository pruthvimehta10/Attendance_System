# Flask Attendance System

Simple cloud-ready attendance system built with Flask, Flask-Login, and SQLite.

Quick start

1. Copy `.env.example` to `.env` and set `SECRET_KEY`.
2. Create virtualenv and install dependencies:

```bash
python -m venv venv
venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

3. Initialize DB with sample users (for local testing):

```bash
python create_db.py
```

4. Run:

```bash
python app.py
```

Default sample accounts: `teacher@example.com` and `student@example.com` (password: `password`).

Deployment notes
- Use environment variables for `SECRET_KEY` and `DATABASE_URL`.
- On cloud platforms behind proxies, ensure `X-Forwarded-For` is forwarded so IP checks work.
