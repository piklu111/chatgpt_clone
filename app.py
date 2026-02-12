import streamlit as st
from auth import authenticate

st.set_page_config("My App")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    st.switch_page("pages/_chatbot.py")

st.title("Login")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    user_id = authenticate(username, password)
    if user_id:
        st.session_state.logged_in = True
        st.session_state.user_id = user_id
        st.switch_page("pages/_chatbot.py")
    else:
        st.error("Invalid credentials")
