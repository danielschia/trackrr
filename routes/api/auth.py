from flask import Blueprint, jsonify, request
from flask_openapi3 import APIBlueprint, Info, Tag
from pydantic import BaseModel, Field
from flask_jwt_extended import create_access_token
from database.base import db
from model.user import User

auth_tag = Tag(name="Auth", description="Operations related to authentication")
auth_api_bp = APIBlueprint("auth_api", __name__)

class SignupBody(BaseModel):
    username: str = Field(min_length=1, description="The username of the new user")
    email: str = Field(min_length=1, description="The email of the new user")
    password: str = Field(min_length=1, description="The password of the new user")

class LoginBody(BaseModel):
    username: str = Field(min_length=1, description="The username of the user")
    password: str = Field(min_length=1, description="The password of the user")

class ErrorResponse(BaseModel):
    error: str = Field(description="Error message")


@auth_api_bp.post("/signup", tags=[auth_tag], responses={"400": ErrorResponse, "201": SignupBody})
def api_signup():
    data = request.get_json() or {}
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "Username, email, and password are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    new_user = User(username=username, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    access_token = create_access_token(identity=str(new_user.id))
    return jsonify({"access_token": access_token}), 201

@auth_api_bp.post("/login", tags=[auth_tag], responses={"400": ErrorResponse, "401": ErrorResponse, "200": LoginBody})
def api_login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid username or password"}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": access_token}), 200