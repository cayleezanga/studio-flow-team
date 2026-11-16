# Studio Flow — Pilates Class Booking (Team Project)

A small Django prototype created as a clean starting point from the Scarlet Roasters course structure.

**Current state:** four navigable pages with *temporary sample class data*. There is no real booking form, database connection, or payment processing yet. This is a STARTER, not the final project.

## Get it running locally

1. Open the `studio-flow-starter` folder in VS Code (the folder containing `manage.py`).
2. In its terminal, run:

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac/Linux
   # Windows PowerShell: .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   python manage.py runserver
   ```

3. Visit http://127.0.0.1:8000/ , then `/schedule/`, `/reservations/`, `/about/`.

You may see a warning about unapplied Django migrations because our public sample pages do not need the database yet. We will handle the database in a later step.

## File map, like the Scarlet Roasters starter

- `django_project/urls.py` and `pages/urls.py`: URL routing
- `pages/views.py`: functions that select a template and sample data
- `pages/sample_data.py`: temporary list of sample Pilates sessions, like the course's earlier catalog list
- `templates/base.html`: shared navigation and styling
- `templates/pages/*.html`: the four public pages
- `static/css/studio.css`: studio-specific design
- `docs/database-plan.md`: the proposed **seven** related PostgreSQL tables, including payments

## Next steps (do these in order)

1. Register your solo team in Canvas and create a new personal GitHub repository (`studio-flow-team`) for this project. Invite instructor `mianyacd`.
2. Draw the seven-table ER diagram and write `schema.sql`, including constraints and foreign keys.
3. Create a **new** Neon PostgreSQL project (do not connect to or change your Scarlet Roasters database). Store its connection string in local `.env` only, never GitHub.
4. Add a Django `operations` app with `managed=False` models that match your SQL tables.
5. Replace temporary schedule data with database queries. Then add booking CRUD, input validation, a transaction, payment-status recordkeeping, and the dashboard.
6. Deploy on Vercel; configure `DATABASE_URL` and `SECRET_KEY` in Vercel environment variables, never in code; verify public URL and complete project deliverables.

### AI disclosure reminder

The course requires documenting how AI helped in the final README and being able to explain the code yourself in Q&A. We will write that section when the project is complete.
