from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from database.base import db
from model.dashboard import Dashboard
from model.task import Task


tasks_api_bp = Blueprint("tasks_api", __name__)


@tasks_api_bp.route("/tasks", methods=["POST"])
@jwt_required()
def create_task():
    current_user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    title = (data.get("title") or "").strip()
    description = data.get("description") or ""
    dashboard_id = data.get("dashboard_id")
    list_id = data.get("list_id")

    if not title:
        return jsonify({"error": "Task title is required"}), 400

    if not isinstance(title, str):
        return jsonify({"error": "Task title must be a string"}), 400

    if description is not None and not isinstance(description, str):
        return jsonify({"error": "Description must be a string"}), 400

    if not dashboard_id:
        return jsonify({"error": "Dashboard id is required"}), 400

    if not list_id:
        return jsonify({"error": "List id is required"}), 400

    dashboard = Dashboard.query.filter_by(id=dashboard_id, user_id=current_user_id).first()
    if dashboard is None:
        return jsonify({"error": "Dashboard not found"}), 404

    new_task = Task(
        title=title,
        description=description,
        user_id=current_user_id,
        dashboard_id=dashboard.id,
        list_id=0,
        position=1000
    )
    db.session.add(new_task)
    db.session.commit()

    return jsonify(new_task.to_dict()), 201