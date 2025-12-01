import requests
import json

API_URL = "http://localhost:11434/api/chat"

payload = {
    "model": "llama3",
    "messages": [
        {"role": "user", "content": "Explain RAG in 3 bullet points."}
    ],
    "stream": False   # Set True if you want streaming
}

response = requests.post(API_URL, json=payload)

# Pretty print the JSON response
print(json.dumps(response.json(), indent=4))
