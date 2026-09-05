from flask import Blueprint, render_template
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask import request

from model.list import List
from database.base import db


list_web_bp = Blueprint("web_list", __name__)


@list_web_bp.route("/lists-page", methods=["GET"])
@jwt_required()
def lists_page():
    current_user_id = int(get_jwt_identity())
    lists = List.query.filter_by(user_id=current_user_id).all()
    return render_template("lists/index.html", lists=lists)

@list_web_bp.route("/lists", methods=["POST"])
@jwt_required()
def create_list():
    current_user_id = int(get_jwt_identity())
    name = request.form.get("name")
    description = request.form.get("description")
    dashboard_id = request.form.get("dashboard_id")

    if not name:
        return render_template("lists/index.html", error="List name is required"), 400

    if not isinstance(name, str):
        return render_template("lists/index.html", error="List name must be a string"), 400

    if description is not None and not isinstance(description, str):
        return render_template("lists/index.html", error="Description must be a string"), 400

    if description is None:
        description = ""

    new_list = List(name=name, description=description, user_id=current_user_id, dashboard_id=dashboard_id)
    db.session.add(new_list)
    db.session.commit()

    return render_template("lists/index.html", lists=List.query.filter_by(user_id=current_user_id).all()), 201

@list_web_bp.route("/lists/<int:list_id>", methods=["GET"])
@jwt_required()
def list_detail(list_id):
    current_user_id = int(get_jwt_identity())
    list_obj = List.query.filter_by(id=list_id, user_id=current_user_id).first()
    if list_obj is None or list_obj.user_id != current_user_id:
        return render_template("lists/detail.html", error="List not found"), 404

    return render_template("lists/detail.html", list=list_obj), 200

@list_web_bp.route("/lists/<int:list_id>/delete", methods=["POST"])
@jwt_required()
def delete_list(list_id):
    current_user_id = int(get_jwt_identity())
    list_obj = List.query.filter_by(id=list_id, user_id=current_user_id).first()
    if list_obj is None:
        return render_template("lists/index.html", error="List not found"), 404

    db.session.delete(list_obj)
    db.session.commit()

    return render_template("lists/index.html", lists=List.query.filter_by(user_id=current_user_id).all()), 200