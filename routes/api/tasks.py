from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from database.base import db
from model.dashboard import Dashboard
from model.list import List
from model.task import Task


tasks_api_bp = Blueprint("tasks_api", __name__)


@tasks_api_bp.route("/tasks", methods=["POST"])
@jwt_required()
def create_task():
    current_user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    title = (data.get("title") or "").strip()
    description_raw = data.get("description")
    if description_raw is None:
        description = ""
    elif not isinstance(description_raw, str):
        return jsonify({"error": "Description must be a string"}), 400
    else:
        description = description_raw
    dashboard_id = data.get("dashboard_id")
    list_id = data.get("list_id")

    if not title:
        return jsonify({"error": "Task title is required"}), 400

    if not isinstance(title, str):
        return jsonify({"error": "Task title must be a string"}), 400

    if not dashboard_id:
        return jsonify({"error": "Dashboard id is required"}), 400

    if not list_id:
        return jsonify({"error": "List id is required"}), 400

    dashboard = Dashboard.query.filter_by(id=dashboard_id, user_id=current_user_id).first()
    if dashboard is None:
        return jsonify({"error": "Dashboard not found"}), 404

    list_obj = List.query.filter_by(id=list_id, user_id=current_user_id, dashboard_id=dashboard.id).first()
    if list_obj is None:
        return jsonify({"error": "List not found"}), 404

    new_task = Task(
        title=title,
        description=description,
        user_id=current_user_id,
        dashboard_id=dashboard.id,
        list_id=list_obj.id,
        position=1000
    )
    db.session.add(new_task)
    db.session.commit()

    return jsonify(new_task.to_dict()), 201

@tasks_api_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
@jwt_required()
def delete_task(task_id):
    current_user_id = int(get_jwt_identity())
    task = Task.query.filter_by(id=task_id, user_id=current_user_id).first()
    if task is None:
        return jsonify({"error": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()

    return jsonify({"message": "Task deleted successfully"}), 200

@tasks_api_bp.route("/tasks/<int:task_id>", methods=["PUT"])
@jwt_required()
def update_task(task_id):
    current_user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    list_id = data.get("list_id")
    position = data.get("position")
    title = data.get("title")
    description = data.get("description")
    task = Task.query.filter_by(id=task_id, user_id=current_user_id).first()
    if task is None:
        return jsonify({"error": "Task not found"}), 404

    if list_id is not None:
        list_obj = List.query.filter_by(id=list_id, user_id=current_user_id, dashboard_id=task.dashboard_id).first()
        if list_obj is None:
            return jsonify({"error": "List not found"}), 404
        if list_obj.dashboard_id != task.dashboard_id:
            return jsonify({"error": "List does not belong to the same dashboard as the task"}), 400
        task.list_id = list_obj.id

    if position is not None:
        if not isinstance(position, int):
            return jsonify({"error": "Position must be an integer"}), 400
        task.position = position

    if title is not None:
        if title.strip() == "":
            return jsonify({"error": "Task title is required"}), 400
        if not isinstance(title, str):
            return jsonify({"error": "Task title must be a string"}), 400
        task.title = title.strip()
    

    if description is not None:
        if description.strip() == "":
            return jsonify({"error": "Task description cannot be empty"}), 400
        if not isinstance(description, str):
            return jsonify({"error": "Description must be a string"}), 400
        task.description = description.strip()

    db.session.commit()

    return jsonify(task.to_dict()), 200