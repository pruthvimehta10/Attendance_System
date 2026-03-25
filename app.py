import os
from datetime import timedelta

from flask import Flask
from database import db
from flask_login import LoginManager
from dotenv import load_dotenv

load_dotenv()

login_manager = LoginManager()


def create_app():
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

    # Create DB tables if not present
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
