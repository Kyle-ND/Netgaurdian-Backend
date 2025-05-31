from flask import Blueprint,g
from Utils.auth_required import auth_required
from DB_Manager import get_all_users

users_bp = Blueprint("users", __name__)

@users_bp.route("/", methods=["GET"])
@auth_required
def get_all():
    auth_user = g.user
    if auth_user is None or auth_user.get("role") != "admin":
        return {"error": "Unauthorized"}, 401
    users = get_all_users()
    if "error" in users:
        return {"error": users["error"]}, 400
    return {"users": users}, 200
    
    
