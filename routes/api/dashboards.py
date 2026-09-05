from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from database.base import db
from model.dashboard import Dashboard


dashboards_api_bp = Blueprint("dashboards_api", __name__)


@dashboards_api_bp.route("/dashboards", methods=["GET"])
@jwt_required()
def list_dashboards():
    current_user_id = int(get_jwt_identity())
    dashboards = Dashboard.query.filter_by(user_id=current_user_id).all()
    return jsonify([dashboard.to_dict() for dashboard in dashboards]), 200


@dashboards_api_bp.route("/dashboards", methods=["POST"])
@jwt_required()
def create_dashboard():
    current_user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    name = data.get("name")
    description = data.get("description")

    if not name:
        return jsonify({"error": "Dashboard name is required"}), 400

    if not isinstance(name, str):
        return jsonify({"error": "Dashboard name must be a string"}), 400

    if description is not None and not isinstance(description, str):
        return jsonify({"error": "Description must be a string"}), 400

    if description is None:
        description = ""

    new_dashboard = Dashboard(name=name, description=description, user_id=current_user_id)
    db.session.add(new_dashboard)
    db.session.commit()

    return jsonify(new_dashboard.to_dict()), 201


@dashboards_api_bp.route("/dashboards/<int:dashboard_id>", methods=["GET"])
@jwt_required()
def dashboard_detail(dashboard_id):
    dashboard = Dashboard.query.filter_by(id=dashboard_id).first()
    if dashboard is None:
        return jsonify({"error": "Dashboard not found"}), 404

    return jsonify(dashboard.to_dict()), 200
