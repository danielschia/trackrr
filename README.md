# Trackr

Trackr is an MVP developed for the 1st sprint of the Post-Graduation course in Software Engineering at PUC Rio.

The project is a Flask-based task management application with:
- Server-rendered web pages
- REST endpoints documented with OpenAPI
- JWT-based authentication
- SQLite persistence for local development

## 1. Prerequisites

Install the following tools in your environment:
- Python 3.10 or newer
- pip (usually included with Python)
- Git

To verify:

```bash
python --version
pip --version
git --version
```

## 2. Clone and enter the project

```bash
git clone <your-repository-url>
cd trackr
```

## 3. Create and activate a virtual environment

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

## 4. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Configure environment variables

Create a `.env` file in the project root with this content:

```env
SQLALCHEMY_DATABASE_URI=sqlite:///app.db
SQLALCHEMY_TRACK_MODIFICATIONS=False
JWT_SECRET_KEY=change-this-in-real-environments
```

Notes:
- For local MVP development, SQLite is enough.
- For shared/staging/production environments, use a stronger secret key and a managed database.

## 6. Start the application

Run the app with Flask:

```bash
flask --app app run --debug
```

The app will be available at:
- http://localhost:5000/

## 7. Database commands (optional)

This project creates tables automatically on startup in local development.

Optional Flask CLI commands:

```bash
flask --app app db_create
flask --app app db_drop
flask --app app db_seed
```

## 8. Troubleshooting

- If `flask` command is not found, ensure the virtual environment is activated.
- If dependency errors occur, recreate the virtual environment and reinstall:

```bash
deactivate  # if active
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows, replace activation/removal commands with their PowerShell equivalents.

## 9. Sprint context

This repository represents the MVP baseline delivered for Sprint 1 of the PUC Rio Software Engineering post-graduate program.
Future sprints may extend architecture, security hardening, testing depth, and deployment automation.
