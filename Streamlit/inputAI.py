import streamlit as st

st.title("Simple AI Prompt Console")

prompt = st.text_input("Enter your prompt for the AI model")

if st.button("Send to AI"):
    st.write("You entered:")
    st.write(prompt)