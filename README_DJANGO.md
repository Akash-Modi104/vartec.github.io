# VARTEC Django CMS

This branch contains the new database-driven VARTEC website. It preserves the existing English and Dutch content, images, hero slides and video while replacing the static Angular frontend with a fast server-rendered Django site and authenticated admin.

## Local setup

1. Create and activate a Python virtual environment.
2. Install dependencies: `pip install -r requirements.txt`.
3. Run migrations: `python manage.py migrate`.
4. Import existing content and media: `python manage.py seed_vartec --force`.
5. Create the first administrator: `python manage.py createsuperuser`.
6. Start the site: `python manage.py runserver`.
7. Open the public site at `http://127.0.0.1:8000/` and admin at `http://127.0.0.1:8000/admin/`.

Run the seed command once for a new database. Production uses `seed_vartec --if-empty`, which imports the starter content only when no CMS pages exist, so later admin edits and hidden content are never overwritten by a deployment.

## What administrators can control

- Every text key and its value for every active language.
- Languages, flags, ordering, default language and visibility.
- Homepage hero slides and reusable capability blocks.
- Services, projects, page sections, text items, images, layouts, colours, ordering and visibility.
- Existing asset library plus new image/video uploads.
- Global branding, contact details, SEO defaults and section feature toggles.
- Contact submissions, workflow status and internal notes.

A new language can be added without a code change: create the Language, then add translations to Text Keys. Missing translations safely fall back to the English default text.

## Production

GitHub Pages cannot execute Django. Use the included Dockerfile or Render blueprint with PostgreSQL. Configure the values shown in `.env.example`, run migrations, seed once, create a superuser, and use persistent/object storage for future admin uploads.

The seed command imports only services and claims already present on the existing VARTEC site. Run `--force` only during initial setup because it replaces sections on the seeded pages.
