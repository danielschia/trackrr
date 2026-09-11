from flask import Blueprint, redirect, render_template, request, url_for
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import func

from database.base import db
from model.dashboard import Dashboard
from model.list import List

list_web_bp = Blueprint("web_list", __name__)


def reusable_request_data():
    current_user_id = int(get_jwt_identity())
    data = request.form or {}
    name = data.get("name")
    description = data.get("description")
    dashboard_id = data.get("dashboard_id")
    return current_user_id, name, description, dashboard_id


def parse_optional_int(value):
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


@list_web_bp.route("/lists", methods=["POST"])
@jwt_required()
def create_list():
    current_user_id, name_raw, description_raw, dashboard_id_raw = reusable_request_data()
    dashboard_id = parse_optional_int(dashboard_id_raw)
    if dashboard_id is None:
        return render_template("dashboards/index.html", error="Dashboard id is required"), 400

    dashboard = Dashboard.query.filter_by(id=dashboard_id, user_id=current_user_id).first()

    if not isinstance(name_raw, str):
        if dashboard is not None:
            return render_template("dashboards/detail.html", dashboard=dashboard, error="List name must be a string"), 400
        return render_template("dashboards/index.html", error="Dashboard not found"), 404

    name = name_raw.strip()

    if not name:
        if dashboard is not None:
            return render_template("dashboards/detail.html", dashboard=dashboard, error="List name is required"), 400
        return render_template("dashboards/index.html", error="Dashboard not found"), 404

    if description_raw is not None and not isinstance(description_raw, str):
        if dashboard is not None:
            return render_template("dashboards/detail.html", dashboard=dashboard, error="Description must be a string"), 400
        return render_template("dashboards/index.html", error="Dashboard not found"), 404

    if description_raw is None:
        description = ""
    else:
        description = description_raw

    if dashboard is None:
        return render_template("dashboards/detail.html", error="Dashboard not found"), 404

    last_position = db.session.query(func.max(List.position)).filter_by(dashboard_id=dashboard.id).scalar()
    next_position = (last_position or 0) + 1000

    new_list = List(
        name=name,
        description=description,
        user_id=current_user_id,
        dashboard_id=dashboard.id,
        position=next_position,
    )
    db.session.add(new_list)
    db.session.commit()

    return redirect(url_for("web_dashboard.dashboard_detail", dashboard_id=dashboard.id))

@list_web_bp.route("/lists/<int:list_id>/edit", methods=["POST"])
@jwt_required()
def edit_list(list_id):
    current_user_id, name_raw, description_raw, _dashboard_id = reusable_request_data()
    list_obj = List.query.filter_by(id=list_id, user_id=current_user_id).first()
    if list_obj is None:
        return render_template("dashboards/detail.html", error="List not found"), 404

    if not isinstance(name_raw, str):
        return render_template("dashboards/detail.html", dashboard=list_obj.dashboard, error="List name must be a string"), 400

    name = name_raw.strip()
    description = description_raw

    if not name:
        return render_template("dashboards/detail.html", dashboard=list_obj.dashboard, error="List name is required"), 400

    if description is not None and not isinstance(description, str):
        return render_template("dashboards/detail.html", dashboard=list_obj.dashboard, error="Description must be a string"), 400

    if description is None:
        description = ""

    list_obj.name = name
    list_obj.description = description
    db.session.commit()

    return redirect(url_for("web_dashboard.dashboard_detail", dashboard_id=list_obj.dashboard_id))

@list_web_bp.route("/lists/<int:list_id>/delete", methods=["POST"])
@jwt_required()
def delete_list(list_id):
    current_user_id = int(get_jwt_identity())
    list_obj = List.query.filter_by(id=list_id, user_id=current_user_id).first()
    if list_obj is None:
        return render_template("dashboards/detail.html", error="List not found"), 404

    db.session.delete(list_obj)
    db.session.commit()

    return redirect(url_for("web_dashboard.dashboard_detail", dashboard_id=list_obj.dashboard_id))