from flask import Blueprint, request

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    # Validate and authenticate user
    pass

@auth_bp.route("/register", methods=["POST"])
def register():
    # Register user with Supabase Auth + DB
    pass
