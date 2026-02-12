import streamlit as st
from auth_guard import require_login
from backend import compiled_graph
from langchain_core.messages import HumanMessage
import time

st.set_page_config(page_title="GPT Clone", layout="wide")
require_login()

st.title("GPT Clone")

# ---------- Sidebar ----------
with st.sidebar:
    st.header("⚙️ Settings")

    model_name = st.selectbox(
        "Model",
        ["gpt-4o-mini", "gpt-4o", "gpt-4.1"],
        index=0
    )

    temperature = st.slider(
        "Temperature", 0.0, 1.0, 0.7, 0.1
    )

st.session_state.setdefault("model_name", model_name)
st.session_state.setdefault("temperature", temperature)

# ---------- Chat state ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------- Chat history ----------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------- Chat input ----------
if prompt := st.chat_input("Ask anything ..."):
    # User message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    config = {
        "configurable": {
            "thread_id": st.session_state.user_id,
            "model": st.session_state.model_name,
            "temperature": st.session_state.temperature,
        }
    }

    # 🔹 Invoke model ONCE
    response = compiled_graph.invoke(
        {"message": HumanMessage(prompt)},
        config=config
    )

    answer = response["message"][-1].content

    # 🔹 Stream output
    with st.chat_message("assistant"):
        def stream_text(text: str):
            for line in text.split("\n"):
                yield line + "\n"
                time.sleep(0.05)

        st.write_stream(stream_text(answer))

    # 🔹 Save full answer
    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )
