from flask import jsonify, request
from flask_jwt_extended import jwt_required
from .controllers import (
    get_attendance, get_latest_attendance, get_levels, get_personnel, get_sections, get_strands, get_students, 
    get_types, list_all_users_controller, create_user_controller, 
    log_attendance, user_login, user_profile, update_user, delete_user
)
from src.app import app

@app.route("/login", methods=["POST"])
def get_user_login():
    return user_login()

@app.route("/new-user", methods=["POST"])
@jwt_required()
def get_create_user():
    return create_user_controller()

@app.route("/users", methods=["GET"])
@jwt_required()
def get_list_users():
    return list_all_users_controller()

@app.route("/users/<user_id>", methods=["GET", "PUT", "DELETE"])
@jwt_required()
def profile_update_delete_user(user_id):
    if request.method == "GET":
        return user_profile(user_id)
    if request.method == "PUT":
        return update_user(user_id)
    if request.method == "DELETE":
        return delete_user(user_id)

@app.route("/personnel", methods=["GET"])
@jwt_required()
def personnel():
    return get_personnel()

@app.route("/types", methods=["GET"])
@jwt_required()
def types():
    return get_types()

@app.route("/students", methods=["GET"])
@jwt_required()
def students():
    return get_students()

@app.route("/levels", methods=["GET"])
@jwt_required()
def levels():
    return get_levels()

@app.route("/sections", methods=["GET"])
@jwt_required()
def sections():
    return get_sections()

@app.route("/strands", methods=["GET"])
@jwt_required()
def strands():
    return get_strands()

@app.route("/log_attendance", methods=['POST'])
@jwt_required()
def create_log_attendance():
    return log_attendance()

@app.route("/get_attendance", methods=['GET'])
@jwt_required()
def get_attendances():
    return get_attendance()

@app.route("/latest-attendance", methods=['GET'])
@jwt_required()
def get_one_latest_attendance():
    return get_latest_attendance()
