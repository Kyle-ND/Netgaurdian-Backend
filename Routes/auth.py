from flask import Blueprint, request
from DB_Manager import login_user,register_user

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():

    user_request = request.get_json()
    if not user_request:
        return {"error": "Invalid request"}, 400
    email = user_request.get("email")
    password = user_request.get("password")
    if not email or not password:
        return {"error": "Email and password are none values"}, 400
    else:
        user = login_user(email, password)
        
        if "error" in user:
            return {"error":user["error"],
                "message": "Invalid email or password"}, 401 
        else:
            return {"message": "Login successful", "user": user}, 200
    

@auth_bp.route("/register", methods=["POST"])
def register():
    
    user_request = request.get_json()

    if not user_request:
        return {"error": "Invalid request"}, 400
    email = user_request.get("email")
    password = user_request.get("password")
    name = user_request.get("name", "")
    if not email or not password or name =="":
        return {"error": "Email,password or name are none values please check request body and try again"}, 400
    else:
        user = register_user(email, password, name)
        if "error" in user:
            return user, 400
        else:
            return {"message": "Registration successful", "user": user}, 200

