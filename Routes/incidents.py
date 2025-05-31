from flask import Blueprint
from Utils.auth_required import auth_required

incidents_bp = Blueprint("incidents", __name__)

@incidents_bp.route("/", methods=["GET"])
@auth_required
def get_user_incidents():
    pass

@incidents_bp.route("/", methods=["POST"])
@auth_required
def log_incident():
    pass

@incidents_bp.route("/resolve/<incident_id>", methods=["PUT"])
@auth_required
def resolve_incident(incident_id):
    pass
