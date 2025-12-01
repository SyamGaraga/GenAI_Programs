import time, random
import requests

API_URL = "https://api.groq.com/openai/v1/chat/completions"
API_KEY = "enter_your_api_key_here"  # Replace with your actual API key

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def call_llama3_groq(payload, max_retries=5):
    delay = 1  # base backoff in seconds

    for attempt in range(1, max_retries + 1):
        try:
            r = requests.post(API_URL, json=payload, headers=headers, timeout=30)

            # Success
            if 200 <= r.status_code < 300:
                return r.json()

            # Retryable transient errors
            if r.status_code in (429, 500, 502, 503, 504):
                print(f"Attempt {attempt} failed with status: {r.status_code}")
                retry_after = r.headers.get("Retry-After")
                if retry_after:
                    sleep_for = float(retry_after)
                else:
                    sleep_for = delay + random.uniform(0, 0.5)
                    delay *= 2
            else:
                r.raise_for_status()

        except requests.exceptions.RequestException as e:
            print(f"Network error on attempt {attempt}: {e}")
            sleep_for = delay + random.uniform(0, 0.5)
            delay *= 2

        if attempt == max_retries:
            raise RuntimeError("Groq Llama 3 API still failing after retries.")

        print(f"Waiting {sleep_for:.2f} seconds before retry...")
        time.sleep(sleep_for)

# Conversation messages
messages = []

print("Start chatting with Llama 3 (type 'exit' to quit)")

while True:
    user_input = input("You: ")
    if user_input.lower() in ("exit", "quit"):
        break

    # Add user message to conversation
    messages.append({"role": "user", "content": user_input})

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": messages,
        "temperature": 0.7
    }

    response = call_llama3_groq(payload)
    assistant_msg = response["choices"][0]["message"]["content"]

    # Add assistant response to conversation
    messages.append({"role": "assistant", "content": assistant_msg})

    print(f"Llama 3: {assistant_msg}")