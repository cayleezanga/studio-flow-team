# Studio Flow — Pilates Class Booking and Management

**Live website:** https://studio-flow-team.vercel.app/  
**GitHub repository:** https://github.com/cayleezanga/studio-flow-team

## What the application does and who it is for

Studio Flow is a Django web application designed for a small Pilates studio. Visitors can view the class schedule, including class types, instructors, dates, times, rooms, and remaining capacity. Studio staff can sign in to manage reservations, record payment statuses, and view a dashboard summarizing activity.

The project demonstrates a working database-backed booking workflow, not an actual commercial service. **Bookings and member records are managed by staff in this version**; customers do not have their own self-service accounts. Payments are for **recordkeeping only**; the website does not charge cards, issue real refunds, or transmit money. Sample people and studio records are fictional.

## Main features

- **Public class schedule:** Reads class sessions, class types, instructor details, and rooms from the PostgreSQL database; calculates remaining spaces from currently booked reservations.
- **Reservation management:** Authorized staff can create, view, change the status of, and delete eligible reservations through the website. A reservation with an associated payment cannot be deleted; it can be cancelled instead.
- **Booking safeguards:** Prevents duplicate member/session reservations and bookings into full sessions. Cancelled reservations can be reactivated if a space is available.
- **Payment tracking:** Staff can add one payment record per eligible reservation and update its status through `Pending → Paid → Refunded`. These are administrative records, not real transactions.
- **Studio dashboard:** Shows reservation totals, members, upcoming sessions, popular class types, and payment totals grouped by status, using live database aggregation queries.
- **Staff authentication:** Reservation details, booking actions, payments, and the dashboard require a Django staff account.

## Technology stack

- Python and **Django 5.2**
- **PostgreSQL on Neon** for application data
- Django ORM and SQL for database access
- HTML, CSS, and Bootstrap for pages and styling
- **GitHub** for source control
- **Vercel** for public deployment

## How to run the application locally

**Prerequisites:** Python 3.12 or later, Git, and access to a Neon PostgreSQL database containing the Studio Flow tables.

1. Clone the repository and open the project folder:

   ```bash
   git clone https://github.com/cayleezanga/studio-flow-team.git
   cd studio-flow-team
   ```

2. Create a virtual environment and install dependencies:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

   On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1` instead.

3. Create a local `.env` file beside `manage.py`, using `.env.example` as a guide. Set:

   ```dotenv
   DATABASE_URL=postgresql://YOUR_NEON_CONNECTION_STRING
   SECRET_KEY=YOUR_OWN_RANDOM_SECRET_KEY
   ```

   Use the **full** PostgreSQL connection string provided by Neon in place of the example. Do not add a second `DATABASE_URL=` inside the value. Never commit `.env`, secrets, or passwords to GitHub.

4. If setting up a **new empty Neon project**, run `sql/schema.sql` first in the Neon SQL Editor, then `sql/studio_flow_seed_data.sql` to insert fictional demonstration records. **Do not rerun the schema on a database where the seven business tables already exist.** The business tables are database-first and are represented in Django by models with `managed = False`.

5. Apply Django's own migrations, check the project, and start the development server:

   ```bash
   python manage.py migrate
   python manage.py check
   python manage.py runserver
   ```

6. Open http://127.0.0.1:8000/ for the homepage and http://127.0.0.1:8000/schedule/ for the schedule. To use staff-only pages in a new development database, create a local staff account with `python manage.py createsuperuser` and then sign in at `/accounts/login/`.

Production deployment uses the `DATABASE_URL` and `SECRET_KEY` environment variables configured privately in Vercel. The repository does not contain those secret values.

## Database design

The seven related business tables are defined in [`sql/schema.sql`](sql/schema.sql):

| Table | Role |
| --- | --- |
| `members` | People associated with reservations |
| `instructors` | Pilates instructors and specialties |
| `class_types` | Class descriptions, durations, levels, and prices |
| `rooms` | Studio rooms and maximum capacities |
| `class_sessions` | Scheduled offerings linking a class type, instructor, and room |
| `reservations` | A member's booking for a specific class session and its status |
| `payments` | One optional payment record per reservation, with amount and status |

`class_sessions` has foreign keys to `class_types`, `instructors`, and `rooms`; `reservations` has foreign keys to `members` and `class_sessions`; `payments` references `reservations`. Primary keys, foreign keys, uniqueness rules, and `CHECK` constraints help protect the data. The final ER diagram should match this SQL schema.

Remaining spots are **calculated**, not stored: `class_sessions.capacity` minus reservations with `booking_status='Booked'`.

## Behind the product: database reads and writes

Django handles a request through **URL → view → model/ORM → template**, following the course architecture.

- `pages/urls.py` maps browser paths such as `/schedule/`, `/reservations/`, `/payments/`, and `/dashboard/` to views.
- `pages/views.py` reads scheduled classes using the ORM, including related class types, instructors, and rooms. It also handles the staff reservation pages.
- `operations/models.py` describes the seven existing Neon tables using unmanaged Django models (`managed = False`).
- `operations/booking.py` contains booking rules and functions that create, update, and delete eligible reservation records.
- `pages/payment_views.py` and `operations/payments.py` read and update administrative payment records.
- `pages/dashboard_views.py` uses Django ORM aggregation (`Count`, `Sum`, `values`, and `annotate`) to calculate dashboard statistics from multiple related tables.
- `templates/` renders the information as HTML pages.

### Business transaction and what it protects

`operations/booking.py` implements `create_booking()` with `@transaction.atomic`. When staff choose **Also create a Pending payment record** while booking, the operation:

1. Locks the selected class session using `select_for_update()` so competing bookings cannot bypass the capacity check.
2. Checks for an existing member reservation and verifies that the session has space.
3. Inserts a reservation (or reactivates a cancelled reservation).
4. Inserts a related Pending payment record, when the option is selected.

The reservation and payment writes happen **in one transaction**. If a required step fails, PostgreSQL rolls back the operation rather than saving a partial booking. Form validation and database constraints provide additional safeguards.

### Other business rules

- A member cannot have two separate reservation rows for the same session (`UNIQUE (member_id, session_id)`).
- A room and an instructor each cannot be double-scheduled at exactly the same date and start time, according to the SQL uniqueness constraints.
- Class durations and capacities must be positive, and payment amounts cannot be negative.
- Staff cannot delete a reservation that has a payment record.
- Payments follow the allowed status sequence `Pending → Paid → Refunded`.

## Suggested live demonstration

1. Open the public homepage and class schedule; point out the class, instructor, room, and available-spots data.
2. Sign in as a staff member and create a reservation for an available class, optionally with a Pending payment record.
3. Return to the schedule to demonstrate that its availability changed.
4. Open the reservation, update its status, and demonstrate cancellation or deletion of a reservation **without** a payment record.
5. Open Payments and update a Pending payment to Paid (no money is actually transferred).
6. Open the dashboard and explain how its class popularity and payment totals come from database queries.
7. Show `sql/schema.sql`, the final ER diagram, and `operations/booking.py` to explain keys, relationships, constraints, and the transaction.

For the instructor's live demo, provide test account credentials securely and **not** in this public README.

## How AI was used

ChatGPT was used to help modify Django/Python and HTML files from the course's Scarlet Roasters patterns and troubleshoot terminal and Vercel issues. The student is responsible for verifying the implementation and for understanding and explaining the final database and application code during the course Q&A. The project does not use an AI service at runtime.

## Team contribution

This is a **one-person team project**. The student selected the project concept, set up and configured the local Django environment, GitHub repository, Neon database and Vercel deployment, installed and tested the application features, verified database read/write behavior, and prepared the final demo and documentation with AI assistance as disclosed above.

