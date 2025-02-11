from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from .models import Users

from src.app import app
from .controllers import (
    list_all_users_controller,
    create_user_controller,
    list_of_students_by_level,
    list_of_students_by_section,
    list_of_students_by_strand,
    log_attendance,
    user_login,
    user_profile,
    update_user,
    delete_user,
    list_of_users_by_type,
)

@app.route("/login", methods=["POST"])
def get_user_login():
    return user_login()

@app.route("/new-user", methods=["POST"])
def get_create_user():
    return create_user_controller()

@app.route("/users", methods=["GET"])
@jwt_required()
def get_list_users():
    current_user_id = get_jwt_identity()
    user = Users.query.get(current_user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    return list_all_users_controller()


@app.route("/users/<user_id>", methods=["GET", "PUT", "DELETE"])
@jwt_required()
def profile_update_delete_user(user_id):
    current_user_id = get_jwt_identity()
    user = Users.query.get(current_user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404    
    if request.method == "GET":
        return user_profile(user_id)
    if request.method == "PUT":
        return update_user(user_id)
    if request.method == "DELETE":
        return delete_user(user_id)
    else:
        return "Method is Not Allowed"


@app.route("/types/<type>", methods=["GET"])
@jwt_required()
def get_user_type(type):
    current_user_id = get_jwt_identity()
    user = Users.query.get(current_user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    return list_of_users_by_type(type)


@app.route("/students/<filter_type>/<value>", methods=["GET"])
@jwt_required()
def get_list_of_students_by_filter(filter_type, value):
    current_user_id = get_jwt_identity()
    user = Users.query.get(current_user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    if filter_type == "level":
        return list_of_students_by_level(value)
    elif filter_type == "section":
        return list_of_students_by_section(value)
    elif filter_type == "strand":
        return list_of_students_by_strand(value)
    else:
        return "Invalid filter type", 400

@app.route("/log_attendance", methods=['POST'])
def create_log_attendance():
    return log_attendance()