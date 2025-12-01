# -------------------------------------------------------------
# Import Flask and required modules
# -------------------------------------------------------------
from flask import Flask, request, jsonify

# -------------------------------------------------------------
# Create Flask app
# -------------------------------------------------------------
app = Flask(__name__)

# -------------------------------------------------------------
# GET Request Example
# -------------------------------------------------------------
@app.get("/get-example")
def get_example():
    return jsonify({
"status": "success",
"method": "GET",
"message": "This is a GET response"
})

# -------------------------------------------------------------
# GET with Query Parameters
# -------------------------------------------------------------
@app.get("/user")
def get_user():
    user_id = request.args.get("id")
    user_name = request.args.get("name")
    return jsonify({
"status": "success",
"method": "GET with Query Params",
"id": user_id,
"name": user_name
})

# -------------------------------------------------------------
# POST Request Example
# -------------------------------------------------------------
@app.post("/add-detailed-info")
def add_info():
    global user_profile
    data = request.get_json()
    
    # Store the received data into our global variable
    user_profile = data
    
    return jsonify({
        "status": "success",
        "message": "Personal information saved successfully!",
        "received_data": user_profile
    })

# -------------------------------------------------------------
# PUT Request Example
# -------------------------------------------------------------
@app.put("/update/<int:user_id>")
def update_user(user_id):
    update_data = request.get_json()
    return jsonify({
"status": "success",
"method": "PUT",
"user_id": user_id,
"updated_fields": update_data
})

# -------------------------------------------------------------
# DELETE Request Example
# -------------------------------------------------------------
@app.delete("/delete/<int:user_id>")
def delete_user(user_id):
    return jsonify({
"status": "success",
"method": "DELETE",
"deleted_user_id": user_id
})

# -------------------------------------------------------------
# Start Server
# -------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)