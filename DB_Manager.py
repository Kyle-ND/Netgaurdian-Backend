from supabase import create_client, Client,SupabaseAuthClient
from datetime import datetime
import jwt

SUPABASE_URL = "https://cncwdqumhxclbpfggifx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNuY3dkcXVtaHhjbGJwZmdnaWZ4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg0NjExMDYsImV4cCI6MjA2NDAzNzEwNn0.7mpT2aujpt28YTSCy9Ily-zBnu_AKh17GkGA-E7J8o8"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
db_password = "ymeAQUk8dUlv69n3"



def register_user(email, password, name=""):
    try:
        result = supabase.auth.sign_up({
            "email": email,
            "password": password
        })

        user = result.user
        if not user:
            return {"error": "Registration failed"}

        supabase.table("users").insert({
            "id": user.id,
            "email": email,
            "name": name,
            "role": "user"
        }).execute()

        return {
            "user": {
                "id": user.id,
                "email": email,
                "name": name,
                "role": "user"
            }
        }
    except Exception as e:
        return {"error": "An error occurred during registration: " + str(e)}



def login_user(email: str, password: str):
    try:
        # Authenticate using Supabase Auth
        result = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        user = result.user
        session = result.session

        if not user or not session:
            return {"error": "Invalid credentials"}

        # Fetch additional user data from your `users` table (optional)
        user_data = supabase.table("users").select("*").eq("id", user.id).single().execute()

        return {
            "token": session.access_token,
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user_data.data.get("name", ""),
                "role": user_data.data.get("role", "user")
            }
        }

    except Exception as e:
        return {"error": "An error occurred during login: " + str(e)}

def get_user_by_email(email):
    return supabase.table("users").select("*").eq("email", email).single().execute()


def update_user_name(user_id, new_name):
    return supabase.table("users").update({"name": new_name}).eq("id", user_id).execute()

def delete_user(user_id):
    return supabase.table("users").delete().eq("id", user_id).execute()

def get_all_users():
    result = supabase.table("users").select("*").execute()
    return [
        {
            "id": u["id"],
            "email": u["email"],
            "name": u.get("name", ""),
            "role": u.get("role", "user"),
            "createdAt": u.get("created_at")
        }
        for u in result.data
    ]

def log_incident(user_id, incident_type, description, source, severity, timestamp=None):
    print("Logging incident:")
    inserted = supabase.table("incidents").insert({
        "user_id": user_id,
        "type": incident_type,
        "description": description,
        "source": source,
        "severity": severity,
        "detected_at": timestamp or datetime.utcnow()
    }).execute()
    print(inserted.data[0])

    populate_single_incident(
        supabase_client=supabase,
        incident_type=incident_type,
        description=description,
        source=source,
        severity=severity,
        incident_id=inserted.data[0].get("id"),  # Let Supabase generate the ID
        detected_at=timestamp or datetime.now(),  # Use current UTC time if not provided
        resolved=False,  # Default to unresolved
        updated_at=None  # Let Supabase handle the updated_at timestamp
    )


    


def get_user_incidents(user_id):
    return supabase.table("incidents").select("*").eq("user_id", user_id).order("detected_at", desc=True).execute()

def resolve_incident(incident_id):
    return supabase.table("incidents").update({"resolved": True}).eq("id", incident_id).execute()

def delete_incident(incident_id):
    return supabase.table("incidents").delete().eq("id", incident_id).execute()

def get_all_incidents():
    return supabase.table("admin_incidents").select("*").order("detected_at", desc=True).execute()

def populate_single_incident(
    supabase_client: Client,
    incident_type: str,
    description: str,
    source: str,
    severity: int,
    incident_id, # Optional: User can provide an ID
    detected_at,  # Optional: defaults to current UTC time if None
    resolved,   # Optional: defaults to False
    updated_at,    # Optional: only set if you want to override default/trigger
):
    """
    Populates a single row in the 'admin_incidents' table in Supabase.
    Allows specifying an incident_id. If None, Supabase will generate it.

    Args:
        supabase_client: An initialized Supabase client instance.
        incident_type: The type or category of the incident.
        description: Detailed description of the incident.
        source: Where or how the incident was detected.
        severity: Numerical representation of the incident's severity.
        incident_id: Optional UUID for the incident.
        detected_at: Timestamp of when the incident was detected. Defaults to now (UTC).
        resolved: Boolean flag indicating if the incident is resolved. Defaults to False.
        updated_at: Timestamp of when the record was last updated. Defaults to None (Supabase trigger will handle).
    """

    incident_data = {
        'incident_id': incident_id,  # This will be None if not provided, allowing Supabase to auto-generate
        'type': incident_type,
        'description': description,
        'source': source,
        'severity': severity,
        'detected_at': detected_at, # Convert datetime to ISO 8601 string
        'resolved': resolved,

    }

    try:
        print(f"Attempting to insert a single incident: {incident_type} (ID: {incident_id or 'Auto-generated'})...")
        data, error = supabase_client.table('admin_incidents').insert(incident_data).execute()

        if error and error.message:
            print(f"Error inserting data: {error.message}")
            if hasattr(error, 'details'): print(f"Details: {error.details}")
            if hasattr(error, 'hint'): print(f"Hint: {error.hint}")
        elif data and len(data[1]) > 0:
            inserted_id = data[1][0].get('incident_id', 'N/A')
            print(f"Successfully inserted incident. ID: {inserted_id}")
            # print("Inserted data:", data[1]) # Uncomment to see the inserted record
        else:
            print("Insertion completed, but response format was unexpected or no error message provided.")
            print("Full response data:", data)
            print("Full error object:", error)

    except AttributeError as e:
        print("added incident")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

def add_recommendation(user_id, incident_id, message):
    return supabase.table("recommendations").insert({
        "user_id": user_id,
        "incident_id": incident_id,
        "message": message
    }).execute()

def get_user_recommendations(user_id):
    return supabase.table("recommendations").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()

def get_user_from_token(jwt_token):
    try:
        auth_client: SupabaseAuthClient = supabase.auth
        user = auth_client.get_user(jwt_token)
        return user
    except Exception as e:
        return {"error": str(e)}, 401




def decode_token(jwt_token, secret_key):
    try:
        payload = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])
        return payload  # contains `sub` (user ID), `exp`, etc.
    except jwt.ExpiredSignatureError:
        return {"error": "Token expired"}, 401
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}, 401
    

def map_severity(level: int) -> str:
    if level == 1:
        return "low"
    elif level in (2, 3):
        return "medium"
    elif level in (4, 5):
        return "high"
    return "unknown"
