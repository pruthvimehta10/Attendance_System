from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import qrcode
import io
import uuid
from fpdf import FPDF
import os
import smtplib
from email.message import EmailMessage
from database import db
from models import AttendanceSession, AttendanceRecord, User
# send_email import removed — outbound SMTP (Gmail) is blocked on Railway's network

teacher_bp = Blueprint('teacher', __name__, url_prefix='/teacher')


def teacher_required(fn):
    from functools import wraps

    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'teacher':
            flash('Access denied: teachers only.', 'danger')
            return redirect(url_for('auth.login'))
        return fn(*args, **kwargs)

    return wrapper


@teacher_bp.route('/dashboard')
@login_required
@teacher_required
def dashboard():
    # Show last active session if any
    now = datetime.utcnow()
    active = AttendanceSession.query.filter(AttendanceSession.teacher_id == current_user.id, AttendanceSession.end_time > now).order_by(AttendanceSession.start_time.desc()).first()
    remaining = None
    if active:
        remaining = (active.end_time - now).total_seconds()
    return render_template('teacher_dashboard.html', active_session=active, remaining=remaining)


@teacher_bp.route('/start-session', methods=['POST'])
@login_required
@teacher_required
def start_session():
    # fixed window (5 minutes) or configurable via form
    session_name = request.form.get('name', 'Unnamed Session').strip()
    if not session_name:
        session_name = 'Unnamed Session'
    minutes = int(request.form.get('minutes', 5))
    start = datetime.utcnow()
    end = start + timedelta(minutes=minutes)
    
    # Use actual network IP instead of localhost
    import socket
    teacher_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if teacher_ip:
        teacher_ip = teacher_ip.split(',')[0].strip()

    if teacher_ip == '127.0.0.1' or teacher_ip == 'localhost':
        # Get actual network IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        teacher_ip = s.getsockname()[0]
        s.close()
    
    session = AttendanceSession(
        teacher_id=current_user.id, 
        name=session_name,
        start_time=start, 
        end_time=end, 
        teacher_ip=teacher_ip
    )
    db.session.add(session)
    db.session.commit()
    flash(f'Attendance session "{session_name}" started for {minutes} minutes.', 'success')
    return redirect(url_for('teacher.dashboard'))


@teacher_bp.route('/attendance/<int:session_id>')
@login_required
@teacher_required
def view_attendance(session_id):
    session = AttendanceSession.query.get_or_404(session_id)
    if session.teacher_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('teacher.dashboard'))
    
    records = AttendanceRecord.query.filter_by(session_id=session_id).all()
    return render_template('attendance_view.html', session=session, records=records)


@teacher_bp.route('/recent-sessions')
@login_required
@teacher_required
def recent_sessions():
    """Get recent sessions for the current teacher (up to 5)"""
    sessions = AttendanceSession.query.filter_by(teacher_id=current_user.id)\
        .order_by(AttendanceSession.start_time.desc())\
        .limit(5)\
        .all()
    
    session_data = []
    for session in sessions:
        attendance_count = AttendanceRecord.query.filter_by(session_id=session.id).count()
        session_data.append({
            'id': session.id,
            'name': session.name or f'Session {session.id}',
            'start_time': session.start_time.isoformat(),
            'end_time': session.end_time.isoformat(),
            'attendance_count': attendance_count
        })
    
    return jsonify({'sessions': session_data})

@teacher_bp.route('/attendance/<int:session_id>/download', methods=['GET'])
@login_required
@teacher_required
def download_attendance(session_id):
    session = AttendanceSession.query.get_or_404(session_id)
    if session.teacher_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('teacher.dashboard'))
    
    records = AttendanceRecord.query.filter_by(session_id=session_id).all()
    
    # 1. Generate PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    
    # Title
    session_title = session.name or f'Session {session.id}'
    pdf.cell(0, 10, f'Attendance Report: {session_title}', ln=True, align='C')
    
    # Session Date and Time
    pdf.set_font('Arial', '', 12)
    session_start_ist = session.start_time + timedelta(hours=5, minutes=30)
    session_end_ist = session.end_time + timedelta(hours=5, minutes=30)
    date_str = session_start_ist.strftime("%Y-%m-%d")
    time_str = f"{session_start_ist.strftime('%H:%M:%S')} to {session_end_ist.strftime('%H:%M:%S')} IST"
    
    pdf.cell(0, 10, f'Session Date: {date_str}  |  Time: {time_str}', ln=True, align='C')
    
    pdf.ln(10)
    
    # Table Header
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(80, 10, 'Student Name', border=1)
    pdf.cell(110, 10, 'Email', border=1)
    pdf.ln()
    
    # Table Body
    pdf.set_font('Arial', '', 12)
    for record in records:
        pdf.cell(80, 10, str(record.student.name), border=1)
        pdf.cell(110, 10, str(record.student.email), border=1)
        pdf.ln()
    
    # Output to binary string
    pdf_output = pdf.output(dest='S').encode('latin-1')
    
    # Return directly as downloadable file
    return send_file(
        io.BytesIO(pdf_output),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'Attendance_{session.id}.pdf'
    )
