from datetime import date, datetime
import os
from flask import jsonify, request, json, Response
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from sqlalchemy import distinct
from src import db
from src.config import ALLOWED_EXTENSIONS, BASE_URL, UPLOAD_FOLDER
from .models import Attendance, Levels, Strands, UserTypes, Users, Sections
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename


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
    
    current_user = json.loads(get_jwt_identity())
    photo_url = ""
    file = request.files.get('photo_url')
    print(file)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        photo_url = f"{BASE_URL}/uploads/{filename}"
        
    if not isinstance(current_user, dict) or "role" not in current_user:
        return jsonify({"message": "Invalid token format."}), 401

    if current_user["role"] != "Administration":
        return jsonify({"message": "Access denied. Admins only."}), 403

    if Users.query.filter_by(email=request.form.get("email")).first():
        return jsonify({"message": "User already exists"}), 400

    # Create a new user
    new_user = Users(
        first_name=request.form.get("first_name"),
        middle_name=request.form.get("middle_name"),
        last_name=request.form.get("last_name"),
        contact_num=request.form.get("contact_num"),
        photo_url=photo_url,
        email=request.form.get("email"),
        password=generate_password_hash(request.form.get("password")),
        type_id=request.form.get("type_id"),
        level_id=request.form.get("level_id"),
        section_id=request.form.get("section_id"),
        strand_id=request.form.get("strand_id"),
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

    # Start the query
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

    # Apply sorting
    query = query.order_by(Users.level_id, Users.section_id, Users.strand_id)

    students = query.all()

    student_data = []
    for student in students:
        student_data.append(
            {
                "id": student.id,
                "first_name": student.first_name,
                "middle_name": student.middle_name,
                "last_name": student.last_name,
                "contact_num": student.contact_num,
                "level_id": student.level_id,
                "section_id": student.section_id,
                "strand_id": student.strand_id,
            }
        )

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
    type_id = request.args.get("type_id", type=int)

    # Exclude students, only fetch personnel
    query = Users.query.join(UserTypes).filter(~UserTypes.type_name.in_(["Student"]))

    if type_id:
        query = query.filter(Users.type_id == type_id)

    personnels = query.all()

    personnel_data = [
        {
            "id": personnel.id,
            "first_name": personnel.first_name,
            "middle_name": personnel.middle_name,
            "last_name": personnel.last_name,
            "contact_num": personnel.contact_num,
            "type_id": personnel.type_id,
        }
        for personnel in personnels
    ]

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
    """Logs student or personnel attendance based on RFID scans."""
    rfid_tag = request.json.get("rfid_tag")

    if not rfid_tag:
        return jsonify({"error": "RFID tag is required"}), 400

    # Find the user based on RFID tag
    user = Users.query.filter_by(rfid_tag=rfid_tag).first()
    if user is None:
        return jsonify({"error": "User not found"}), 401

    # Get the current date and time
    current_time = datetime.now()
    start_of_day = datetime.combine(current_time.date(), datetime.min.time())
    end_of_day = datetime.combine(current_time.date(), datetime.max.time())

    # Check today's attendance record
    today_attendance = (
        Attendance.query.filter(
            Attendance.user_id == user.id,
            Attendance.timestamp >= start_of_day,
            Attendance.timestamp <= end_of_day,
        )
        .order_by(Attendance.timestamp)
        .first()
    )

    # Format time in 12-hour format with AM/PM
    def format_time(timestamp):
        return timestamp.strftime("%I:%M:%S %p") if timestamp else None

    if not today_attendance:
        # First scan → Log "Time In"
        new_attendance = Attendance(
            user_id=user.id,
            rfid_tag=rfid_tag,
            status="in",
            timestamp=current_time,
            time_in=current_time,
            time_out=None,  # Ensure time_out starts as None
        )
        db.session.add(new_attendance)

        # Commit the transaction and add logging
        try:
            db.session.commit()
            print(
                f"Attendance logged for user {user.id}: time_in={new_attendance.time_in}"
            )
        except Exception as e:
            db.session.rollback()  # Rollback in case of error
            return jsonify({"error": f"Failed to log attendance: {str(e)}"}), 500

        return jsonify(
            {"message": "Time In recorded", "time_in": format_time(current_time)}
        ), 200

    elif today_attendance.time_out is None:
        # Second scan → Log "Time Out" (only if time_out is not set)
        today_attendance.status = "out"
        today_attendance.time_out = current_time

        # Commit the transaction and add logging
        try:
            db.session.commit()
            print(
                f"Attendance updated for user {user.id}: time_out={today_attendance.time_out}"
            )
        except Exception as e:
            db.session.rollback()  # Rollback in case of error
            return jsonify({"error": f"Failed to log time out: {str(e)}"}), 500

        return jsonify(
            {"message": "Time Out recorded", "time_out": format_time(current_time)}
        ), 200

    else:
        # Prevent multiple scans after logging out
        return jsonify({"error": "User already logged in and out today"}), 400


def get_attendance():
    # Parse query parameters
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)
    day = request.args.get("day", type=int)
    level_id = request.args.get("level_id", type=int)
    section_id = request.args.get("section_id", type=int)
    strand_id = request.args.get("strand_id", type=int)
    type_id = request.args.get("type_id", type=int)  # For filtering personnel types

    # Validate required parameters
    if not all([year, month, day]):
        return jsonify({"error": "Year, month, and day are required"}), 400

    # Define the start and end of the day
    start_date = datetime(year, month, day, 0, 0, 0)
    end_date = datetime(year, month, day, 23, 59, 59)

    # Build the query with filters
    query = Attendance.query.join(Users).filter(
        Attendance.timestamp.between(start_date, end_date)
    )

    # Apply additional filters if provided
    if type_id:
        query = query.filter(Users.type_id == type_id)
    else:
        # Default to filtering for students if no type_id is provided
        query = query.filter(Users.type.has(type_name="Student"))

    if level_id:
        query = query.filter(Users.level_id == level_id)
    if section_id:
        query = query.filter(Users.section_id == section_id)
    if strand_id:
        query = query.filter(Users.strand_id == strand_id)

    # Execute the query to fetch attendance records
    attendance_records = query.all()
   
    # Prepare the attendance data to be returned
    attendance_data = [
        {
            "id": attendance.user.id,
            "first_name": attendance.user.first_name,
            "middle_name": attendance.user.middle_name,
            "last_name": attendance.user.last_name,
            "contact_num": attendance.user.contact_num,
            "type_id": attendance.user.type_id,
            "status": attendance.status,
            "timestamp": attendance.timestamp.isoformat(),
            "time_in": attendance.time_in.isoformat() if attendance.time_in else None,
            "time_out": attendance.time_out.isoformat()
            if attendance.time_out
            else None,
        }
        for attendance in attendance_records
    ]
    print(attendance_data)
    # Return the response with proper JSON formatting
    return jsonify(attendance_data), 200


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
        "photo_url": user.photo_url
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
    """Calculate the percentage of students and personnel who have timed in and not yet timed out."""
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

    # Start of day (00:00:00) for accurate filtering
    start_of_day = datetime.combine(date.today(), datetime.min.time())

    # Get users who timed in today
    timed_in_users = (
        Attendance.query.filter(
            Attendance.status == "in",
            Attendance.timestamp >= start_of_day,
        )
        .with_entities(distinct(Attendance.user_id))
        .subquery()
    )

    # Get users who timed out today
    timed_out_users = (
        Attendance.query.filter(
            Attendance.status == "out",
            Attendance.timestamp >= start_of_day,
        )
        .with_entities(distinct(Attendance.user_id))
        .subquery()
    )

    # Count students who are still timed in (timed in but not timed out)
    timed_in_students = (
        Users.query.join(UserTypes)
        .filter(
            UserTypes.type_name == student_type,
            Users.id.in_(timed_in_users),  # Users who timed in
            ~Users.id.in_(timed_out_users),  # Exclude users who timed out
        )
        .count()
    )

    # Count personnel who are still timed in
    timed_in_personnel = (
        Users.query.join(UserTypes)
        .filter(
            UserTypes.type_name != student_type,
            Users.id.in_(timed_in_users),
            ~Users.id.in_(timed_out_users),
        )
        .count()
    )

    # Calculate attendance percentages safely
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

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        return jsonify({'message': 'File uploaded successfully', 'path': file_path}), 200

    return jsonify({'error': 'Invalid file type'}), 400