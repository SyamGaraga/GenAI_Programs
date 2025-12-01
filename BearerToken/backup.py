import time
import requests

def get_with_retry(url: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            return resp
        except requests.exceptions.RequestException as exc:
            wait = 2 ** attempt  # 1s, 2s, 4s ...
            print(f"Attempt {attempt + 1} failed: {exc}")
            if attempt == max_retries - 1:
                raise
            print(f"Waiting {wait} seconds before retry...")
            time.sleep(wait)
