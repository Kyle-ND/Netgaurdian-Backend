from flask import Blueprint
from DB_Manager import get_user_incidents, log_incident, resolve_incident;
from Utils.auth_required import auth_required

incidents_bp = Blueprint("incidents", __name__)

@incidents_bp.route("/", methods=["GET"])
@auth_required
def get_user_incidents():
    user = auth_required()
    if not user:
        return {"error": "Unauthorized"}, 401
    
    incidents = get_user_incidents(user["id"])
    return {"incidents": incidents}, 200
    

@incidents_bp.route("/resolve/<incident_id>", methods=["PUT"])
@auth_required
def resolve_incident(incident_id):
    user = auth_required()
    if not user:
        return {"error": "Unauthorized"}, 401
    
    result = resolve_incident(incident_id)
    if result.get("error"):
        return {"error": result["error"]}, 400
    
    return {"message": "Incident resolved successfully"}, 200
