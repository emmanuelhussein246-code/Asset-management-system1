# Swahilipot Hub — Asset Management System
### Rebuilt with HTML/CSS Frontend + Django Backend

**Mombasa, Kenya** · Phase 1 — Administration Department

---

## Tech Stack

| Layer      | Technology                              |
|------------|-----------------------------------------|
| Frontend   | **HTML5 + CSS3** (custom design system) |
| Backend    | **Django 5.0** (Python 3.12+)           |
| Database   | **SQLite** (dev) / PostgreSQL (prod)    |
| Auth       | Django built-in (`is_staff` guard)      |
| Fonts      | Syne · Space Mono · Outfit (Google)     |
| Static     | WhiteNoise                              |

---

## Frontend Architecture

The frontend is built as **pure HTML + CSS** — no JavaScript frameworks.

```
static/
└── css/
    └── main.css          ← Full design system (colors, layout, components)

assets_app/templates/assets_app/
├── base.html             ← Sidebar layout shell
├── login.html            ← Standalone login page
├── dashboard.html        ← Overview with stats & activity
├── asset_list.html       ← Asset registry table with filters
├── asset_form.html       ← Add / Edit asset
├── asset_detail.html     ← Full asset view + checkout history
├── asset_confirm_delete.html
├── checkout_form.html    ← Check out asset
├── checkin_confirm.html  ← Return asset
├── maintenance_list.html ← All maintenance tasks
├── maintenance_form.html ← Add maintenance task
├── audit_log.html        ← Full audit trail
├── staff_list.html       ← Staff directory
└── staff_form.html       ← Add staff member
```

---

## Quick Start

### 1. Extract & enter the folder
```bash
cd swahilipot_hub
```

### 2. Create virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment
The `.env` file is included with safe defaults for development.
For production, open `.env` and set a strong `SECRET_KEY`:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Run migrations
```bash
python manage.py migrate
```

### 6. Seed the database
```bash
python manage.py shell < seed.py
```
This creates 6 departments + the default superadmin account.

### 7. Start the development server
```bash
python manage.py runserver
```

Open: **http://127.0.0.1:8000**

---

## Default Login

| Field    | Value                  |
|----------|------------------------|
| Username | `admin`                |
| Password | `admin234`             |

> ⚠ Change this immediately after first login via **Staff → Edit account**

---

## Asset Label Format

```
SPH-[TYPE]-[NUMBER]
```

| Code    | Type        | Example         |
|---------|-------------|-----------------|
| `ELEC`  | Electronics | `SPH-ELEC-0001` |
| `FURN`  | Furniture   | `SPH-FURN-0012` |
| `EQUIP` | Equipment   | `SPH-EQUIP-0007`|
| `STAT`  | Stationery  | `SPH-STAT-0003` |
| `VEH`   | Vehicle     | `SPH-VEH-0001`  |
| `FAC`   | Facility    | `SPH-FAC-0002`  |

---

## Common Issues

| Problem                          | Fix                                              |
|----------------------------------|--------------------------------------------------|
| `no such table` error            | Run `python manage.py migrate`                   |
| `ModuleNotFoundError`            | Activate venv: `source venv/bin/activate`        |
| Port in use                      | `python manage.py runserver 8080`                |
| Static files not loading         | Ensure `DEBUG=True` in `.env` for development    |
| `SECRET_KEY` error               | Check `.env` file exists in project root         |

---

## Departments (pre-loaded)

1. Administration
2. Finance
3. Technology
4. Community Service
5. Communication & Media
6. Creative Arts & Heritage

---

*Built for Swahilipot Hub Foundation · Mombasa, Kenya*
