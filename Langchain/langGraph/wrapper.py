import time
from typing import Callable, Dict

# 1. The Retry Logic (with added print statements to visualize retries)
def with_retry(node_fn: Callable, retries: int = 3, delay: float = 1.0):
    def wrapper(state: Dict) -> Dict:
        last_exc = None
        for i in range(retries):
            try:
                print(f"Attempting execution (Try {i+1}/{retries})...")
                return node_fn(state)
            except Exception as e:
                print(f"   -> Failed with error: {e}")
                last_exc = e
                time.sleep(delay)
        
        # if all retries fail, add error info to state
        print("All retries exhausted.")
        state["error"] = str(last_exc)
        return state
    return wrapper

# 2. A node designed to ALWAYS fail
def answer_node(state: Dict) -> Dict:
    # This simulates a crash, like a broken API connection
    raise ValueError("Simulated API Connection Error")

# 3. Run it
safe_answer_node = with_retry(answer_node, retries=3, delay=0.5)

current_state = {"user_input": "Test input"}
result = safe_answer_node(current_state)

print("-" * 30)
print("Final State:", result)