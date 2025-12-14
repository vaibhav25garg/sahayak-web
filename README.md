# Sahayak Circle Website

A comprehensive Django-based service platform that connects skilled workers with customers who need reliable services. This platform facilitates worker registration, service requests, task management, and provides a complete admin dashboard for managing the entire ecosystem.

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation Guide](#installation-guide)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Admin Panel Access](#admin-panel-access)
- [Common Tasks](#common-tasks)
- [Troubleshooting](#troubleshooting)
- [Deployment](#deployment)

---

## 🎯 Project Overview

Sahayak Circle (ServiceConnect) is a service marketplace platform that enables:
- **Workers** to register and showcase their skills
- **Customers** to request services and connect with verified workers
- **Administrators** to manage workers, tasks, requirements, and track service delivery

The platform includes features like worker verification, task assignment, scheduling, payment tracking, ratings, and an IVR (Interactive Voice Response) system for call management.

---

## ✨ Features

### Public Features
- **Worker Registration**: Workers can register with personal details, Aadhar verification, and skill categories
- **Service Request Form**: Customers can submit service requirements
- **Public Website**: Home, About, and Contact pages

### Admin Dashboard
- **Worker Management**: View, verify, and manage worker profiles
- **Task Management**: Create, assign, and track tasks
- **Requirement Management**: Handle customer service requests
- **Category Management**: Organize services by categories
- **Location Management**: Manage service locations
- **Calling Summary**: Track IVR call summaries
- **Task Log History**: View complete task history

### API Features
- RESTful API endpoints for all resources
- Filtering and pagination support
- CORS enabled for cross-origin requests

---

## 🛠 Technology Stack

- **Backend Framework**: Django 5.2.7
- **API Framework**: Django REST Framework 3.16.1
- **Database**: SQLite (default) / PostgreSQL (production)
- **Image Processing**: Pillow 12.0.0
- **PDF Generation**: WeasyPrint 53.3
- **CORS Handling**: django-cors-headers 4.9.0
- **Filtering**: django-filter 25.2
- **Configuration**: python-decouple 3.8
- **Database Driver**: psycopg2-binary 2.9.11 (for PostgreSQL)

---

## 📦 Prerequisites

Before you begin, ensure you have the following installed on your system:

1. **Python 3.8+** (Python 3.12 recommended)
   - Check installation: `python --version` or `python3 --version`
   - Download from: https://www.python.org/downloads/

2. **pip** (Python package manager)
   - Usually comes with Python
   - Check installation: `pip --version` or `pip3 --version`

3. **Git** (optional, for version control)
   - Check installation: `git --version`
   - Download from: https://git-scm.com/downloads

4. **PostgreSQL** (optional, for production)
   - Only needed if you want to use PostgreSQL instead of SQLite
   - Download from: https://www.postgresql.org/download/

5. **Virtual Environment** (recommended)
   - `venv` comes with Python 3.3+

---

## 🚀 Installation Guide

Follow these step-by-step instructions to set up the project on your local machine.

### Step 1: Clone or Navigate to the Project

If you have the project in a Git repository:
```bash
git clone <repository-url>
cd sahayak-circle-website
```

If you already have the project folder:
```bash
cd sahayak-circle-website
```

### Step 2: Create a Virtual Environment

**On Windows:**
```bash
python -m venv venv
```

**On macOS/Linux:**
```bash
python3 -m venv venv
```

This creates a `venv` folder in your project directory.

### Step 3: Activate the Virtual Environment

**On Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**On macOS/Linux:**
```bash
source venv/bin/activate
```

You should see `(venv)` at the beginning of your command prompt, indicating the virtual environment is active.

### Step 4: Install Dependencies

With the virtual environment activated, install all required packages:

```bash
pip install -r requirements.txt
```

This will install all dependencies listed in `requirements.txt`. The installation may take a few minutes.

**Note**: If you encounter errors:
- On Windows, you might need to install Visual C++ Build Tools for some packages
- On Linux, you may need system packages like `libpq-dev` for PostgreSQL support

### Step 5: Verify Installation

Check if Django is installed correctly:
```bash
python manage.py --version
```

You should see the Django version (5.2.7).

---

## ⚙️ Configuration

### Environment Variables (Optional)

The project uses `python-decouple` for configuration management. You can create a `.env` file in the project root for sensitive settings:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=service_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
```

**Note**: Currently, the project uses hardcoded settings. To use environment variables, uncomment the relevant lines in `config/settings.py`.

### Settings Overview

Key settings in `config/settings.py`:
- **SECRET_KEY**: Django secret key (change in production!)
- **DEBUG**: Set to `False` in production
- **ALLOWED_HOSTS**: List of allowed hostnames
- **ADMIN_URL**: Custom admin panel URL (default: `secure-admin-panel-2024/`)
- **SESSION_COOKIE_AGE**: 24 hours (86400 seconds)

---

## 🗄 Database Setup

### Option 1: SQLite (Default - Recommended for Development)

SQLite is already configured and requires no additional setup. The database file (`db.sqlite3`) will be created automatically.

### Option 2: PostgreSQL (Recommended for Production)

1. **Install PostgreSQL** (if not already installed)

2. **Create a Database:**
   ```sql
   CREATE DATABASE service_db;
   CREATE USER your_username WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE service_db TO your_username;
   ```

3. **Update Settings:**
   - Uncomment the PostgreSQL database configuration in `config/settings.py`
   - Update the database credentials
   - Comment out the SQLite configuration

### Run Migrations

After configuring your database, run migrations to create all database tables:

```bash
python manage.py makemigrations
python manage.py migrate
```

This will create all necessary tables for:
- Workers
- Tasks
- Requirements
- Categories
- Locations
- IVR
- Calling Summary
- Django admin and authentication

### Create a Superuser

Create an admin user to access the Django admin panel:

```bash
python manage.py createsuperuser
```

Follow the prompts to enter:
- Username
- Email (optional)
- Password (twice)

**Important**: Remember these credentials for accessing the admin panel!

---

## 🏃 Running the Application

### Development Server

Start the Django development server:

```bash
python manage.py runserver
```

By default, the server runs on `http://127.0.0.1:8000/`

You can specify a different port:
```bash
python manage.py runserver 8080
```

### Access Points

Once the server is running, you can access:

1. **Public Homepage**: `http://127.0.0.1:8000/`
2. **Admin Dashboard**: `http://127.0.0.1:8000/dashboard/`
3. **Django Admin Panel**: `http://127.0.0.1:8000/secure-admin-panel-2024/`
4. **API Root**: `http://127.0.0.1:8000/api/`

### Stop the Server

Press `Ctrl + C` in the terminal to stop the development server.

---

## 📁 Project Structure

```
sahayak-circle-website/
│
├── apps/                          # Django applications
│   ├── workers/                   # Worker management app
│   │   ├── models.py             # Worker model
│   │   ├── views.py              # Worker views and ViewSets
│   │   ├── serializers.py        # API serializers
│   │   └── urls.py               # URL routing
│   │
│   ├── tasks/                     # Task management app
│   │   ├── models.py             # Task model
│   │   ├── views.py              # Task views
│   │   └── template_views.py     # Template-based views
│   │
│   ├── categories/                # Category management
│   ├── locations/                 # Location management
│   ├── requirements/              # Service requirements
│   ├── ivr/                       # IVR system
│   ├── calling_summary/           # Call summaries
│   ├── public/                    # Public-facing views
│   └── dashboard/                 # Admin dashboard
│
├── config/                        # Project configuration
│   ├── settings.py               # Django settings
│   ├── urls.py                   # Main URL configuration
│   ├── wsgi.py                   # WSGI configuration
│   └── asgi.py                   # ASGI configuration
│
├── templates/                     # HTML templates
│   ├── base.html                 # Base template
│   ├── public/                   # Public page templates
│   ├── dashboard/                # Dashboard templates
│   ├── tasks/                    # Task templates
│   └── workers/                  # Worker templates
│
├── media/                         # User-uploaded files
│   ├── workers/                  # Worker images (Aadhar, selfies)
│   └── tasks/                    # Task images
│
├── middleware/                    # Custom middleware
│   └── session_error_handler.py  # Session error handling
│
├── manage.py                     # Django management script
├── requirements.txt              # Python dependencies
├── db.sqlite3                    # SQLite database (created after migration)
└── README.md                     # This file
```

---

## 🔌 API Endpoints

The project provides RESTful API endpoints using Django REST Framework.

### Base URL
```
http://127.0.0.1:8000/api/
```

### Available Endpoints

1. **Workers**
   - `GET /api/workers/` - List all workers
   - `POST /api/workers/` - Create a new worker
   - `GET /api/workers/{id}/` - Get worker details
   - `PUT /api/workers/{id}/` - Update worker
   - `DELETE /api/workers/{id}/` - Delete worker

2. **Tasks**
   - `GET /api/tasks/` - List all tasks
   - `POST /api/tasks/` - Create a new task
   - `GET /api/tasks/{id}/` - Get task details
   - `PUT /api/tasks/{id}/` - Update task
   - `DELETE /api/tasks/{id}/` - Delete task

3. **Categories**
   - `GET /api/categories/` - List all categories
   - `POST /api/categories/` - Create a category
   - `GET /api/categories/{id}/` - Get category details

4. **Locations**
   - `GET /api/locations/` - List all locations
   - `POST /api/locations/` - Create a location

5. **Requirements**
   - `GET /api/requirements/` - List all requirements
   - `POST /api/requirements/` - Create a requirement

6. **IVR**
   - `GET /api/ivr/` - List IVR records
   - `POST /api/ivr/` - Create IVR record

7. **Calling Summary**
   - `GET /api/calling-summary/` - List call summaries
   - `POST /api/calling-summary/` - Create call summary

### API Features

- **Pagination**: Results are paginated (10 items per page by default)
- **Filtering**: Use query parameters to filter results
- **CORS**: Cross-origin requests are enabled

### Example API Usage

**List all workers:**
```bash
curl http://127.0.0.1:8000/api/workers/
```

**Create a worker (using JSON):**
```bash
curl -X POST http://127.0.0.1:8000/api/workers/ \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "phone": "1234567890", "primary_category": 1}'
```

---

## 🔐 Admin Panel Access

### Django Admin Panel

**URL**: `http://127.0.0.1:8000/secure-admin-panel-2024/`

**Access**: Requires superuser credentials created with `createsuperuser`

**Features**:
- Full CRUD operations on all models
- User management
- Advanced filtering and search
- Bulk actions

### Custom Dashboard

**URL**: `http://127.0.0.1:8000/dashboard/`

**Access**: Requires user authentication (login required)

**Features**:
- Worker management interface
- Task assignment and tracking
- Requirement management
- Worker verification
- Task log history
- PDF generation for worker details

**Login URL**: `http://127.0.0.1:8000/dashboard/login/`

---

## 📝 Common Tasks

### Creating Categories

Categories can be created through:
1. Django Admin Panel
2. API endpoint: `POST /api/categories/`
3. Custom dashboard (if implemented)

### Registering a Worker

1. **Via Public Form**: Navigate to `/join-as-worker/` and fill the registration form
2. **Via Admin**: Use Django admin or dashboard to create workers manually
3. **Via API**: POST request to `/api/workers/`

### Creating a Task

1. **Via Public Form**: Navigate to `/request-service/` and submit a requirement
2. **Via Dashboard**: Use the task management interface
3. **Via API**: POST request to `/api/tasks/`

### Assigning a Worker to a Task

1. Navigate to the task detail page in the dashboard
2. Use the "Assign Worker" functionality
3. Select a worker from the available list
4. Save the assignment

### Verifying a Worker

1. Go to the worker detail page in the dashboard
2. Review uploaded documents (Aadhar, selfie)
3. Update verification status:
   - `verified` - Worker is verified
   - `rejected` - Worker verification rejected
   - `under_review` - Under review
   - `pending` - Pending verification

### Running Database Migrations

When models are changed:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Collecting Static Files (for production)

```bash
python manage.py collectstatic
```

### Creating Database Backup (SQLite)

```bash
# On Windows
copy db.sqlite3 db_backup.sqlite3

# On macOS/Linux
cp db.sqlite3 db_backup.sqlite3
```

---

## 🔧 Troubleshooting

### Issue: ModuleNotFoundError

**Solution**: Ensure virtual environment is activated and dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: Database Migration Errors

**Solution**: 
1. Delete `db.sqlite3` (if using SQLite and in development)
2. Delete migration files (except `__init__.py`) in each app's `migrations/` folder
3. Run migrations again:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

### Issue: Port Already in Use

**Solution**: Use a different port:
```bash
python manage.py runserver 8080
```

### Issue: Static Files Not Loading

**Solution**: 
1. Ensure `DEBUG = True` in settings (for development)
2. Run `python manage.py collectstatic` (for production)
3. Check `STATIC_URL` and `STATIC_ROOT` settings

### Issue: Media Files Not Accessing

**Solution**: 
1. Ensure `MEDIA_URL` and `MEDIA_ROOT` are configured correctly
2. Check that the `media/` folder exists
3. Verify URL configuration includes media file serving in development

### Issue: Permission Denied (Windows)

**Solution**: Run PowerShell as Administrator or use Command Prompt

### Issue: PostgreSQL Connection Error

**Solution**:
1. Verify PostgreSQL is running
2. Check database credentials in settings
3. Ensure database exists
4. Verify user has proper permissions

---

## 🚢 Deployment

### Pre-Deployment Checklist

1. **Security Settings**:
   - Set `DEBUG = False`
   - Generate a new `SECRET_KEY` and store it securely
   - Update `ALLOWED_HOSTS` with your domain
   - Change `ADMIN_URL` to a secure, random path

2. **Database**:
   - Switch to PostgreSQL for production
   - Configure proper database credentials
   - Run migrations on production database

3. **Static Files**:
   - Run `python manage.py collectstatic`
   - Configure web server (Nginx/Apache) to serve static files

4. **Media Files**:
   - Configure proper media file storage (consider cloud storage for production)
   - Set up proper file permissions

5. **Environment Variables**:
   - Use `.env` file or environment variables for sensitive data
   - Never commit `.env` file to version control

### Deployment Options

1. **Heroku**
   - Add `Procfile` with: `web: gunicorn config.wsgi`
   - Configure environment variables
   - Use Heroku PostgreSQL addon

2. **AWS/DigitalOcean**
   - Use Gunicorn as WSGI server
   - Configure Nginx as reverse proxy
   - Set up SSL certificates

3. **Docker**
   - Create `Dockerfile` and `docker-compose.yml`
   - Use Docker for containerized deployment

### Production Settings Recommendations

```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
SECRET_KEY = os.environ.get('SECRET_KEY')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

---

## 📞 Support

For issues, questions, or contributions:
- Check the troubleshooting section above
- Review Django documentation: https://docs.djangoproject.com/
- Review Django REST Framework docs: https://www.django-rest-framework.org/

---

## 📄 License

[Specify your license here]

---

## 👥 Contributors

[Add contributor information here]

---

## 🔄 Version History

- **v1.0.0** - Initial release
  - Worker registration and management
  - Task assignment system
  - Admin dashboard
  - REST API endpoints
  - IVR integration
  - PDF generation

---

**Last Updated**: [Current Date]

**Maintained by**: [Your Name/Team]

