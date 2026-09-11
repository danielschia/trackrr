from flask import Blueprint, redirect, render_template, request, url_for
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import func

from database.base import db
from model.dashboard import Dashboard
from model.list import List
from model.task import Task

task_web_bp = Blueprint("web_task", __name__)


def reusable_request_data():
    current_user_id = int(get_jwt_identity())
    data = request.form or {}
    list_id = data.get("list_id")
    title = data.get("title")
    description = data.get("description")
    dashboard_id = data.get("dashboard_id")
    return current_user_id, list_id, title, description, dashboard_id


def parse_optional_int(value):
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None

@task_web_bp.route("/tasks", methods=["POST"])
@jwt_required()
def create_task():
    current_user_id, list_id_raw, title_raw, description_raw, dashboard_id_raw = reusable_request_data()
    dashboard_id = parse_optional_int(dashboard_id_raw)
    list_id = parse_optional_int(list_id_raw)

    if dashboard_id is None:
        return render_template("dashboards/index.html", error="Dashboard id is required"), 400

    if list_id is None:
        dashboard = Dashboard.query.filter_by(id=dashboard_id, user_id=current_user_id).first()
        if dashboard is not None:
            return render_template("dashboards/detail.html", dashboard=dashboard, error="List id is required"), 400
        return render_template("dashboards/index.html", error="Dashboard not found"), 404

    if not isinstance(title_raw, str):
        dashboard = Dashboard.query.filter_by(id=dashboard_id, user_id=current_user_id).first()
        if dashboard is not None:
            return render_template("dashboards/detail.html", dashboard=dashboard, error="Task title must be a string"), 400
        return render_template("dashboards/index.html", error="Dashboard not found"), 404

    title = title_raw.strip()

    dashboard = Dashboard.query.filter_by(id=dashboard_id, user_id=current_user_id).first()

    if not title:
        if dashboard is not None:
            return render_template("dashboards/detail.html", dashboard=dashboard, error="Task title is required"), 400
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

    list_obj = List.query.filter_by(id=list_id, user_id=current_user_id, dashboard_id=dashboard.id).first()
    if list_obj is None:
        return render_template("dashboards/detail.html", dashboard=dashboard, error="List not found"), 404

    last_position = db.session.query(func.max(Task.position)).filter_by(list_id=list_obj.id).scalar()
    next_position = (last_position or 0) + 1000

    new_task = Task(
        title=title,
        description=description,
        user_id=current_user_id,
        dashboard_id=dashboard.id,
        list_id=list_obj.id,
        position=next_position,
    )
    db.session.add(new_task)
    db.session.commit()

    return redirect(url_for("web_dashboard.dashboard_detail", dashboard_id=dashboard.id))

@task_web_bp.route("/tasks/<int:task_id>/delete", methods=["POST"])
@jwt_required()
def delete_task(task_id):
    current_user_id = int(get_jwt_identity())
    task_obj = Task.query.filter_by(id=task_id, user_id=current_user_id).first()
    if task_obj is None:
        return render_template("dashboards/detail.html", error="Task not found"), 404

    db.session.delete(task_obj)
    db.session.commit()

    return redirect(url_for("web_dashboard.dashboard_detail", dashboard_id=task_obj.dashboard_id))

@task_web_bp.route("/tasks/<int:task_id>/edit", methods=["POST"])
@jwt_required()
def edit_task(task_id):
    current_user_id, list_id_raw, title_raw, description_raw, _dashboard_id = reusable_request_data()
    task_obj = Task.query.filter_by(id=task_id, user_id=current_user_id).first()
    if task_obj is None:
        return render_template("dashboards/detail.html", error="Task not found"), 404

    if not isinstance(title_raw, str):
        return render_template("dashboards/detail.html", dashboard=task_obj.dashboard, error="Task title must be a string"), 400

    title = title_raw.strip()
    description = description_raw

    if not title:
        return render_template("dashboards/detail.html", dashboard=task_obj.dashboard, error="Task title is required"), 400

    if description is not None and not isinstance(description, str):
        return render_template("dashboards/detail.html", dashboard=task_obj.dashboard, error="Description must be a string"), 400

    if description is None:
        description = ""

    list_id = parse_optional_int(list_id_raw)
    if list_id_raw not in (None, "") and list_id is None:
        return render_template("dashboards/detail.html", dashboard=task_obj.dashboard, error="List id must be an integer"), 400

    if list_id is not None:
        list_obj = List.query.filter_by(id=list_id, user_id=current_user_id, dashboard_id=task_obj.dashboard_id).first()
        if list_obj is None:
            return render_template("dashboards/detail.html", dashboard=task_obj.dashboard, error="List not found"), 404
        if list_obj.dashboard_id != task_obj.dashboard_id:
            return render_template("dashboards/detail.html", dashboard=task_obj.dashboard, error="List does not belong to the same dashboard as the task"), 400
        task_obj.list_id = list_obj.id

    task_obj.title = title
    task_obj.description = description
    db.session.commit()

    return redirect(url_for("web_dashboard.dashboard_detail", dashboard_id=task_obj.dashboard_id))