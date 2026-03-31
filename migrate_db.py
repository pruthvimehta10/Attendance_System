from app import create_app
from database import db
from sqlalchemy import text

def migrate():
    app = create_app()
    with app.app_context():
        try:
            db.session.execute(text("ALTER TABLE attendance_session ADD COLUMN name VARCHAR(255);"))
            db.session.commit()
            print("Successfully added 'name' column to attendance_session!")
        except Exception as e:
            db.session.rollback()
            print(f"Migration error or column already exists: {e}")

if __name__ == '__main__':
    migrate()
