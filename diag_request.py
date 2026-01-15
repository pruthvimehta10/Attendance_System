from app import create_app, db
from models import User, AttendanceSession
import traceback


def print_preview(resp):
    print('STATUS:', resp.status_code)
    data = resp.get_data(as_text=True)
    print('BODY PREVIEW:\n', data[:2000])


app = create_app()

with app.app_context():
    with app.test_client() as c:
        try:
            print('\nGET /login')
            resp = c.get('/login')
            print_preview(resp)

            # Login as teacher
            print('\nPOST /login as teacher')
            resp = c.post('/login', data={'email': 'teacher@example.com', 'password': 'password'}, follow_redirects=True)
            print_preview(resp)

            # Start a session as teacher
            print('\nPOST /teacher/start-session')
            resp = c.post('/teacher/start-session', data={'minutes': '5'}, follow_redirects=True)
            print_preview(resp)

            # Find latest session id
            session = AttendanceSession.query.order_by(AttendanceSession.id.desc()).first()
            sid = session.id if session else None
            print('\nLatest session id:', sid)

            # Logout
            print('\nGET /logout')
            resp = c.get('/logout', follow_redirects=True)
            print_preview(resp)

            # Login as student
            print('\nPOST /login as student')
            resp = c.post('/login', data={'email': 'student@example.com', 'password': 'password'}, follow_redirects=True)
            print_preview(resp)

            # Attempt to mark attendance
            if sid:
                print('\nPOST /student/mark-attendance')
                resp = c.post('/student/mark-attendance', data={'session_id': str(sid)}, follow_redirects=True)
                print_preview(resp)
            else:
                print('No session to mark attendance for')

        except Exception:
            print('EXCEPTION during diagnostic run')
            traceback.print_exc()
