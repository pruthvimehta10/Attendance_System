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
