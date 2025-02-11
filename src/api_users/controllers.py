from flask import jsonify, request, json, Response
from flask_jwt_extended import create_access_token
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
        token = create_access_token(identity=user.id)
        user_data = {
            "id" : user.id,
            "first_name" : user.first_name,
            "middle_name" : user.middle_name,
            "last_name" : user.last_name,
            "email" : user.email
        }
        response_data = {
            "user": user_data,
            "token": token
        }
        response_json = json.dumps(response_data, sort_keys=False)

        return Response(response_json, status=200, mimetype="application/json")
    
    error_response = json.dumps({"message": "Invalid credentials"})
    return Response(error_response, status=401, mimetype="application/json")


# REGISTER    
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if Users.query.filter_by(email=email).first():
        return jsonify({"message": "User already exists"}), 400

    hashed_password = generate_password_hash(password)
    new_user = Users(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    
# CREATE USER
def create_user_controller():
    request_data = request.get_json()
    
    if Users.query.filter_by(email=request_data["email"]).first():
        return jsonify({"message": "User already exists"}), 400

    new_user = Users(
        rfid_tag=request_data["rfid_tag"],
        student_number=request_data["student_number"],
        first_name=request_data["first_name"],
        middle_name=request_data["middle_name"],
        last_name=request_data["last_name"],
        contact_num=request_data["contact_num"],
        address=request_data["address"],
        email=request_data["email"],
        password=request_data["password"],
        type_id=request_data["type_id"],
        level_id=request_data["level_id"],
        section_id=request_data["section_id"],
        strand_id=request_data["strand_id"],
    )

    new_user.password = generate_password_hash(new_user.password)

    db.session.add(new_user)
    db.session.commit()
    
    new_user = new_user.toDict()
    response_data = json.dumps(new_user, sort_keys=False)
    return Response(response_data, mimetype='application/json'), 201

# LISTING ALL USERS
def list_all_users_controller():
    users = Users.query.all()
    response = [user.toDict() for user in users]
    response_data = json.dumps(response, sort_keys=False)
    return Response(response_data, mimetype='application/json', status=200)

# USER PROFILE
def user_profile(user_id):
    user_profile = Users.query.get(user_id).toDict()
    response_data = json.dumps(user_profile, sort_keys=False)
    return Response(response_data, mimetype='application/json', status=200)

# LIST OF USERS BY TYPE
def list_of_users_by_type(type):
    users_by_type = Users.query.join(UserTypes).filter(UserTypes.type_name == type).all()
    user_data = [user.toDict() for user in users_by_type]
    
    not_a_student = ['Faculty', 'Administrator', 'Staff']
    
    if type in not_a_student:
        for user in user_data:
            if 'student_number' in user:
                del user['student_number']
    
    response_data = json.dumps(user_data, sort_keys=False)
    return Response(response_data, mimetype='application/json', status=200)

# LIST OF STUDENTS BY LEVEL
def list_of_students_by_level(level):
    student_level = Users.query.join(Levels).filter(Levels.level_name == level).all()
    user_data = [user.toDict() for user in student_level]
    response_data = json.dumps(user_data, sort_keys=False)
    return Response(response_data, mimetype='application/json', status=200)

# LIST OF STUDENTS BY SECTION
def list_of_students_by_section(section):
    student_section = Users.query.join(Sections).filter(Sections.section_name == section).all()
    user_data = [users.toDict() for users in student_section]
    response_data = json.dumps(user_data, sort_keys=False)
    return Response(response_data, mimetype='application/json', status=200)

# LIST OF STUDENTS BY STRAND
def list_of_students_by_strand(strand):
    student_strand = Users.query.join(Strands).filter(Strands.strand_name == strand).all()
    user_data = [users.toDict() for users in student_strand]
    response_data = json.dumps(user_data, sort_keys=False)
    return Response(response_data, mimetype='application/json', status=200)

# UPDATING USER INFO
def update_user(user_id):
    user = Users.query.get(user_id)
    
    if request.get_json:
        request_form = request.json
    else:
        request_form = request.form.to_dict()
   
    ignore_fields = ['student_number', 'type_name', 'level_name', 'section_name', 'strand_name']
    
    for key, value in request_form.items():
        if key not in ignore_fields:
            setattr(user, key, value)
          
    db.session.commit()

    user = user.toDict()
    response_data = json.dumps(user, sort_keys=False)
    return Response(response_data, mimetype='application/json', status=201)

# DELETE USER
def delete_user(user_id):
    Users.query.filter_by(id=user_id).delete()
    db.session.commit()

    return Response("Account with ID '{}' deleted succesfully!", statuscode=200).format(user_id)

# LOGGING ATTENDANCE RECORD
def log_attendance():
    user_id = request.json.get('user_id')
    rfid_tag = request.json.get('rfid_tag')
    status = request.json.get('status', 'in')
    
    if status not in ['in', 'out']:
        return jsonify({"error": "Invalid status, must be 'in' or 'out'."}), 400
    
    user = Users.query.filter_by(rfid_tag=rfid_tag).first()
    
    if user is None:
        return jsonify({"error": "User not found"}), 401
    
    attendance = Attendance(
        user_id=user.id,
        rfid_tag=rfid_tag,
        status=status
    )
    
    db.session.add(attendance)
    db.session.commit()    
    
    user_data = {
        "first_name": user.first_name,
        "middle_name": user.middle_name,
        "last_name": user.last_name,
        "level_name": user.level.level_name,
        "section_name": user.section.section_name,
        "strand_name": user.strand.strand_name
    }
    
    response_data = {
        "attendance": {
            "user_id": attendance.user.id,
            "rfid_tag": attendance.rfid_tag,
            "status": attendance.status,
            "timestamp": attendance.timestamp.isoformat()
        },
        "user": user_data
    }
    
    return Response(json.dumps(response_data, sort_keys=False), mimetype='application/json', status=201)