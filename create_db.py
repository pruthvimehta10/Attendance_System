"""Utility to create an initial database and sample users for testing."""
from app import create_app
from database import db
from werkzeug.security import generate_password_hash
from models import User


def init_db():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Create sample teacher and student
        teacher = User(name='Test Teacher', email='teacher@example.com', password_hash=generate_password_hash('password'), role='teacher')
        student = User(name='Test Student', email='student@example.com', password_hash=generate_password_hash('password'), role='student')
        db.session.add_all([teacher, student])
        db.session.commit()
        print('Initialized DB with sample users: teacher@example.com / student@example.com (password)')


if __name__ == '__main__':
    init_db()
