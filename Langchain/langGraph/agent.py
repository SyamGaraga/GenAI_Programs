from langchain.tools import tool
from typing import Dict

@tool
def get_exchange_rate(currency: str) -> str:
    "Get the INR exchange rate for a given currency (dummy implementation)."
    rates = {"USD": "83.2", "EUR": "90.1"}
    return rates.get(currency.upper(), "Rate not available.")

def rate_node(state: Dict) -> Dict:
    result = get_exchange_rate.invoke({"currency": "USD"})
    state["rate_info"] = result
    return state

# Actually call the function to see output
test_state = {}
result_state = rate_node(test_state)
print("Output:", result_state)