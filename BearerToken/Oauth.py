import requests

# Paste the access token you got from OAuth Playground
ACCESS_TOKEN = "enter_your_access_token_here"

url = "https://www.googleapis.com/drive/v3/files"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

params = {
    "pageSize": 20,          # Number of files to list
    "fields": "files(id, name, mimeType)"  # Info you want
}

response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    print("Files in your Google Drive:")
    for f in response.json().get("files", []):
        print(f"{f['name']} ({f['id']}) - {f['mimeType']}")
else:
    print("Error:", response.text)