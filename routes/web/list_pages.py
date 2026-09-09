from flask import Blueprint, redirect, render_template, request, url_for
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import func

from model.dashboard import Dashboard
from model.list import List
from database.base import db


list_web_bp = Blueprint("web_list", __name__)

@list_web_bp.route("/lists", methods=["POST"])
@jwt_required()
def create_list():
    current_user_id = int(get_jwt_identity())
    name = (request.form.get("name") or "").strip()
    description = request.form.get("description")
    dashboard_id = request.form.get("dashboard_id")
    if dashboard_id is not None:
        dashboard_id = int(dashboard_id)
    dashboard = Dashboard.query.filter_by(id=dashboard_id, user_id=current_user_id).first() if dashboard_id else None

    if not name:
        if dashboard is not None:
            return render_template("dashboards/detail.html", dashboard=dashboard, error="List name is required"), 400
        return render_template("dashboards/index.html", error="Dashboard not found"), 404

    if not isinstance(name, str):
        if dashboard is not None:
            return render_template("dashboards/detail.html", dashboard=dashboard, error="List name must be a string"), 400
        return render_template("dashboards/index.html", error="Dashboard not found"), 404

    if description is not None and not isinstance(description, str):
        if dashboard is not None:
            return render_template("dashboards/detail.html", dashboard=dashboard, error="Description must be a string"), 400
        return render_template("dashboards/index.html", error="Dashboard not found"), 404

    if description is None:
        description = ""

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
    current_user_id = int(get_jwt_identity())
    list_obj = List.query.filter_by(id=list_id, user_id=current_user_id).first()
    if list_obj is None:
        return render_template("dashboards/detail.html", error="List not found"), 404

    name = (request.form.get("name") or "").strip()
    description = request.form.get("description")

    if not name:
        return render_template("dashboards/detail.html", dashboard=list_obj.dashboard, error="List name is required"), 400

    if not isinstance(name, str):
        return render_template("dashboards/detail.html", dashboard=list_obj.dashboard, error="List name must be a string"), 400

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