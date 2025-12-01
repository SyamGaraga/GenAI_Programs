import streamlit as st

st.title("Simple Calculator")

num1 = st.number_input("Enter first number:")
num2 = st.number_input("Enter second number:")

operation = st.selectbox("Choose operation", ["Add", "Subtract", "Multiply", "Divide"])

if st.button("Calculate"):
    if operation == "Add":
        st.success(num1 + num2)
    elif operation == "Subtract":
        st.success(num1 - num2)
    elif operation == "Multiply":
        st.success(num1 * num2)
    elif operation == "Divide":
        st.success(num1 / num2 if num2 != 0 else "Cannot divide by zero")
