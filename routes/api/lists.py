from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from database.base import db
from model.dashboard import Dashboard
from model.list import List


lists_api_bp = Blueprint("lists_api", __name__)


@lists_api_bp.route("/lists", methods=["POST"])
@jwt_required()
def create_list():
    current_user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    description = data.get("description") or ""
    dashboard_id = data.get("dashboard_id")

    if not name:
        return jsonify({"error": "List name is required"}), 400

    if not isinstance(name, str):
        return jsonify({"error": "List name must be a string"}), 400

    if description is not None and not isinstance(description, str):
        return jsonify({"error": "Description must be a string"}), 400

    if not dashboard_id:
        return jsonify({"error": "Dashboard id is required"}), 400

    dashboard = Dashboard.query.filter_by(id=dashboard_id, user_id=current_user_id).first()
    if dashboard is None:
        return jsonify({"error": "Dashboard not found"}), 404

    new_list = List(
        name=name,
        description=description,
        user_id=current_user_id,
        dashboard_id=dashboard.id,
    )
    db.session.add(new_list)
    db.session.commit()

    return jsonify(new_list.to_dict()), 201