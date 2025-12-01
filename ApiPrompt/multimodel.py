import requests
import os

# 1. SETUP: Put your API key here
# (Get one from https://platform.openai.com/api-keys)
api_key = "enter_your_openai_api_key_here" 

endpoint = "https://api.openai.com/v1/chat/completions"

# 2. YOUR PAYLOAD (Updated)
payload = {
  "model": "gpt-4o",  # CHANGED: Use a valid model name
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "Summarise the key problems in this dashboard."},
        {
          "type": "image_url",
          # CHANGED: Using a real sample image for testing. 
          # Replace this with your actual dashboard URL later.
          "image_url": {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"}
        }
      ]
    }
  ],
  "max_tokens": 300 # Added to prevent the response from cutting off
}

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# 3. EXECUTE
try:
    response = requests.post(endpoint, headers=headers, json=payload)
    response.raise_for_status() # Check for HTTP errors
    
    # 4. PRINT RESULT
    result = response.json()
    print(result['choices'][0]['message']['content'])
    
except Exception as e:
    print(f"Error: {e}")
    print(response.text)