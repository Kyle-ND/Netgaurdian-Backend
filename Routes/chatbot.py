from flask import Blueprint,request
from Utils.auth_required import auth_required
from Chat_Bot_Service import generate

chatbot_bp = Blueprint("chatbot", __name__)

@chatbot_bp.route("/", methods=["POST"])
@auth_required
def chatbot_response():
    user = auth_required()
    if not user:
        return {"error": "Unauthorized"}, 401
    user_id = user["id"]
    user_message = request.json.get("message", "")
    if not user_message:
        return {"error": "Message cannot be empty"}, 400
    try:
        response = generate(user_message)
        return {"response": response}, 200
    except Exception as e:
        return {"error": str(e)}, 500
