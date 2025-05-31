from flask import Blueprint
from Utils.auth_required import auth_required

users_bp = Blueprint("users", __name__)

@users_bp.route("/", methods=["GET"])
@auth_required
def get_all_users():
    pass
