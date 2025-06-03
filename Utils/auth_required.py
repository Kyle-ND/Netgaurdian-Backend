from functools import wraps
from flask import request, jsonify, g
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Set up Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # Only if you're verifying manually

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        token = auth_header.replace("Bearer ", "")

        try:
            # print("Verifying token:", token)  # Debugging line
            user = supabase.auth.get_user(token)
            if not user or not user.user:
                return jsonify({"error": "Invalid or expired token"}), 401
            # print("User authenticated:", user.user.id)  # Debugging line
            user_data = supabase.table("users").select("*").eq("id", user.user.id).single().execute()
            print("User data fetched:", user_data.data)  # Debugging line
            g.user = user_data.data
            return f(*args, **kwargs)

        except Exception as e:
            return jsonify({"error": str(e)}), 401

        
    return decorated_function
