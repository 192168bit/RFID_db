from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from .models import Users

from src.app import app
from .controllers import (
    get_levels,
    get_sections,
    get_strands,
    get_students,
    list_all_users_controller,
    create_user_controller,
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


@app.route("/students", methods=["GET"])
@jwt_required()
def students():
    return get_students()

# Get all levels
@app.route("/levels", methods=["GET"])
def levels():
    return get_levels()

# Get all sections
@app.route("/sections", methods=["GET"])
def sections():
    return get_sections()

# Get all strands
@app.route("/strands", methods=["GET"])
def strands():
    return get_strands()

@app.route("/log_attendance", methods=['POST'])
def create_log_attendance():
    return log_attendance()