import streamlit as st

st.title("Widgets Example")

gender = st.radio("Select your gender", ["Male", "Female", "Other"])
hobbies = st.multiselect("Select your hobbies", ["Reading", "Music", "Sports"])
subscribe = st.checkbox("Subscribe to newsletter")

st.write("Gender:", gender)
st.write("Hobbies:", hobbies)
st.write("Subscribed:", subscribe)
