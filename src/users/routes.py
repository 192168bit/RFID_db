from flask import request

from ..app import app
from .controllers import list_all_users_controller, create_user_controller, get_user_profile, update_user, delete_user

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
        return get_user_profile(user_id)
    if request.method == "PUT":
        return update_user(user_id)
    if request.method == "DELETE":
        return delete_user(user_id)
    else:
        return "Method is Not Allowed"