-- Studio Flow: sample data for the seven-table Pilates database
-- Run in the Neon SQL Editor for the STUDIO-FLOW project (NOT Scarlet Roasters).
-- Prerequisite: sql/schema.sql has already created all seven tables.
-- Safe to rerun: duplicate master records, sessions, reservations, and payments are skipped.
-- No real customer information or credit-card transactions are used.

BEGIN;

-- 1. MASTER DATA: members, instructors, class types, and rooms
INSERT INTO members (first_name, last_name, email, phone) VALUES
  ('Ava', 'Brooks', 'ava.brooks@example.com', '555-0101'),
  ('Mia', 'Patel', 'mia.patel@example.com', '555-0102'),
  ('Chloe', 'Rivera', 'chloe.rivera@example.com', '555-0103'),
  ('Grace', 'Kim', 'grace.kim@example.com', '555-0104'),
  ('Isabella', 'Reed', 'isabella.reed@example.com', '555-0105'),
  ('Sophie', 'Bennett', 'sophie.bennett@example.com', '555-0106'),
  ('Lily', 'Carter', 'lily.carter@example.com', '555-0107'),
  ('Ella', 'Morgan', 'ella.morgan@example.com', '555-0108'),
  ('Harper', 'Nguyen', 'harper.nguyen@example.com', '555-0109'),
  ('Nora', 'Davis', 'nora.davis@example.com', '555-0110'),
  ('Zoe', 'Campbell', 'zoe.campbell@example.com', '555-0111'),
  ('Olivia', 'Parker', 'olivia.parker@example.com', '555-0112')
ON CONFLICT (email) DO NOTHING;

INSERT INTO instructors (first_name, last_name, email, specialty) VALUES
  ('Emma', 'Lee', 'emma.lee@example.com', 'Beginner Reformer'),
  ('Olivia', 'Stone', 'olivia.stone@example.com', 'Pilates Sculpt'),
  ('Sofia', 'Martinez', 'sofia.martinez@example.com', 'Mat Pilates'),
  ('Liam', 'Brooks', 'liam.brooks@example.com', 'Reformer Flow')
ON CONFLICT (email) DO NOTHING;

INSERT INTO class_types (class_name, description, duration_minutes, difficulty_level, price) VALUES
  ('Beginner Reformer', 'Introduction to reformer Pilates and fundamental movements.', 50, 'Beginner', 28.00),
  ('Pilates Sculpt', 'Strength and conditioning using Pilates-based movement.', 45, 'Intermediate', 30.00),
  ('Mat Pilates', 'Core-focused Pilates exercises on a mat.', 45, 'Beginner', 20.00),
  ('Reformer Flow', 'A continuous reformer sequence for experienced participants.', 50, 'Intermediate', 32.00),
  ('Stretch & Restore', 'Gentle mobility, stretching, and recovery.', 40, 'Beginner', 18.00)
ON CONFLICT (class_name) DO NOTHING;

INSERT INTO rooms (room_name, max_capacity) VALUES
  ('Reformer Studio A', 8),
  ('Reformer Studio B', 10),
  ('Mat Studio', 12)
ON CONFLICT (room_name) DO NOTHING;

-- 2. SESSIONS: scheduled instances of class types, with instructor and room
WITH planned (class_name, instructor_email, room_name, class_day, class_time, capacity) AS (
  VALUES
    ('Beginner Reformer','emma.lee@example.com','Reformer Studio A','2026-12-10','09:00',8),
    ('Mat Pilates','sofia.martinez@example.com','Mat Studio','2026-12-10','11:00',12),
    ('Pilates Sculpt','olivia.stone@example.com','Reformer Studio B','2026-12-10','18:00',10),
    ('Beginner Reformer','emma.lee@example.com','Reformer Studio A','2026-12-11','09:00',8),
    ('Reformer Flow','liam.brooks@example.com','Reformer Studio B','2026-12-11','17:30',10),
    ('Pilates Sculpt','olivia.stone@example.com','Reformer Studio B','2026-12-12','09:00',10),
    ('Mat Pilates','sofia.martinez@example.com','Mat Studio','2026-12-12','11:30',12),
    ('Beginner Reformer','emma.lee@example.com','Reformer Studio A','2026-12-14','09:00',8),
    ('Reformer Flow','liam.brooks@example.com','Reformer Studio B','2026-12-14','18:00',10),
    ('Mat Pilates','sofia.martinez@example.com','Mat Studio','2026-12-15','11:00',12),
    ('Pilates Sculpt','olivia.stone@example.com','Reformer Studio B','2026-12-15','18:00',10),
    ('Beginner Reformer','emma.lee@example.com','Reformer Studio A','2026-12-16','09:00',8),
    ('Reformer Flow','liam.brooks@example.com','Reformer Studio B','2026-12-16','18:00',10),
    ('Stretch & Restore','sofia.martinez@example.com','Mat Studio','2026-12-17','09:00',12),
    ('Pilates Sculpt','olivia.stone@example.com','Reformer Studio B','2026-12-17','18:00',10)
)
INSERT INTO class_sessions (class_type_id, instructor_id, room_id, session_date, start_time, capacity)
SELECT ct.class_type_id, i.instructor_id, rm.room_id,
       p.class_day::date, p.class_time::time, p.capacity
FROM planned p
JOIN class_types ct ON ct.class_name = p.class_name
JOIN instructors i ON i.email = p.instructor_email
JOIN rooms rm ON rm.room_name = p.room_name
ON CONFLICT DO NOTHING;

-- 3. RESERVATIONS: three sample bookings per studio session (45 total).
-- ROW_NUMBER chooses a reproducible rotation of sample members.
WITH sample_members AS (
  SELECT member_id, ROW_NUMBER() OVER (ORDER BY email) AS member_number
  FROM members WHERE email IN (
    'ava.brooks@example.com', 'mia.patel@example.com', 'chloe.rivera@example.com',
    'grace.kim@example.com', 'isabella.reed@example.com', 'sophie.bennett@example.com',
    'lily.carter@example.com', 'ella.morgan@example.com', 'harper.nguyen@example.com',
    'nora.davis@example.com', 'zoe.campbell@example.com', 'olivia.parker@example.com'
  )
),
sample_sessions AS (
  SELECT session_id, ROW_NUMBER() OVER (ORDER BY session_date, start_time, session_id) AS session_number
  FROM class_sessions
  WHERE session_date BETWEEN DATE '2026-12-10' AND DATE '2026-12-17'
),
bookings AS (
  SELECT m.member_id, s.session_id,
         CASE WHEN (s.session_number % 7 = 0 AND slot.slot_number = 3)
              THEN 'Cancelled' ELSE 'Booked' END AS booking_status
  FROM sample_sessions s
  CROSS JOIN generate_series(1, 3) AS slot(slot_number)
  JOIN sample_members m ON m.member_number =
       (((s.session_number - 1) * 3 + slot.slot_number - 1) % 12) + 1
)
INSERT INTO reservations (member_id, session_id, booking_date, booking_status)
SELECT member_id, session_id, CURRENT_DATE, booking_status
FROM bookings
ON CONFLICT (member_id, session_id) DO NOTHING;

-- 4. PAYMENT RECORDS: only statuses, never real payment processing.
-- First 25 bookings: paid; next five: pending (30 payment records total).
WITH eligible AS (
  SELECT r.reservation_id, ct.price,
         ROW_NUMBER() OVER (ORDER BY r.reservation_id) AS payment_number
  FROM reservations r
  JOIN class_sessions s ON s.session_id = r.session_id
  JOIN class_types ct ON ct.class_type_id = s.class_type_id
  WHERE r.booking_status = 'Booked'
    AND s.session_date BETWEEN DATE '2026-12-10' AND DATE '2026-12-17'
)
INSERT INTO payments (reservation_id, amount, payment_date, payment_method, payment_status)
SELECT reservation_id, price,
       CASE WHEN payment_number <= 25 THEN CURRENT_DATE ELSE NULL END,
       CASE WHEN payment_number <= 25 THEN 'Card' ELSE NULL END,
       CASE WHEN payment_number <= 25 THEN 'Paid' ELSE 'Pending' END
FROM eligible
WHERE payment_number <= 30
ON CONFLICT (reservation_id) DO NOTHING;

COMMIT;

-- 5. VERIFICATION: expected counts on a brand-new empty Studio Flow schema:
-- members 12; instructors 4; class_types 5; rooms 3;
-- class_sessions 15; reservations 45; payments 30.
SELECT 'members' AS table_name, COUNT(*) AS row_count FROM members
UNION ALL SELECT 'instructors', COUNT(*) FROM instructors
UNION ALL SELECT 'class_types', COUNT(*) FROM class_types
UNION ALL SELECT 'rooms', COUNT(*) FROM rooms
UNION ALL SELECT 'class_sessions', COUNT(*) FROM class_sessions
UNION ALL SELECT 'reservations', COUNT(*) FROM reservations
UNION ALL SELECT 'payments', COUNT(*) FROM payments
ORDER BY table_name;

-- Optional example: join four tables to display scheduled classes.
SELECT s.session_date, s.start_time, ct.class_name,
       i.first_name || ' ' || i.last_name AS instructor,
       rm.room_name, s.capacity
FROM class_sessions s
JOIN class_types ct ON ct.class_type_id = s.class_type_id
JOIN instructors i ON i.instructor_id = s.instructor_id
JOIN rooms rm ON rm.room_id = s.room_id
ORDER BY s.session_date, s.start_time;
