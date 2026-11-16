# Studio Flow — seven-table database plan (design stage)

The Django starter currently uses temporary sample data. These tables have **not yet** been created in Neon or Django. Create them in SQL first, then add matching unmanaged Django models (`managed = False`) following the course’s database-first approach.

| Table | Primary key | Important fields and relationships |
|---|---|---|
| `members` | `member_id` | `first_name`, `last_name`, `email` (UNIQUE), `phone` |
| `instructors` | `instructor_id` | `first_name`, `last_name`, `email`, `specialty` |
| `class_types` | `class_type_id` | `class_name`, `description`, `duration_minutes` (CHECK > 0), `difficulty_level`, `price` (CHECK >= 0) |
| `rooms` | `room_id` | `room_name` (UNIQUE), `max_capacity` (CHECK > 0) |
| `class_sessions` | `session_id` | `class_type_id` FK → `class_types`; `instructor_id` FK → `instructors`; `room_id` FK → `rooms`; `session_date`, `start_time`, `capacity` (CHECK > 0) |
| `reservations` | `reservation_id` | `member_id` FK → `members`; `session_id` FK → `class_sessions`; `booking_date`, `booking_status` |
| `payments` | `payment_id` | `reservation_id` FK → `reservations` (UNIQUE for at most one payment record per reservation); `amount` (CHECK >= 0), `payment_date`, `payment_method`, `payment_status` |

## Relationships

- One member may have many reservations; every reservation belongs to one member.
- One class session may have many reservations; every reservation belongs to one session.
- One class type, instructor, or room may be linked to many sessions; each session uses one of each.
- A reservation may have zero or one payment record; every payment is for exactly one reservation. Enforce this with `payments.reservation_id` as NOT NULL, UNIQUE and FOREIGN KEY.

## Rules to implement later

- Do not allow two active reservations for the same member and session.
- Do not book a full class. Derive availability from `class_sessions.capacity` minus its active reservations, rather than storing a potentially inconsistent `spots_remaining` field.
- When booking, atomically verify remaining capacity and insert the reservation in a database transaction. Handle concurrent bookings safely.
- Validate capacity against the room's max capacity.
- Payments are **recordkeeping only** (pending/paid/refunded); no credit-card processing or external payment gateway is needed.
- Use form validation for invalid entries, alongside SQL constraints.
- Seed realistic sample data, including at least about 30 reservations for your demo dashboard.

**Status:** Planning document, not an implemented database, ER diagram, or working payments feature. Align the final `schema.sql`, Django models, and ER diagram when you implement them.
