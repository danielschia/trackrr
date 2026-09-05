from flask import Flask, render_template
from flask_jwt_extended import JWTManager, get_jwt_identity, verify_jwt_in_request
from database.base import db
from model.user import User
from model.dashboard import Dashboard
from model.list import List
from model.task import Task
from dotenv import load_dotenv
import os
from pathlib import Path


load_dotenv(Path(__file__).resolve().parent / ".env")

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_COOKIE_CSRF_PROTECT"] = False

db.init_app(app)
jwt = JWTManager(app)

from routes.api.auth import auth_api_bp
from routes.api.dashboards import dashboards_api_bp
from routes.api.lists import lists_api_bp
from routes.web.auth_pages import auth_web_bp
from routes.web.dashboard_pages import dashboard_web_bp
from routes.web.list_pages import list_web_bp
from routes.web.task_pages import task_web_bp

app.register_blueprint(auth_api_bp, url_prefix="/api/auth")
app.register_blueprint(dashboards_api_bp, url_prefix="/api")
app.register_blueprint(lists_api_bp, url_prefix="/api")
app.register_blueprint(auth_web_bp)
app.register_blueprint(dashboard_web_bp)
app.register_blueprint(list_web_bp)
app.register_blueprint(task_web_bp)


@app.context_processor
def inject_auth_state():
    try:
        verify_jwt_in_request(optional=True)
        is_authenticated = get_jwt_identity() is not None
    except Exception:
        is_authenticated = False

    return {"is_authenticated": is_authenticated}

# Ensure tables exist when the app boots in local/dev environments.
with app.app_context():
    db.create_all()

@app.cli.command('db_create')
def db_create():
    db.create_all()
    print('Database created')


@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('Database dropped')


@app.cli.command('db_seed')
def db_seed():
    test_user = User(username='Stephen Hawking',
                        email='admin@admin.com',
                        password='admin')
    db.session.add(test_user)
    db.session.commit()
    print('Database seeded')

@app.route("/")
def home():
    return render_template("base.html")