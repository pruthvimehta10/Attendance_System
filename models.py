from datetime import datetime
from database import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'teacher' or 'student'

    def __repr__(self):
        return f'<User {self.email}>'


class AttendanceSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(255), nullable=True)  # Name of the class/attendance
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=False)
    teacher_ip = db.Column(db.String(100), nullable=False)
    qr_code = db.Column(db.String(255), nullable=True)  # Unique QR code for this session

    teacher = db.relationship('User', backref='sessions')

    def __repr__(self):
        return f'<AttendanceSession {self.id} by {self.teacher_id}>'


class AttendanceRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('attendance_session.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    student_ip = db.Column(db.String(100), nullable=False)

    session = db.relationship('AttendanceSession', backref='records')
    student = db.relationship('User')

    def __repr__(self):
        return f'<AttendanceRecord session={self.session_id} student={self.student_id}>'
