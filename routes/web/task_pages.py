from flask import Blueprint, redirect, render_template, request, url_for
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import func

from model.dashboard import Dashboard
from model.list import List
from model.task import Task
from database.base import db


task_web_bp = Blueprint("web_task", __name__)

@task_web_bp.route("/tasks", methods=["POST"])
@jwt_required()
def create_task():
    current_user_id = int(get_jwt_identity())
    title = (request.form.get("title") or "").strip()
    description = request.form.get("description")
    list_id = request.form.get("list_id")
    dashboard_id = request.form.get("dashboard_id")

    if list_id is not None:
        list_id = int(list_id)
    if dashboard_id is not None:
        dashboard_id = int(dashboard_id)

    dashboard = Dashboard.query.filter_by(id=dashboard_id, user_id=current_user_id).first() if dashboard_id else None

    if not title:
        if dashboard is not None:
            return render_template("dashboards/detail.html", dashboard=dashboard, error="Task title is required"), 400
        return render_template("dashboards/index.html", error="Dashboard not found"), 404

    if not isinstance(title, str):
        if dashboard is not None:
            return render_template("dashboards/detail.html", dashboard=dashboard, error="Task title must be a string"), 400
        return render_template("dashboards/index.html", error="Dashboard not found"), 404

    if description is not None and not isinstance(description, str):
        if dashboard is not None:
            return render_template("dashboards/detail.html", dashboard=dashboard, error="Description must be a string"), 400
        return render_template("dashboards/index.html", error="Dashboard not found"), 404

    if description is None:
        description = ""

    if dashboard is None:
        return render_template("dashboards/detail.html", error="Dashboard not found"), 404

    list_obj = List.query.filter_by(id=list_id, user_id=current_user_id, dashboard_id=dashboard.id).first() if list_id else None
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