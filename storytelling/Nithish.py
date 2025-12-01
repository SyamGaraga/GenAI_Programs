import os
import json
import time
from flask import Flask, render_template, request, jsonify
import requests

# --- IMPORTANT: Configuration ---
# In a real environment, the API key MUST be loaded from environment variables 
# for security. DO NOT hardcode it here in production.
# I am setting a placeholder here, but you would replace this with:
# GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") 
# and ensure you set the environment variable when running the app.
GEMINI_API_KEY = "enter_your_secure_api_key_here" 
MODEL = 'gemini-2.5-flash-preview-09-2025'
BASE_API_URL = f'https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={GEMINI_API_KEY}'

app = Flask(__name__)

# --- Utility Function (Backend Logic) ---

def fetch_with_backoff(payload, max_retries=5, delay=1.0):
    """Core utility for making API calls with exponential backoff."""
    headers = {'Content-Type': 'application/json'}

    for i in range(max_retries):
        try:
            response = requests.post(
                BASE_API_URL,
                headers=headers,
                data=json.dumps(payload)
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            if response.status_code in [429, 500, 503] and i < max_retries - 1:
                print(f"Attempt {i + 1} failed with status {response.status_code}. Retrying in {delay}s.")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
                continue
            raise e
        except requests.exceptions.RequestException as e:
            if i < max_retries - 1:
                print(f"Attempt {i + 1} failed (Request Error: {e}). Retrying in {delay}s.")
                time.sleep(delay)
                delay *= 2
                continue
            raise e

# --- Flask Routes ---

@app.route('/')
def index():
    """Renders the main HTML template."""
    return render_template('index.html')

@app.route('/generate_story', methods=['POST'])
def generate_story_endpoint():
    """
    Handles the request from the frontend, calls the Gemini API, 
    and returns the result as JSON.
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_SECURE_API_KEY_HERE":
        return jsonify({
            "error": "API Key not configured. Please set the GEMINI_API_KEY environment variable in app.py."
        }), 500

    try:
        # 1. Get user prompt from frontend request
        data = request.get_json()
        user_prompt = data.get('prompt', '').strip()

        if not user_prompt:
            return jsonify({"error": "Prompt cannot be empty."}), 400

        # 2. Define the System Instruction (Business Logic)
        system_prompt = "You are a professional, highly creative AI story writer. Your response must be the complete story, written in an engaging narrative style. Do not include any titles, headers, or conversational text outside of the story itself."

        # 3. Construct the Payload
        payload = {
            "contents": [{"parts": [{"text": user_prompt}]}],
            "systemInstruction": {"parts": [{"text": system_prompt}]},
        }

        # 4. Call the Gemini API using the secure backend utility
        result = fetch_with_backoff(payload)
        
        # 5. Extract and Return Result
        try:
            story = result['candidates'][0]['content']['parts'][0]['text']
            return jsonify({"story": story})
        except (KeyError, IndexError):
            return jsonify({
                "error": "The AI service returned an empty or malformed response."
            }), 500

    except requests.exceptions.RequestException as e:
        print(f"Flask backend request failed: {e}")
        return jsonify({
            "error": f"Backend communication error with Gemini API: {e}"
        }), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({
            "error": f"An unexpected error occurred on the server."
        }), 500

if __name__ == '__main__':
    # Run the server in debug mode for development
    app.run(debug=True, port=5000)