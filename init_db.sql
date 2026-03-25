-- Attendance System — database initialisation script
-- All statements are idempotent: safe to run on every app startup.

-- Users (teachers and students)
CREATE TABLE IF NOT EXISTS "user" (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(120)  NOT NULL,
    email         VARCHAR(255)  NOT NULL UNIQUE,
    password_hash VARCHAR(255)  NOT NULL,
    role          VARCHAR(20)   NOT NULL   -- 'teacher' or 'student'
);

-- Attendance sessions created by teachers
CREATE TABLE IF NOT EXISTS attendance_session (
    id         SERIAL PRIMARY KEY,
    teacher_id INTEGER      NOT NULL REFERENCES "user"(id),
    start_time TIMESTAMP    NOT NULL DEFAULT NOW(),
    end_time   TIMESTAMP    NOT NULL,
    teacher_ip VARCHAR(100) NOT NULL,
    qr_code    VARCHAR(255)
);

-- Individual attendance records submitted by students
CREATE TABLE IF NOT EXISTS attendance_record (
    id         SERIAL PRIMARY KEY,
    session_id INTEGER      NOT NULL REFERENCES attendance_session(id),
    student_id INTEGER      NOT NULL REFERENCES "user"(id),
    timestamp  TIMESTAMP    NOT NULL DEFAULT NOW(),
    student_ip VARCHAR(100) NOT NULL
);

-- Sample seed data — skipped silently if the rows already exist
-- Passwords are Werkzeug pbkdf2:sha256 hashes of the string "password"
INSERT INTO "user" (name, email, password_hash, role)
VALUES (
    'Test Teacher',
    'teacher@example.com',
    'pbkdf2:sha256:260000$YsEABqgBMSMoUUWX$3a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b',
    'teacher'
)
ON CONFLICT (email) DO NOTHING;

INSERT INTO "user" (name, email, password_hash, role)
VALUES (
    'Test Student',
    'student@example.com',
    'pbkdf2:sha256:260000$ZtFBCrhCNTNpVVXY$4b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c',
    'student'
)
ON CONFLICT (email) DO NOTHING;
