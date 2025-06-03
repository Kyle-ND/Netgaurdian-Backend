from flask import Blueprint,g
from DB_Manager import get_all_incidents, get_user_incidents, log_incident, resolve_incident;
from flask import Blueprint, g, jsonify
from DB_Manager import get_user_incidents, log_incident, resolve_incident;
from Utils.auth_required import auth_required

incidents_bp = Blueprint("incidents", __name__)

@incidents_bp.route("/", methods=["GET"])
@auth_required
def get_user_incident():
    user = g.user
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    incidents = get_user_incidents(user["id"]).data

    return {"incidents": incidents}, 200
    

@incidents_bp.route("/resolve/<incident_id>", methods=["PUT"])
@auth_required
def resolve_incide(incident_id):
    user = g.user
    if not user:
        return {"error": "Unauthorized"}, 401
    
    result = resolve_incident(incident_id)
    if result.get("error"):
        return {"error": result["error"]}, 400
    
    return {"message": "Incident resolved successfully"}, 200