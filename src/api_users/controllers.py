from datetime import datetime
from flask import jsonify, request, json, Response
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from src import db
from .models import Attendance, Levels, Strands, UserTypes, Users, Sections
from werkzeug.security import generate_password_hash, check_password_hash


# USER LOGIN
def user_login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = Users.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        # Include both user.id and user.role in the token as a JSON string
        identity = json.dumps({"id": user.id, "role": user.type.type_name})
        token = create_access_token(identity=identity)

        user_data = {
            "id": user.id,
            "first_name": user.first_name,
            "middle_name": user.middle_name,
            "last_name": user.last_name,
            "email": user.email,
            "type": user.type.type_name,
        }

        response_data = {"user": user_data, "token": token}
        response_json = json.dumps(response_data, sort_keys=False)

        return Response(response_json, status=200, mimetype="application/json")

    error_response = json.dumps({"message": "Invalid credentials"})
    return Response(error_response, status=401, mimetype="application/json")


# CREATE USER
@jwt_required()  # Require authentication
def create_user_controller():
    request_data = request.get_json()

    # Get the logged-in user's identity (which is a JSON string in this case)
    current_user = json.loads(get_jwt_identity())

    # Ensure we are dealing with a dictionary and that it contains the 'role' key
    if not isinstance(current_user, dict) or "role" not in current_user:
        return jsonify({"message": "Invalid token format."}), 401

    # Check if the user is an admin
    if current_user["role"] != "Administrator":
        return jsonify({"message": "Access denied. Admins only."}), 403

    # Check if user already exists
    if Users.query.filter_by(email=request_data["email"]).first():
        return jsonify({"message": "User already exists"}), 400

    # Create a new user
    new_user = Users(
        rfid_tag=request_data["rfid_tag"],
        first_name=request_data["first_name"],
        middle_name=request_data["middle_name"],
        last_name=request_data["last_name"],
        contact_num=request_data["contact_num"],
        address=request_data["address"],
        email=request_data["email"],
        password=generate_password_hash(request_data["password"]),
        type_id=request_data["type_id"],
        level_id=request_data["level_id"],
        section_id=request_data["section_id"],
        strand_id=request_data["strand_id"],
    )

    db.session.add(new_user)
    db.session.commit()

    response_data = json.dumps(new_user.toDict(), sort_keys=False)
    return Response(response_data, mimetype="application/json"), 201


# LISTING ALL USERS
def list_all_users_controller():
    users = Users.query.all()
    response = [user.toDict() for user in users]
    response_data = json.dumps(response, sort_keys=False)
    return Response(response_data, mimetype="application/json", status=200)


# USER PROFILE
def user_profile(user_id):
    user_profile = Users.query.get(user_id).toDict()
    response_data = json.dumps(user_profile, sort_keys=False)
    return Response(response_data, mimetype="application/json", status=200)


# LIST OF USERS BY TYPE
def list_of_users_by_type(type):
    users_by_type = (
        Users.query.join(UserTypes).filter(UserTypes.type_name == type).all()
    )
    user_data = [user.toDict() for user in users_by_type]

    not_a_student = ["Faculty", "Administrator", "Staff"]

    if type in not_a_student:
        for user in user_data:
            if "student_number" in user:
                del user["student_number"]

    response_data = json.dumps(user_data, sort_keys=False)
    return Response(response_data, mimetype="application/json", status=200)


def get_students():
    level_id = request.args.get("level_id")
    section_id = request.args.get("section_id")
    strand_id = request.args.get("strand_id")

    query = Users.query

    if level_id:
        query = query.filter(Users.level_id == level_id)
    if section_id:
        query = query.filter(Users.section_id == section_id)
    if strand_id:
        query = query.filter(Users.strand_id == strand_id)

    students = query.all()
    student_data = [student.toDict() for student in students]

    return Response(
        json.dumps(student_data, sort_keys=False),
        mimetype="application/json",
        status=200,
    )


# Fetch all levels
def get_levels():
    levels = Levels.query.all()
    level_data = [{"id": level.id, "name": level.level_name} for level in levels]
    return jsonify(level_data)


# Fetch all sections
def get_sections():
    sections = Sections.query.all()
    section_data = [
        {"id": section.id, "name": section.section_name} for section in sections
    ]
    return jsonify(section_data)


# Fetch all strands
def get_strands():
    strands = Strands.query.all()
    strand_data = [{"id": strand.id, "name": strand.strand_name} for strand in strands]
    return jsonify(strand_data)


def get_personnel():
    type_id = request.args.get("type_id")
    query = Users.query

    # Define list of non-personnel types that shouldn't appear as "personnel"
    non_personnel_types = ['Student']

    if type_id:
        try:
            type_id = int(type_id)  # Ensure type_id is an integer
            query = query.filter(Users.type_id == type_id)
        except ValueError:
            return jsonify({"error": "Invalid type_id format"}), 400
    else:
        # Filter out students by excluding user types associated with students
        query = query.join(UserTypes).filter(~UserTypes.type_name.in_(non_personnel_types))

    personnels = query.all()
    personnel_data = [personnel.toDict() for personnel in personnels]

    return Response(
        json.dumps(personnel_data, sort_keys=False),
        mimetype="application/json",
        status=200,
    )


def get_types():
    types = UserTypes.query.all()
    type_data = [{"id": type.id, "name": type.type_name} for type in types]
    return jsonify(type_data)


# UPDATING USER INFO
def update_user(user_id):
    user = Users.query.get(user_id)

    if request.get_json:
        request_form = request.json
    else:
        request_form = request.form.to_dict()

    ignore_fields = [
        "student_number",
        "type_name",
        "level_name",
        "section_name",
        "strand_name",
    ]

    for key, value in request_form.items():
        if key not in ignore_fields:
            setattr(user, key, value)

    db.session.commit()

    user = user.toDict()
    response_data = json.dumps(user, sort_keys=False)
    return Response(response_data, mimetype="application/json", status=201)


# DELETE USER
def delete_user(user_id):
    Users.query.filter_by(id=user_id).delete()
    db.session.commit()

    return Response("Account with ID '{}' deleted succesfully!", statuscode=200).format(
        user_id
    )


# LOGGING ATTENDANCE RECORD
def log_attendance():
    user_id = request.json.get("user_id")
    rfid_tag = request.json.get("rfid_tag")
    status = request.json.get("status", "in")

    if status not in ["in", "out"]:
        return jsonify({"error": "Invalid status, must be 'in' or 'out'."}), 400

    user = Users.query.filter_by(rfid_tag=rfid_tag).first()

    if user is None:
        return jsonify({"error": "User not found"}), 401

    attendance = Attendance(user_id=user.id, rfid_tag=rfid_tag, status=status)

    db.session.add(attendance)
    db.session.commit()

    response_data = {
        "attendance": {
            "user_id": attendance.user.id,
            "rfid_tag": attendance.rfid_tag,
            "status": attendance.status,
            "timestamp": attendance.timestamp.isoformat(),
        },
    }

    return Response(
        json.dumps(response_data, sort_keys=False),
        mimetype="application/json",
        status=201,
    )
    
def get_attendance():
    # Get the selected year, month, and day from the query params
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)
    day = request.args.get("day", type=int)

    if not year or not month or not day:
        return jsonify({"error": "Year, month, and day are required"}), 400

    # Query attendance records for the selected date
    start_date = datetime(year, month, day, 0, 0, 0)  # Start of the selected day
    end_date = datetime(year, month, day, 23, 59, 59)  # End of the selected day

    attendance_records = Attendance.query.filter(
        Attendance.timestamp.between(start_date, end_date)
    ).all()

    attendance_data = []
    for attendance in attendance_records:
        user_data = {
            "first_name": attendance.user.first_name,
            "middle_name": attendance.user.middle_name,
            "last_name": attendance.user.last_name,
            "status": attendance.status,
            "timestamp": attendance.timestamp.isoformat(),
        }
        attendance_data.append(user_data)

    return Response(
        json.dumps(attendance_data, sort_keys=False),
        mimetype="application/json",
        status=201,
    )

def get_latest_attendance():
    # Query to get the latest attendance record
    latest_attendance = Attendance.query.order_by(Attendance.timestamp.desc()).first()

    # If no attendance records are found, return an error
    if not latest_attendance:
        return jsonify({"error": "No attendance records found."}), 404

    # Fetch the user associated with the latest attendance
    user = Users.query.filter_by(id=latest_attendance.user_id).first()

    # If the user is not found, return an error
    if not user:
        return jsonify({"error": "User not found."}), 404

    # Prepare user data for the response
    user_data = {
        "rfid_tag": latest_attendance.rfid_tag,
        "status": latest_attendance.status,
        "first_name": user.first_name,
        "middle_name": user.middle_name,
        "last_name": user.last_name,
        "email" : user.email,
    }

    # Include student-specific data (level, section, strand) only if the user is a student
    if user.type.type_name == "Student":
        user_data.update({
            "level_name": user.level.level_name if user.level else "N/A",
            "section_name": user.section.section_name if user.section else "N/A",
            "strand_name": user.strand.strand_name if user.strand else "N/A",
        })
    else:
        # For non-student users, include role or any other relevant user-specific info
        user_data.update({
            "role": user.type.type_name,  # Assuming you want to include role for non-student users
        })

    # Prepare the response data
    attendance_data = {
        "attendance": {
            "user_id": latest_attendance.user_id,
            "rfid_tag": latest_attendance.rfid_tag,
            "status": latest_attendance.status,
            "timestamp": latest_attendance.timestamp.isoformat(),
        },
        "user": user_data,
    }

    return Response(
        json.dumps(attendance_data, default=str, sort_keys=False),
        mimetype="application/json",
        status=200,
    )
