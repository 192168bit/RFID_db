import os
from flask import jsonify, request, send_from_directory
from flask_jwt_extended import jwt_required
from .controllers import (
    calculate_attendance_percentage,
    create_event,
    delete_event,
    get_all_events,
    get_attendance,
    get_event_by_id,
    get_latest_attendance,
    get_levels,
    get_personnel,
    get_rfids,
    get_sections,
    get_strands,
    get_students,
    get_types,
    list_all_users_controller,
    create_user_controller,
    log_attendance,
    update_event,
    upload_image,
    user_login,
    user_profile,
    update_user,
    delete_user,
)
from src.app import app
from src.config import UPLOAD_FOLDER

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

@app.route("/rfids", methods=["GET"])
@jwt_required()
def rfid():
    return get_rfids()


@app.route("/log_attendance", methods=["POST"])
def create_log_attendance():
    return log_attendance()


@app.route("/get_attendance", methods=["GET"])
@jwt_required()
def get_attendances():
    return get_attendance()


@app.route("/latest_attendance", methods=["GET"])
def get_one_latest_attendance():
    return get_latest_attendance()


@app.route("/stats", methods=["GET"])
def get_total_present():
    return calculate_attendance_percentage()


@app.route('/upload', methods=['POST'])
def upload():
    return upload_image()


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(os.path.abspath(UPLOAD_FOLDER), filename)

@app.route("/events", methods=["GET"])
def get_events():
    return get_all_events()

# Fetch a single event by ID
@app.route("/events/<int:event_id>", methods=["GET"])
def get_event(event_id):
    return get_event_by_id(event_id)

# Create a new event
@app.route("/events", methods=["POST"])
def add_event():
    return create_event()

# Update an existing event
@app.route("/events/<int:event_id>", methods=["PUT"])
def modify_event(event_id):
    return update_event(event_id)

# Delete an event
@app.route("/events/<int:event_id>", methods=["DELETE"])
def remove_event(event_id):
    return delete_event(event_id)