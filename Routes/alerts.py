from flask import Blueprint, request
from app.utils.auth_required import auth_required

alerts_bp = Blueprint("alerts", __name__)

@alerts_bp.route("/config", methods=["PUT"])
@auth_required
def update_alert_config():
    pass

@alerts_bp.route("/config", methods=["GET"])
@auth_required
def get_alert_config():
    pass
