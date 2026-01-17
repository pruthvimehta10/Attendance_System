"""Quick script to add a single user to the database"""
from app import create_app
from database import db
from werkzeug.security import generate_password_hash
from models import User

def add_user(name, email, password, role='student'):
    """Add a user directly to database"""
    app = create_app()
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print(f'❌ User with email {email} already exists!')
            return False
        
        # Create new user
        password_hash = generate_password_hash(password)
        new_user = User(name=name, email=email, password_hash=password_hash, role=role)
        db.session.add(new_user)
        db.session.commit()
        print(f'✅ Successfully added {role}: {name} ({email})')
        return True

if __name__ == '__main__':
    print("Quick User Add - Flask Attendance System")
    print("=" * 40)
    
    # Get user input
    name = input("Enter full name: ").strip()
    email = input("Enter email: ").strip()
    password = input("Enter password: ").strip()
    role = input("Enter role (teacher/student) [default: student]: ").strip() or 'student'
    
    if not name or not email or not password:
        print("❌ Name, email, and password are required!")
    else:
        if role not in ['teacher', 'student']:
            print("❌ Invalid role! Must be 'teacher' or 'student'")
        else:
            success = add_user(name, email, password, role)
            if success:
                print(f"\n🎉 User added successfully!")
                print(f"📧 Login credentials: {email} / {password}")
            else:
                print(f"\n❌ Failed to add user")
