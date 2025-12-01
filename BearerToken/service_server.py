import jwt
from jwt import InvalidTokenError, ExpiredSignatureError
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

# Same secret as auth_server.py (shared between both services)
SECRET_KEY = "MY_SUPER_SECRET_KEY_FOR_DEMO_ONLY"


@app.route("/")
def serve_service_page():
    # Serve the service.html file as the home page.
    return send_from_directory(".", "service.html")


def verify_token(auth_header: str):
    # Extract token from 'Authorization: Bearer <token>' and verify it.
    if not auth_header:
        return None, "Missing Authorization header"

    if not auth_header.startswith("Bearer "):
        return None, "Invalid header format. Use 'Bearer <token>'."

    token = auth_header.split(" ", 1)[1].strip()

    try:
        # Decode and verify signature + expiry
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload, None
    except ExpiredSignatureError:
        return None, "Token has expired"
    except InvalidTokenError:
        return None, "Token is invalid"


@app.route("/api/secret", methods=["GET"])
def secret_api():
    # Protected endpoint that requires a valid bearer token.
    auth_header = request.headers.get("Authorization")
    payload, error = verify_token(auth_header)

    if error is not None:
        return jsonify({"error": error}), 401

    # If token is valid, we can access claims like payload["sub"]
    username = payload.get("sub", "unknown")

    return jsonify({
        "message": "This is protected data only for authenticated users.",
        "user": username,
        "role": payload.get("role"),
    })


if __name__ == "__main__":
    # Run Service Server on port 5001
    app.run(host="127.0.0.1", port=5001, debug=True)