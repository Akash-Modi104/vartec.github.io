# VARTEC Hostinger Deployment Guide

This guide is the repeatable deployment process for the VARTEC Django website and Angular CMS on the existing Hostinger VPS. It updates only the isolated `vartec-cms` service.

## Deployment locations

- Git branch: `codex/django-redesign`
- Server repository: `/opt/vartec-cms/repo`
- Python environment: `/opt/vartec-cms/venv`
- Production environment file: `/opt/vartec-cms/vartec.env`
- Service: `vartec-cms.service`
- Public website: `https://vartec.187-127-73-203.sslip.io/`
- Angular CMS: `https://vartec.187-127-73-203.sslip.io/admin/`
- Django security fallback: `https://vartec.187-127-73-203.sslip.io/django-admin/`

## 1. Prepare and test locally

Run these commands from the project directory:

```bash
npm run build:admin
.venv/bin/python manage.py check
.venv/bin/python manage.py test
DJANGO_DEBUG=false \
DJANGO_ALLOWED_HOSTS=localhost \
DJANGO_SECRET_KEY=build-verification-only \
.venv/bin/python manage.py collectstatic --noinput
git diff --check
```

Commit both the Angular source in `admin-src/` and its production output in `static/cms/`:

```bash
git add -A
git commit -m "Describe the website update"
git push origin codex/django-redesign
```

## 2. Open the Hostinger console

In Hostinger, open **VPS → Overview → Web console**.

Check the current deployment before changing anything:

```bash
sudo -u vartec git -C /opt/vartec-cms/repo status --short
sudo -u vartec git -C /opt/vartec-cms/repo branch --show-current
sudo -u vartec git -C /opt/vartec-cms/repo rev-parse --short HEAD
```

The status command must be empty. Stop and investigate if it shows server-side changes.

## 3. Pull and prepare the release

```bash
sudo -u vartec git -C /opt/vartec-cms/repo fetch origin
sudo -u vartec git -C /opt/vartec-cms/repo switch codex/django-redesign
sudo -u vartec git -C /opt/vartec-cms/repo pull --ff-only origin codex/django-redesign
```

Install dependencies, apply safe database migrations, validate Django and collect production assets:

```bash
sudo -u vartec bash -lc '
set -a
source /opt/vartec-cms/vartec.env
set +a
cd /opt/vartec-cms/repo
/opt/vartec-cms/venv/bin/pip install -r requirements.txt
/opt/vartec-cms/venv/bin/python manage.py migrate --noinput
/opt/vartec-cms/venv/bin/python manage.py check
/opt/vartec-cms/venv/bin/python manage.py collectstatic --noinput
'
```

Node.js is not required on the VPS because the tested Angular build is committed in `static/cms/`.

## 4. Restart only VARTEC

```bash
sudo systemctl restart vartec-cms.service
sudo systemctl is-active vartec-cms.service
sudo systemctl is-active nginx
```

Both services must report `active`.

## 5. Verify the release

```bash
curl -I https://vartec.187-127-73-203.sslip.io/
curl -I https://vartec.187-127-73-203.sslip.io/admin/
curl -I https://vartec.187-127-73-203.sslip.io/cms-api/session/
```

Open the public website and CMS in a browser. Confirm that images load, the CMS login works, and an existing content item can be opened without saving changes.

Check that the other VPS applications remain active:

```bash
sudo systemctl is-active job-dashboard supervisor ollama nginx
sudo ss -ltnp | grep -E ':5001|:8010|:8080|:8090'
```

## Troubleshooting

View only the VARTEC service logs:

```bash
sudo journalctl -u vartec-cms.service -n 100 --no-pager
```

If preparation fails, do not restart the service. Correct the problem, run the preparation commands again, and restart only after `manage.py check` succeeds.

Never edit `/opt/vartec-cms/vartec.env` during a normal code deployment, and never restart unrelated applications.
