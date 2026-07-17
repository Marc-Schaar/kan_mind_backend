# ![KanMind Logo](assets/icons/logo_icon.svg) KanMind Backend API

**RESTful API backend for KanMind — a collaborative Kanban board application.**
Built with Django and Django REST Framework, deployed to a production server with PostgreSQL, Gunicorn, and Nginx.

🔗 **Live API:** [kanmind.marc-schaar.com](https://kanmind.marc-schaar.com)
🌐 **Portfolio:** [marc-schaar.com](https://marc-schaar.com)

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.2-092E20?logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/Django%20REST%20Framework-3.16-A30000?logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-production-4169E1?logo=postgresql&logoColor=white)

---

## About the project

KanMind is a Trello-style Kanban board API built as a portfolio project to demonstrate a complete backend workflow: API design, authentication, authorization, testing, and a real production deployment (not just `runserver`).

The API handles boards, tasks, and comments with role-based permissions, so multiple users can collaborate on the same board while only board members can view or modify its content.

---

## Features

- User registration and token-based authentication
- CRUD operations on Boards, Tasks, and Comments
- Permissions ensuring only board members or owners can access and modify data
- Task assignment and review workflows
- Commenting on tasks
- API schema and documentation support with **drf-spectacular** (OpenAPI/Swagger)

---

## Tech Stack

| Layer          | Technology                              |
|----------------|------------------------------------------|
| Language       | Python 3.10+                             |
| Framework      | Django 5.2, Django REST Framework        |
| Auth           | DRF Token Authentication                 |
| Database       | PostgreSQL (production), SQLite (local)  |
| Deployment     | Gunicorn, Nginx, systemd, Let's Encrypt  |
| Config         | Environment-based via `python-dotenv`    |

---

## Usage

- API base URL (local): `http://127.0.0.1:8000/api/`
- API base URL (production): `https://kanmind.marc-schaar.com/api/`

### Authentication

- Token-based authentication is used.
- Obtain a token via the login endpoint.
- Include the token in the `Authorization` header as:
  `Authorization: Token <your_token>`

### Notes

- All endpoints (except registration and login) require authentication.
- Boards are collaborative; only owners or members can access or modify them.
- Tasks support assignment and review.
- Comments belong to tasks and require membership to create/delete.

---

## Local Development Setup

**Requirements:** Python 3.10+, pip, virtualenv

1. **Clone the repository**

    ```bash
    git clone https://github.com/Marc-Schaar/kan_mind_backend.git
    cd kan_mind_backend
    ```

2. **Create and activate a virtual environment**

    ```bash
    python3 -m venv env
    source env/bin/activate  # macOS/Linux
    # .\env\Scripts\activate # Windows
    ```

3. **Install dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4. **Create a `.env` file**

    Copy the example file and adjust it for local development (`DEBUG=True` uses SQLite, so the `DB_*` variables can stay as-is):

    ```bash
    cp .env.example .env
    ```

5. **Apply migrations**

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

6. **Create a superuser (optional, for admin access)**

    ```bash
    python manage.py createsuperuser
    ```

7. **Run the development server**

    ```bash
    python manage.py runserver
    ```

---

## Production Deployment

The live instance at **[kanmind.marc-schaar.com](https://kanmind.marc-schaar.com)** runs behind Gunicorn and Nginx, with PostgreSQL as the database and HTTPS via Let's Encrypt. Summary of the setup:

<details>
<summary><strong>Full deployment guide (click to expand)</strong></summary>

### 1. Environment variables

Configuration is read from a `.env` file in the project root (see `.env.example`). On the server, create `.env` with production values:

```env
DEBUG=False
SECRET_KEY=<generate a new, unique secret key>
ALLOWED_HOSTS=kanmind.marc-schaar.com,www.kanmind.marc-schaar.com
CSRF_TRUSTED_ORIGINS=https://kanmind.marc-schaar.com,https://www.kanmind.marc-schaar.com
CORS_ALLOWED_ORIGINS=https://kanmind.marc-schaar.com,https://www.kanmind.marc-schaar.com

DB_NAME=kanmind
DB_USER=kanmind
DB_PASSWORD=<strong password>
DB_HOST=localhost
DB_PORT=5432
```

Generate a fresh `SECRET_KEY`:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

When `DEBUG=False`, `core/settings.py` automatically:
- switches the database engine from SQLite to **PostgreSQL** (using the `DB_*` variables),
- enables production security settings (`SECURE_SSL_REDIRECT`, HSTS, secure cookies, `SECURE_PROXY_SSL_HEADER` for use behind a reverse proxy).

### 2. PostgreSQL setup

Create the database and user referenced in `.env`:

```bash
sudo -u postgres psql -c "CREATE DATABASE kanmind;"
sudo -u postgres psql -c "CREATE USER kanmind WITH PASSWORD '<strong password>';"
sudo -u postgres psql -c "ALTER ROLE kanmind SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE kanmind TO kanmind;"
```

### 3. Install & prepare the app

```bash
git clone https://github.com/Marc-Schaar/kan_mind_backend.git
cd kan_mind_backend
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt

# .env created as described above

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 4. Run with Gunicorn

```bash
gunicorn core.wsgi:application --bind 127.0.0.1:8000 --workers 3
```

For a persistent service, create a systemd unit, e.g. `/etc/systemd/system/kanmind.service`:

```ini
[Unit]
Description=KanMind Django app (Gunicorn)
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/kan_mind_backend
EnvironmentFile=/path/to/kan_mind_backend/.env
ExecStart=/path/to/kan_mind_backend/env/bin/gunicorn core.wsgi:application --bind 127.0.0.1:8000 --workers 3

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now kanmind
```

### 5. Nginx reverse proxy + HTTPS

Point Nginx at Gunicorn and serve static files from `STATIC_ROOT` (`staticfiles/`):

```nginx
server {
    listen 80;
    server_name kanmind.marc-schaar.com www.kanmind.marc-schaar.com;

    location /static/ {
        alias /path/to/kan_mind_backend/staticfiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Then obtain a TLS certificate (required, since `SECURE_SSL_REDIRECT` forces HTTPS in production):

```bash
sudo certbot --nginx -d kanmind.marc-schaar.com -d www.kanmind.marc-schaar.com
```

### 6. Deploying updates

```bash
git pull
source env/bin/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart kanmind
```

</details>

---

## Author

**Marc Schaar**
🌐 [marc-schaar.com](https://marc-schaar.com)
