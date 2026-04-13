"""Utility functions for the Flask Attendance System"""
from datetime import datetime
import pytz

def get_ist_time():
    """Get current IST time"""
    utc_now = datetime.utcnow()
    ist = pytz.timezone('Asia/Kolkata')
    return utc_now.replace(tzinfo=pytz.UTC).astimezone(ist)

def format_ist_time(utc_datetime):
    """Format UTC datetime to IST time string"""
    if not utc_datetime:
        return "N/A"
    
    try:
        ist = pytz.timezone('Asia/Kolkata')
        utc = pytz.UTC
        utc_time = utc_datetime.replace(tzinfo=utc)
        ist_time = utc_time.astimezone(ist)
        return ist_time.strftime('%Y-%m-%d %H:%M:%S IST')
    except Exception as e:
        return str(utc_datetime) + " UTC"


def send_email(to, subject, body):
    """Send a plain-text email via the configured Flask-Mail instance.

    Args:
        to (str | list): Recipient address or list of addresses.
        subject (str): Email subject line.
        body (str): Plain-text email body.

    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """
    from app import mail
    from flask import current_app

    if isinstance(to, str):
        to = [to]

    try:
        msg = Message(subject=subject, recipients=to, body=body)
        mail.send(msg)
        current_app.logger.info(f'[send_email] Email sent to {to} — subject: {subject!r}')
        return True
    except Exception:
        import traceback as _tb
        current_app.logger.error(
            f'[send_email] Failed to send email to {to}:\n{_tb.format_exc()}'
        )
        return False
