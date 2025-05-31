from flask import Blueprint
from Utils.auth_required import auth_required

chatbot_bp = Blueprint("chatbot", __name__)

@chatbot_bp.route("/", methods=["POST"])
@auth_required
def chatbot_response():
    pass
