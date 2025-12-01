import streamlit as st
import requests
import json

st.set_page_config(page_title="HF Chatbot", page_icon="🤖")

st.title("🤖 HuggingFace Chatbot (Llama 3.2 1B Instruct)")

# User inputs HF API key
api_key = st.text_input("enter_the_key", type="password")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display previous messages
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# HF API call function (NEW WORKING ENDPOINT)
def call_huggingface_chat(prompt):
    url = "https://router.huggingface.co/hf-inference/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "meta-llama/Llama-3.2-1B-Instruct",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"⚠️ API Error: {str(e)}"


# Chat input box
user_input = st.chat_input("Type your message...")

if user_input:
    # Add user message
    st.session_state["messages"].append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    # Get bot response
    bot_reply = call_huggingface_chat(user_input)

    # Add assistant response
    st.session_state["messages"].append({"role": "assistant", "content": bot_reply})

    with st.chat_message("assistant"):
        st.write(bot_reply)
