from flask import jsonify, request
from src import db
from .models import UserTypes, Users


def list_all_users_controller():
    users = Users.query.all()
    response = [user.toDict() for user in users]
    return jsonify(response)


def get_user_profile(user_id):
    response = Users.query.get(user_id).toDict()
    return jsonify(response)


def list_user_by_type(type):
    users = Users.query.join(UserTypes).filter(UserTypes.type_name == type).all()
    return jsonify(
        {
            type + "s": [
                {
                    'first_name': user.first_name,
                    'middle_name': user.middle_name,
                    'last_name': user.last_name,
                    'contact_num': user.contact_num,
                    'email': user.email,
                    'type_name': user.type.type_name,
                    'level': user.level,
                    'section': user.section,
                    'strand': user.strand,
                }
                for user in users
            ]
        }
    )


def create_user_controller():
    request_data = request.get_json()

    new_user = Users(
        first_name=request_data["first_name"],
        middle_name=request_data["middle_name"],
        last_name=request_data["last_name"],
        contact_num=request_data["contact_num"],
        address=request_data["address"],
        email=request_data["email"],
        type_id=request_data["type_id"],
        level_id=request_data["level_id"],
        section_id=request_data["section_id"],
        strand_id=request_data["strand_id"],
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify(new_user.toDict()), 201


def update_user(user_id):
    request_form = request.form.to_dict()
    user = Users.query.get(user_id).toDict()

    user.first_name = request_form["first_name"]
    user.middle_name = request_form["middle_name"]
    user.last_name = request_form["last_name"]
    user.contact_num = request_form["contact_num"]
    user.address = request_form["address"]
    user.email = request_form["email"]
    user.type_id = request_form["type_id"]
    user.level_id = request_form["level_id"]
    user.section_id = request_form["section_id"]
    user.strand_id = request_form["strand_id"]

    db.session.commit()

    response = Users.query.get(user_id).toDict()
    return jsonify(response)


def delete_user(user_id):
    Users.query.filter_by(id=user_id).delete()
    db.session.commit()

    return ("Account with ID '{}' deleted succesfully!").format(user_id)
