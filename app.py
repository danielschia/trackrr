from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from database.base import db
from model.user import User
from model.dashboard import Dashboard
from model.list import List
from model.task import Task
from dotenv import load_dotenv
import os
from pathlib import Path


load_dotenv(Path(__file__).resolve().parent / ".env")

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

db.init_app(app)
jwt = JWTManager(app)
@app.cli.command('db_create')
def db_create():
    db.create_all()
    print('Database created')


@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('Database dropped')


@app.cli.command('db_seed')
def db_seed():
    test_user = User(username='Stephen Hawking',
                        email='admin@admin.com',
                        password='admin')
    db.session.add(test_user)
    db.session.commit()
    print('Database seeded')

@app.route("/")
def home():
    return "<h1>Welcome to Trackrr</h1>"

@app.route("/auth/signup", methods=['POST'])
def signup():
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

    access_token = create_access_token(identity=new_user.id)
    return jsonify({"access_token": access_token}), 201

@app.route("/auth/login", methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or user.password != password:
        return jsonify({"error": "Invalid username or password"}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({"access_token": access_token}), 200

@app.route("/auth/logout")
def logout():
    return "<h1>Logout Page</h1>"

@app.route("/dashboards", methods=['GET'])
def dashboards():
    return "<h1>Dashboards Page</h1>"

@app.route("/dashboards/<int:dashboard_id>", methods=['GET'])
def dashboard_detail(dashboard_id):
    return f"<h1>Dashboard Detail Page for Dashboard ID: {dashboard_id}</h1>"