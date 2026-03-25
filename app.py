import os
import traceback

from flask import Flask
from database import db
from flask_login import LoginManager
from dotenv import load_dotenv

load_dotenv()

login_manager = LoginManager()


def _init_db(app):
    """Read init_db.sql and execute it against the configured database.

    The script uses CREATE TABLE IF NOT EXISTS and INSERT … ON CONFLICT DO
    NOTHING, so it is fully idempotent and safe to run on every startup.
    Falls back gracefully when the database is SQLite (development) or when
    the SQL file is not present.
    """
    sql_path = os.path.join(os.path.dirname(__file__), 'init_db.sql')
    print(f'[init_db] SQL file path: {sql_path}', flush=True)

    if not os.path.exists(sql_path):
        print('[init_db] WARNING: init_db.sql not found — skipping automatic DB init.', flush=True)
        return

    db_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    # Mask credentials for safe logging: show scheme + host only
    try:
        from urllib.parse import urlparse as _urlparse
        _p = _urlparse(db_url)
        masked_url = f'{_p.scheme}://***:***@{_p.hostname}:{_p.port or 5432}{_p.path}'
    except Exception:
        masked_url = '<unparseable>'
    print(f'[init_db] DATABASE_URL (masked): {masked_url}', flush=True)

    if not db_url.startswith('postgresql'):
        # SQLite / other backends: rely on SQLAlchemy's create_all() instead.
        print('[init_db] Non-PostgreSQL database detected — skipping init_db.sql.', flush=True)
        return

    try:
        import psycopg2
        from urllib.parse import urlparse

        print('[init_db] Connecting to PostgreSQL…', flush=True)
        parsed = urlparse(db_url)
        conn = psycopg2.connect(
            dbname=parsed.path.lstrip('/'),
            user=parsed.username,
            password=parsed.password,
            host=parsed.hostname,
            port=parsed.port or 5432,
        )
        conn.autocommit = True
        print('[init_db] Connection established. Reading SQL file…', flush=True)
        with open(sql_path, 'r') as fh:
            sql = fh.read()
        print(f'[init_db] Executing {len(sql)} bytes of SQL…', flush=True)
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.close()
        print('[init_db] Database initialised successfully from init_db.sql.', flush=True)
    except Exception as exc:
        # Print full traceback so the exact failure is visible in gunicorn logs.
        print('[init_db] ERROR: Database initialisation failed:', flush=True)
        print(traceback.format_exc(), flush=True)


def _seed_sample_users(app):
    """Insert sample teacher and student accounts if they do not yet exist.

    Uses SQLAlchemy so this works for both PostgreSQL and SQLite.  Passwords
    are hashed with Werkzeug's default algorithm so they are immediately usable
    through the login form.
    """
    print('[seed] Starting sample user seed…', flush=True)
    try:
        from models import User
        from werkzeug.security import generate_password_hash

        with app.app_context():
            seeds = [
                ('Test Teacher', 'teacher@example.com', 'password', 'teacher'),
                ('Test Student', 'student@example.com', 'password', 'student'),
            ]
            added = []
            for name, email, password, role in seeds:
                if not User.query.filter_by(email=email).first():
                    user = User(
                        name=name,
                        email=email,
                        password_hash=generate_password_hash(password),
                        role=role,
                    )
                    db.session.add(user)
                    added.append(email)
            if added:
                db.session.commit()
                print(f'[seed] Seeded sample users: {", ".join(added)}', flush=True)
            else:
                print('[seed] Sample users already present — skipping seed.', flush=True)
    except Exception as exc:
        print('[seed] ERROR: Failed to seed sample users:', flush=True)
        print(traceback.format_exc(), flush=True)


def create_app():
    print('[create_app] create_app() called — starting application factory.', flush=True)
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret')
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///attendance.db')
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Register user loader after login_manager initialized
    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except Exception:
            return None

    # Add custom filter for IST time formatting
    from utils import format_ist_time
    app.jinja_env.filters['format_ist_time'] = format_ist_time

    # Blueprints
    from auth import auth_bp
    from teacher_routes import teacher_bp
    from student_routes import student_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(student_bp)

    # Initialise schema and seed data on every startup (all operations are
    # idempotent — existing tables and rows are left untouched).
    with app.app_context():
        # For PostgreSQL: run the raw SQL file so the schema is authoritative.
        # For SQLite (local dev): fall back to SQLAlchemy's create_all().
        _init_db(app)
        db.create_all()
        _seed_sample_users(app)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
