from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from database import db
from models import AttendanceSession, AttendanceRecord

student_bp = Blueprint('student', __name__, url_prefix='/student')


def student_required(fn):
    from functools import wraps

    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'student':
            flash('Access denied: students only.', 'danger')
            return redirect(url_for('auth.login'))
        return fn(*args, **kwargs)

    return wrapper


@student_bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    # show all active sessions
    now = datetime.utcnow()
    active_sessions = AttendanceSession.query.filter(AttendanceSession.end_time > now).order_by(AttendanceSession.start_time.desc()).all()
    return render_template('student_dashboard.html', active_sessions=active_sessions)


@student_bp.route('/mark-attendance', methods=['POST'])
@login_required
@student_required
def mark_attendance():
    session_id = int(request.form.get('session_id'))
    session = AttendanceSession.query.get(session_id)
    now = datetime.utcnow()
    if not session:
        flash('Session not found.', 'danger')
        return redirect(url_for('student.dashboard'))

    # Check if session is still active
    if now > session.end_time:
        flash('Session is closed.', 'danger')
        return redirect(url_for('student.dashboard'))

    # Check if already marked
    existing = AttendanceRecord.query.filter_by(session_id=session.id, student_id=current_user.id).first()
    if existing:
        flash('Attendance already recorded.', 'info')
        return redirect(url_for('student.dashboard'))

    # Mark attendance
    student_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if student_ip:
        student_ip = student_ip.split(',')[0].strip()

    if student_ip != session.teacher_ip:
        flash('You must be on the same WiFi network as the teacher to mark attendance.', 'danger')
        return redirect(url_for('student.dashboard'))

    record = AttendanceRecord(session_id=session.id, student_id=current_user.id, timestamp=now, student_ip=student_ip)
    db.session.add(record)
    db.session.commit()
    flash('Attendance marked successfully.', 'success')
    return redirect(url_for('student.dashboard'))


