from functools import wraps
from flask import request, jsonify, g
from supabase import create_client
import os
import jwt
import requests
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


# Set up Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")  # Only if you're verifying manually

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        token = auth_header.replace("Bearer ", "")

        try:
            # ✅ OPTION 1: Verify using Supabase SDK
            user = supabase.auth.get_user(token)
            if not user or not user.user:
                return jsonify({"error": "Invalid or expired token"}), 401

            # Optional: fetch user metadata from your own users table
            user_data = supabase.table("users").select("*").eq("id", user.user.id).single().execute()
            g.user = user_data.data  # Flask global variable

        except Exception as e:
            return jsonify({"error": str(e)}), 401

        return f(*args, **kwargs)
    return decorated_function
