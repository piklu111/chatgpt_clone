import streamlit as st
from auth import authenticate

st.set_page_config(page_title="My App")

# ---------- Session defaults ----------
st.session_state.setdefault("step", "choice")
st.session_state.setdefault("logged_in", False)

# ---------- Already authenticated ----------
if st.session_state.logged_in or "openai_api_key" in st.session_state:
    st.switch_page("pages/_chatbot.py")

st.title("Welcome 👋")

# =========================================================
# STEP 1 — Ask if user has API key
# =========================================================
if st.session_state.step == "choice":
    st.subheader("Do you have your own OpenAI API key?")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Yes, I have one"):
            st.session_state.step = "byok"
            st.rerun()

    with col2:
        if st.button("❌ No, login instead"):
            st.session_state.step = "login"
            st.rerun()

# =========================================================
# STEP 2 — BYOK FLOW
# =========================================================
elif st.session_state.step == "byok":
    st.subheader("🔑 Enter your API key")

    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        placeholder="sk-..."
    )

    model = st.selectbox(
        "Model",
        ["gpt-4o-mini", "gpt-4o", "gpt-4.1"]
    )

    temperature = st.slider(
        "Temperature", 0.0, 1.0, 0.7, 0.1
    )

    if st.button("Continue to Chat"):
        if not api_key:
            st.error("API key is required")
        else:
            st.session_state.openai_api_key = api_key
            st.session_state.model_name = model
            st.session_state.temperature = temperature
            st.switch_page("pages/_chatbot_without_api_key.py")

    if st.button("⬅ Back"):
        st.session_state.step = "choice"
        st.rerun()

# =========================================================
# STEP 3 — LOGIN FLOW
# =========================================================
elif st.session_state.step == "login":
    st.subheader("🔐 Login")

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

    if st.button("⬅ Back"):
        st.session_state.step = "choice"
        st.rerun()
