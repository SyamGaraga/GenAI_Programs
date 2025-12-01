import time, random, requests

API_URL = "https://api.example-ai.com/v1/chat"

def call_genai_api(payload, max_retries=5):
    delay = 1  # seconds
    for attempt in range(1, max_retries + 1):
        try:
            r = requests.post(API_URL, json=payload, timeout=30)

            if 200 <= r.status_code < 300:
                return r.json()

            if r.status_code not in (429, 500, 502, 503, 504):
                # non‑retryable error
                r.raise_for_status()

            print(f"Attempt {attempt} failed with {r.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Network error on attempt {attempt}: {e}")

        if attempt == max_retries:
            raise RuntimeError("API still failing after retries.")

        sleep_for = delay + random.uniform(0, 0.5)
        print(f"Waiting {sleep_for:.2f} seconds...")
        time.sleep(sleep_for)
        delay *= 2

payload = {"messages":[{"role":"user","content":"Hello, AI!"}]}
response = call_genai_api(payload)
print(response)