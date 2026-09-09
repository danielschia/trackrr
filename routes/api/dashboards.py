from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_openapi3 import APIBlueprint, Tag
from pydantic import BaseModel, Field
from database.base import db
from model.dashboard import Dashboard


dashboards_api_bp = APIBlueprint("dashboards_api", __name__)

class CreateDashboardBody(BaseModel):
    name: str = Field(min_length=1, description="The name of the dashboard")
    description: str | None = Field(default=None, description="The description of the dashboard")

class ErrorResponse(BaseModel):
    error: str = Field(description="Error message")


@dashboards_api_bp.get("/dashboards", tags=[Tag(name="Dashboards", description="Operations related to dashboards")], responses={"200": CreateDashboardBody})
@jwt_required()
def list_dashboards():
    current_user_id = int(get_jwt_identity())
    dashboards = Dashboard.query.filter_by(user_id=current_user_id).all()
    return jsonify([dashboard.to_dict() for dashboard in dashboards]), 200


@dashboards_api_bp.post("/dashboards", tags=[Tag(name="Dashboards", description="Operations related to dashboards")], responses={"400": ErrorResponse, "201": CreateDashboardBody})
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


@dashboards_api_bp.get("/dashboards/<int:dashboard_id>", tags=[Tag(name="Dashboards", description="Operations related to dashboards")], responses={"404": ErrorResponse, "200": CreateDashboardBody})
@jwt_required()
def dashboard_detail(dashboard_id):
    dashboard = Dashboard.query.filter_by(id=dashboard_id).first()
    if dashboard is None:
        return jsonify({"error": "Dashboard not found"}), 404

    return jsonify(dashboard.to_dict()), 200
