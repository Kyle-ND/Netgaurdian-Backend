from flask import Blueprint,request,g
from Utils.auth_required import auth_required
from Chat_Bot_Service import generate
from DB_Manager import get_user_incidents

chatbot_bp = Blueprint("chatbot", __name__)

@chatbot_bp.route("/", methods=["POST"])
@auth_required
def chatbot_response():
    user = g.user
    if not user:
        return {"error": "Unauthorized"}, 401
    user_id = user["id"]
    user_message = request.json.get("message", "")
    if not user_message:
        return {"error": "Message cannot be empty"}, 400
    try:
        incidents = get_user_incidents(user_id)
        response = generate(user_message + "\n" + str(incidents.data))
        return {"response": response}, 200
    except Exception as e:
        return {"error": str(e)}, 500
