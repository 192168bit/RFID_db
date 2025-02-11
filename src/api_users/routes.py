from flask import request

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

@app.route("/users", methods=["GET", "POST"])
def list_create_users():
    if request.method == "GET":
        return list_all_users_controller()
    if request.method == "POST":
        return create_user_controller()
    else:
        return "Method is Not Allowed"


@app.route("/users/<user_id>", methods=["GET", "PUT", "DELETE"])
def profile_update_delete_user(user_id):
    if request.method == "GET":
        return user_profile(user_id)
    if request.method == "PUT":
        return update_user(user_id)
    if request.method == "DELETE":
        return delete_user(user_id)
    else:
        return "Method is Not Allowed"


@app.route("/types/<type>", methods=["GET"])
def get_user_type(type):
    return list_of_users_by_type(type)


@app.route("/students/<filter_type>/<value>", methods=["GET"])
def get_list_of_students_by_filter(filter_type, value):
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