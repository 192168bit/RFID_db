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

    current_user = json.loads(get_jwt_identity())

    if not isinstance(current_user, dict) or "role" not in current_user:
        return jsonify({"message": "Invalid token format."}), 401

    if current_user["role"] != "Administration":
        return jsonify({"message": "Access denied. Admins only."}), 403

    if Users.query.filter_by(email=request_data["email"]).first():
        return jsonify({"message": "User already exists"}), 400

    # Create a new user
    new_user = Users(
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

    not_a_student = ["Faculty", "Administration", "Staff"]

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

    # Create the initial query
    query = (
        db.session.query(Users).join(UserTypes).filter(UserTypes.type_name == "Student")
    )

    # Apply filters if provided
    if level_id:
        query = query.filter(Users.level_id == level_id)
    if section_id:
        query = query.filter(Users.section_id == section_id)
    if strand_id:
        query = query.filter(Users.strand_id == strand_id)

    # Execute the query and get all students
    students = query.all()

    # Convert students to dictionaries using toDict() method
    student_data = [student.toDict() for student in students]

    # Return the JSON response
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
    non_personnel_types = ["Student"]

    if type_id:
        try:
            type_id = int(type_id)  # Ensure type_id is an integer
            query = query.filter(Users.type_id == type_id)
        except ValueError:
            return jsonify({"error": "Invalid type_id format"}), 400
    else:
        # Filter out students by excluding user types associated with students
        query = query.join(UserTypes).filter(
            ~UserTypes.type_name.in_(non_personnel_types)
        )

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
    rfid_tag = request.json.get("rfid_tag")

    if not rfid_tag:
        return jsonify({"error": "RFID tag is required"}), 400

    # Find the user based on RFID tag
    user = Users.query.filter_by(rfid_tag=rfid_tag).first()
    if user is None:
        return jsonify({"error": "User not found"}), 401

    # Get the current date and time
    current_time = datetime.now()
    start_of_day = datetime(
        current_time.year, current_time.month, current_time.day, 0, 0, 0
    )
    end_of_day = datetime(
        current_time.year, current_time.month, current_time.day, 23, 59, 59
    )

    # Check attendance for today
    today_attendance = (
        Attendance.query.filter(
            Attendance.user_id == user.id,
            Attendance.timestamp.between(start_of_day, end_of_day),
        )
        .order_by(Attendance.timestamp)
        .all()
    )

    # if not today_attendance:
    # First scan → Log "Time In"
    new_attendance = Attendance(
        user_id=user.id, rfid_tag=rfid_tag, status="in", timestamp=current_time
    )
    db.session.add(new_attendance)
    db.session.commit()

    # Call `calculate_attendance_percentage()` after logging time-in (no need to pass time_in)
    return calculate_attendance_percentage()  # Removed 'time_in'

    # elif len(today_attendance) == 1:
    #     # Second scan → Log "Time Out"
    #     new_attendance = Attendance(
    #         user_id=user.id, rfid_tag=rfid_tag, status="out", timestamp=current_time
    #     )
    #     db.session.add(new_attendance)
    #     db.session.commit()

    #     # Call `calculate_attendance_percentage()` after logging time-out (no need to pass time_out)
    #     return calculate_attendance_percentage()  # Removed 'time_out'

    # else:
    #     # Prevent multiple entries (already logged in and out today)
    #     return jsonify({"error": "User already logged in and out today"}), 400


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
    latest_attendance = Attendance.query.order_by(Attendance.timestamp.desc()).first()

    if not latest_attendance:
        return jsonify({"error": "No attendance records found."}), 404

    user = Users.query.filter_by(id=latest_attendance.user_id).first()

    if not user:
        return jsonify({"error": "User not found."}), 404

    user_data = {
        "rfid_tag": latest_attendance.rfid_tag,
        "status": latest_attendance.status,
        "first_name": user.first_name,
        "middle_name": user.middle_name,
        "last_name": user.last_name,
        "email": user.email,
    }

    if user.type.type_name == "Student":
        user_data.update(
            {
                "level_name": user.level.level_name if user.level else "N/A",
                "section_name": user.section.section_name if user.section else "N/A",
                "strand_name": user.strand.strand_name if user.strand else "N/A",
            }
        )
    else:
        user_data.update(
            {
                "role": user.type.type_name,
            }
        )
    attendance_data = {
        "user": user_data,
        "rfid_tag": latest_attendance.rfid_tag,
        "status": latest_attendance.status,
        "timestamp": latest_attendance.timestamp.isoformat(),
    }

    return Response(
        json.dumps(attendance_data, default=str, sort_keys=False),
        mimetype="application/json",
        status=200,
    )


def calculate_attendance_percentage():
    """Calculate the percentage of students and personnel who have timed in."""
    student_type = "Student"

    # Get total count of students and personnel
    total_students = (
        Users.query.join(UserTypes).filter(UserTypes.type_name == student_type).count()
    )
    total_personnel = (
        Users.query.join(UserTypes).filter(UserTypes.type_name != student_type).count()
    )

    # If no registered users are found
    if total_students == 0 and total_personnel == 0:
        return jsonify({"error": "No registered users"}), 400

    # Start of day (00:00:00)
    start_of_day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # Calculate number of students who are timed in (status == 'in')
    timed_in_students = (
        Attendance.query.join(Users)
        .join(UserTypes)
        .filter(
            Attendance.status == "in",
            Attendance.timestamp >= start_of_day,
            UserTypes.type_name == student_type,
        )
        .distinct(Attendance.user_id)
        .count()
    )

    # Calculate number of personnel who are timed in (status == 'in')
    timed_in_personnel = (
        Attendance.query.join(Users)
        .join(UserTypes)
        .filter(
            Attendance.status == "in",
            Attendance.timestamp >= start_of_day,
            UserTypes.type_name != student_type,
        )
        .distinct(Attendance.user_id)
        .count()
    )

    # Calculate attendance percentages
    student_attendance_percentage = (
        (timed_in_students / total_students * 100) if total_students > 0 else 0
    )
    personnel_attendance_percentage = (
        (timed_in_personnel / total_personnel * 100) if total_personnel > 0 else 0
    )

    # Format response data
    response_data = {
        "student_attendance_percentage": f"{student_attendance_percentage:.2f}%",
        "personnel_attendance_percentage": f"{personnel_attendance_percentage:.2f}%",
    }

    return jsonify(response_data), 200
