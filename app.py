import os
from pathlib import Path

from dotenv import load_dotenv
from flask import jsonify, make_response, redirect, render_template, request, url_for
from flask_bootstrap import Bootstrap5
from flask_jwt_extended import JWTManager, decode_token, unset_jwt_cookies
from flask_jwt_extended.exceptions import JWTExtendedException
from flask_openapi3.models.info import Info
from flask_openapi3.openapi import OpenAPI

from database.base import db
from model.user import User

load_dotenv(Path(__file__).resolve().parent / ".env")

info = Info(title="Trackr API",
    version="1.0.0",
    description="API for the Trackr application")
app = OpenAPI(__name__, info=info)
Bootstrap5(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_COOKIE_CSRF_PROTECT"] = False

db.init_app(app)
jwt = JWTManager(app)

PUBLIC_PATH_PREFIXES = (
    "/",
    "/openapi",
    "/docs",
    "/login",
    "/signup",
    "/static",
    "/bootstrap/static",
)


def is_api_request() -> bool:
    return request.path.startswith("/api")


def is_public_path() -> bool:
    return any(request.path == prefix or request.path.startswith(prefix + "/") for prefix in PUBLIC_PATH_PREFIXES)


def clear_auth_and_redirect(target: str):
    response = make_response(redirect(target))
    unset_jwt_cookies(response)
    return response


@jwt.expired_token_loader
def handle_expired_token(_jwt_header, _jwt_payload):
    if is_api_request():
        return jsonify({"error": "Token has expired"}), 401
    if is_public_path():
        return clear_auth_and_redirect(request.path)
    return clear_auth_and_redirect(url_for("web_auth.login_page"))


@jwt.invalid_token_loader
def handle_invalid_token(reason: str):
    if is_api_request():
        return jsonify({"error": "Invalid token", "details": reason}), 401
    if is_public_path():
        return clear_auth_and_redirect(request.path)
    return clear_auth_and_redirect(url_for("web_auth.login_page"))


@jwt.unauthorized_loader
def handle_unauthorized(reason: str):
    if is_api_request():
        return jsonify({"error": "Missing or invalid token", "details": reason}), 401
    if is_public_path():
        return clear_auth_and_redirect(request.path)
    return redirect(url_for("web_auth.login_page"))

from routes.api.auth import auth_api_bp
from routes.api.dashboards import dashboards_api_bp
from routes.api.lists import lists_api_bp
from routes.api.tasks import tasks_api_bp
from routes.web.auth_pages import auth_web_bp
from routes.web.dashboard_pages import dashboard_web_bp
from routes.web.list_pages import list_web_bp
from routes.web.task_pages import task_web_bp

app.register_api(auth_api_bp, url_prefix="/api/auth")
app.register_api(dashboards_api_bp, url_prefix="/api/dashboards")
app.register_api(lists_api_bp, url_prefix="/api/lists")
app.register_api(tasks_api_bp, url_prefix="/api")
app.register_blueprint(auth_web_bp)
app.register_blueprint(dashboard_web_bp)
app.register_blueprint(list_web_bp)
app.register_blueprint(task_web_bp)


@app.context_processor
def inject_auth_state():
    access_token = request.cookies.get("access_token_cookie")
    if not access_token:
        return {"is_authenticated": False}

    try:
        decode_token(access_token)
        is_authenticated = True
    except JWTExtendedException:
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
    return render_template("home/home.html")


@app.route("/docs")
@app.route("/openapi")
def openapi_docs_shortcut():
    return redirect("/openapi/swagger")