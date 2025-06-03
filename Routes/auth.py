from flask import Blueprint, request
from DB_Manager import login_user,register_user
from wifi_scanner_service import permit_device,deny_device
from twilio.twiml.messaging_response import MessagingResponse

auth_bp = Blueprint("auth", __name__)
def send_message(message):

    bot_resp = MessagingResponse()
    msg = bot_resp.message()
    if message == "car not found":
        msg.body(
            "Oops I dont recognise the vehicle maybe you can get the car details for me and I'll try figure the car out for you?"
        )
    msg.body(message)
    return str(bot_resp)


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

@auth_bp.route("/whatsapp-response", methods=["POST"])
def whatsapp_response():
    """Handle WhatsApp responses for device authorization."""
    response_data = request.values.get('Body', '').lower()
    if not response_data:
        return {"error": "Invalid request"}, 400
    device_info = response_data.get("message", {}).get("body", "")
    global verify
    if device_info == "1":
        permit_device(verify[-1]['IP'], verify[-1]['MAC'])
        verify.pop()
    elif device_info == "2":
        deny_device(verify[-1]['IP'], verify[-1]['MAC'])
        verify.pop()
    return send_message("Thank you for your response")
    