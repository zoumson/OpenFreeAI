# server/auth.py
import jwt
import datetime
from flask import request, jsonify, current_app
from werkzeug.security import check_password_hash, generate_password_hash

SECRET_KEY = "replace_with_your_secret_key"

# Simple in-memory user store
USERS = {
    "admin": {"password": generate_password_hash("adminpass"), "role": "admin"},
    "user": {"password": generate_password_hash("userpass"), "role": "user"}
}

def create_token(username):
    payload = {
        "username": username,
        "role": USERS[username]["role"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def decode_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# ---------------------------
# Login endpoint
# ---------------------------
from flask import Blueprint

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    user = USERS.get(username)
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid credentials"}), 401
    token = create_token(username)
    return jsonify({"access_token": token})
