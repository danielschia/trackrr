from flask import (
    Blueprint,
    Response,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_jwt_extended import (
    create_access_token,
    set_access_cookies,
    unset_jwt_cookies,
)

from database.base import db
from model.user import User
from services.AuthService.build_user import build_new_user
from services.AuthService.validate_signup import validate_sign_up_input

auth_web_bp = Blueprint("web_auth", __name__)


@auth_web_bp.route("/signup", methods=["GET"])
def signup_page():
    return render_template("auth/signup.html")


@auth_web_bp.route("/signup", methods=["POST"])
def signup_submit():
    username = (request.form.get("username") or "").strip()
    email = (request.form.get("email") or "").strip()
    password = request.form.get("password") or ""

    validation_error = validate_sign_up_input(username, email, password)
    if validation_error:
        return validation_error

    new_user = build_new_user(username, email, password)
    
    db.session.add(new_user)
    db.session.commit()

    access_token = create_access_token(identity=str(new_user.id))
    response: Response = make_response(redirect(url_for("web_dashboard.dashboards_page")))
    set_access_cookies(response, access_token)
    return response


@auth_web_bp.route("/login", methods=["GET"])
def login_page():
    return render_template("auth/login.html")


@auth_web_bp.route("/login", methods=["POST"])
def login_submit():
    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""

    if not username or not password:
        return render_template("auth/login.html", error="Username and password are required"), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return render_template("auth/login.html", error="Invalid username or password"), 401

    access_token = create_access_token(identity=str(user.id))
    response: Response = make_response(redirect(url_for("web_dashboard.dashboards_page")))
    set_access_cookies(response, access_token)
    return response


@auth_web_bp.route("/logout")
def logout():
    response: Response = make_response(redirect(url_for("web_auth.login_page")))
    unset_jwt_cookies(response)
    return response
