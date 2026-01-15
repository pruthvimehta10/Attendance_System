from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import qrcode
import io
import uuid
from database import db
from models import AttendanceSession, AttendanceRecord, User

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
    minutes = int(request.form.get('minutes', 5))
    start = datetime.utcnow()
    end = start + timedelta(minutes=minutes)
    teacher_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    # Generate unique QR code for this session
    qr_code_uuid = str(uuid.uuid4())
    
    session = AttendanceSession(
        teacher_id=current_user.id, 
        start_time=start, 
        end_time=end, 
        teacher_ip=teacher_ip,
        qr_code=qr_code_uuid
    )
    db.session.add(session)
    db.session.commit()
    flash(f'Attendance session started for {minutes} minutes.', 'success')
    return redirect(url_for('teacher.dashboard'))


@teacher_bp.route('/qr-code/<int:session_id>')
@login_required
@teacher_required
def generate_qr_code(session_id):
    session = AttendanceSession.query.get_or_404(session_id)
    if session.teacher_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('teacher.dashboard'))
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(session.qr_code)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to memory
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png')


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
