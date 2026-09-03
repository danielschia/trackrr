from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from database.base import db
from model.user import User

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "super-secret"
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
    test_user = User(user_name='Stephen Hawking',
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
    return jsonify("Sign Up Page")
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

@app.route("/auth/login")
def login():
    return "<h1>Login Page</h1>"

@app.route("/auth/logout")
def logout():
    return "<h1>Logout Page</h1>"

@app.route("/dashboards")
def dashboards():
    return "<h1>Dashboards Page</h1>"

@app.route("/dashboards/<int:dashboard_id>")
def dashboard_detail(dashboard_id):
    return f"<h1>Dashboard Detail Page for Dashboard ID: {dashboard_id}</h1>"