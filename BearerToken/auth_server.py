from datetime import datetime, timedelta
import jwt
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

# Secret key used to sign our JWT tokens.
# In real systems this MUST be stored securely (env variable, key vault, etc.)
SECRET_KEY = "MY_SUPER_SECRET_KEY_FOR_DEMO_ONLY"


@app.route("/")
def serve_auth_page():
    # Serve the auth.html file as the home page.
    return send_from_directory(".", "auth.html")


@app.route("/create-token", methods=["POST"])
def create_token():
    # Validate username/password and create a JWT bearer token.
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    # 1. Very simple hard-coded check (for demo)
    if username != "admin" or password != "secret":
        return jsonify({"error": "Invalid credentials"}), 401

    # 2. Build token payload (claims)
    payload = {
        "sub": username,                           # subject (who the token represents)
        "role": "demo-user",                       # custom claim
        "exp": datetime.utcnow() + timedelta(minutes=15),  # expiry time (15 min)
        "iat": datetime.utcnow()                   # issued-at time
    }

    # 3. Create signed JWT using HS256 algorithm
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    # 4. Return JSON with token
    return jsonify({
        "access_token": token,
        "token_type": "bearer",
        "expires_in_minutes": 15
    })


if __name__ == "__main__":
    # Run Auth Server on port 5000
    app.run(host="127.0.0.1", port=5000, debug=True)