# server/decorators.py
from functools import wraps
from flask import request, jsonify
from server.auth import decode_token

def jwt_required(role=None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return jsonify({"error": "Missing token"}), 401
            token = auth_header.split(" ")[1]
            payload = decode_token(token)
            if not payload:
                return jsonify({"error": "Invalid or expired token"}), 401
            if role and payload.get("role") != role:
                return jsonify({"error": "Forbidden"}), 403
            # Pass payload to endpoint if needed
            return fn(*args, **kwargs, user=payload)
        return wrapper
    return decorator
