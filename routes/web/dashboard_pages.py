from flask import Blueprint, render_template, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.orm import selectinload

from database.base import db
from model.dashboard import Dashboard

dashboard_web_bp = Blueprint("web_dashboard", __name__)


def reusable_request_data():
    current_user_id = int(get_jwt_identity())
    data = request.form or {}
    name = data.get("name")
    description = data.get("description")
    return current_user_id, name, description


@dashboard_web_bp.route("/dashboards-page", methods=["GET"])
@jwt_required()
def dashboards_page():
    current_user_id = int(get_jwt_identity())
    dashboards = Dashboard.query.filter_by(user_id=current_user_id).all()
    return render_template("dashboards/index.html", dashboards=dashboards)

@dashboard_web_bp.route("/dashboards", methods=["POST"])
@jwt_required()
def create_dashboard():
    current_user_id, name_raw, description_raw = reusable_request_data()

    if not isinstance(name_raw, str):
        return render_template("dashboards/index.html", error="Dashboard name must be a string"), 400

    name = name_raw.strip()
    description = description_raw

    if not name:
        return render_template("dashboards/index.html", error="Dashboard name is required"), 400

    if description is not None and not isinstance(description, str):
        return render_template("dashboards/index.html", error="Description must be a string"), 400

    if description is None:
        description = ""

    new_dashboard = Dashboard(name=name, description=description, user_id=current_user_id)
    db.session.add(new_dashboard)
    db.session.commit()

    return render_template("dashboards/index.html", dashboards=Dashboard.query.filter_by(user_id=current_user_id).all()), 201

@dashboard_web_bp.route("/dashboards/<int:dashboard_id>", methods=["GET"])
@jwt_required()
def dashboard_detail(dashboard_id):
    current_user_id = int(get_jwt_identity())
    dashboard = Dashboard.query.options(selectinload(Dashboard.lists)).filter_by(id=dashboard_id, user_id=current_user_id).first()

    if dashboard is None or dashboard.user_id != current_user_id:
        return render_template("dashboards/detail.html", error="Dashboard not found"), 404

    return render_template("dashboards/detail.html", dashboard=dashboard), 200

@dashboard_web_bp.route("/dashboards/<int:dashboard_id>/delete", methods=["POST"])
@jwt_required()
def delete_dashboard(dashboard_id):
    current_user_id = int(get_jwt_identity())
    dashboard = Dashboard.query.filter_by(id=dashboard_id, user_id=current_user_id).first()

    if dashboard is None or dashboard.user_id != current_user_id:
        return render_template("dashboards/index.html", error="Dashboard not found"), 404

    db.session.delete(dashboard)
    db.session.commit()

    return render_template("dashboards/index.html", dashboards=Dashboard.query.filter_by(user_id=current_user_id).all()), 200