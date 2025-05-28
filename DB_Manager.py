from supabase import create_client, Client

SUPABASE_URL = ""
SUPABASE_KEY = "service-role-key"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def create_user(email, name):
    return supabase.table("users").insert({"email": email, "name": name}).execute()

def get_user_by_email(email):
    return supabase.table("users").select("*").eq("email", email).single().execute()

def update_user_name(user_id, new_name):
    return supabase.table("users").update({"name": new_name}).eq("id", user_id).execute()

def delete_user(user_id):
    return supabase.table("users").delete().eq("id", user_id).execute()

def get_all_users():
    return supabase.table("users").select("*").execute()

def log_incident(user_id, incident_type, description, source, severity):
    return supabase.table("incidents").insert({
        "user_id": user_id,
        "type": incident_type,
        "description": description,
        "source": source,
        "severity": severity
    }).execute()

def get_user_incidents(user_id):
    return supabase.table("incidents").select("*").eq("user_id", user_id).order("detected_at", desc=True).execute()

def resolve_incident(incident_id):
    return supabase.table("incidents").update({"resolved": True}).eq("id", incident_id).execute()

def delete_incident(incident_id):
    return supabase.table("incidents").delete().eq("id", incident_id).execute()

def get_all_incidents():
    return supabase.table("incidents").select("*").order("detected_at", desc=True).execute()

def add_recommendation(user_id, incident_id, message):
    return supabase.table("recommendations").insert({
        "user_id": user_id,
        "incident_id": incident_id,
        "message": message
    }).execute()

def get_user_recommendations(user_id):
    return supabase.table("recommendations").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
