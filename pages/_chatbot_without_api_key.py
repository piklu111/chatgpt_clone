import streamlit as st
import time
import uuid

from langchain_core.messages import HumanMessage, BaseMessage
from backend import create_graph, get_thread_id, delete_thread

if (
    "login_method" not in st.session_state
    or st.session_state.login_method != "byok"
):
    st.warning("Unauthorized access")
    st.switch_page("app.py")
    st.stop()

# ---------------------------------------------------
# Page Config (MUST be first Streamlit command)
# ---------------------------------------------------
st.set_page_config(page_title="GPT Clone", layout="wide")

st.title("GPT Clone")


# ---------------------------------------------------
# Session State Init
# ---------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "conv_id" not in st.session_state:
    id = str(uuid.uuid4())
    st.session_state.conv_id = {'conv_lst' : [id, *get_thread_id(st.session_state.user_id)],'curr_conv':id}

if "model_name" not in st.session_state:
    st.session_state.model_name = "gpt-4o-mini"

if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7

@st.cache_resource
def get_graph(api_key, model, temp):
    return create_graph(api_key, model, temp)

chat_state = get_graph(
    st.session_state.openai_api_key,
    st.session_state.model_name,
    st.session_state.temperature
)
def handle_click(thread_id):
    st.session_state.conv_id['curr_conv'] = thread_id
    config = {
        "configurable": {
            "user_id": st.session_state.user_id,
            "thread_id": thread_id
        }
    }
    print('config',config)
    state = chat_state.get_state(config)
    print('state',state)

    if not state:
        return

    messages = state.values.get("message", [])
    print('messages',messages)
    st.session_state.messages = []

    for m in messages:
        if isinstance(m, HumanMessage):
            role = "user"
        else:
            role = "assistant"

        st.session_state.messages.append(
            {
                "conv_id": thread_id,
                "role": role,
                "content": m.content,
            }
        )

def new_chat():
    id = str(uuid.uuid4())
    st.session_state.conv_id['conv_lst'].append(id)
    st.session_state.conv_id['curr_conv'] = id
    st.session_state.messages = []

def delete_thread_memory(thread_id):
    delete_thread(thread_id)
    # user_id = st.session_state.user_id

    # # Build the config key format used internally
    # config = {
    #     "configurable": {
    #         "user_id": user_id,
    #         "thread_id": thread_id
    #     }
    # }

    # # Access internal storage
    # storage = chat_state.checkpointer.storage

    # # Build the exact key
    # key = tuple(sorted(config["configurable"].items()))

    # if key in storage:
    #     del storage[key]

def delete_conversation(thread_id):
    if len(st.session_state.conv_id['conv_lst']) > 1:
        index = st.session_state.conv_id['conv_lst'].index(thread_id)
        st.session_state.conv_id['conv_lst'].pop(index)
        index = index if 0 <= index < len(st.session_state.conv_id['conv_lst']) else index -1
        st.session_state.conv_id['curr_conv'] = st.session_state.conv_id['conv_lst'][index]
        config = {"configurable":{"user_id": st.session_state.user_id,"thread_id": st.session_state.conv_id['curr_conv']}}
        state = chat_state.get_state(config)
        print('state',state)

        if not state:
            return

        messages = state.values.get("message", [])
        print('messages',messages)
        st.session_state.messages = []

        for m in messages:
            if isinstance(m, HumanMessage):
                role = "user"
            else:
                role = "assistant"

            st.session_state.messages.append(
                {
                    "conv_id": thread_id,
                    "role": role,
                    "content": m.content,
                }
            )
    else :
        st.session_state.conv_id['conv_lst'].remove(thread_id)
        id = str(uuid.uuid4())
        st.session_state.conv_id['conv_lst'].append(id)
        st.session_state.conv_id['curr_conv'] = id
        st.session_state.messages = []
             
    delete_thread_memory(thread_id)


# ---------------------------------------------------
# Sidebar Settings
# ---------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")

    st.session_state.model_name = st.selectbox(
        "Model",
        ["gpt-4o-mini", "gpt-4o", "gpt-4.1"],
        index=0
    )

    st.session_state.temperature = st.slider(
        "Temperature", 0.0, 1.0, 0.7, 0.1
    )

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("💬History..")
    with col2:
        st.button('New Chat', on_click= new_chat)

    if st.session_state.conv_id['conv_lst']:
        # print(st.session_state.messages)
        for id in reversed(st.session_state.conv_id['conv_lst']):
            col1, col2 = st.columns([4,1])
            with col1:
                label = "👉 " + id if id == st.session_state.conv_id['curr_conv'] else id
                st.button(
                    label,
                    on_click=handle_click,
                    args=(id,))
            with col2:
                st.button("❌",key=f"delete_{id}",on_click= delete_conversation, args=(id,))
            


# ---------------------------------------------------
# Render Existing Messages
# ---------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ---------------------------------------------------
# Chat Input
# ---------------------------------------------------
if prompt := st.chat_input("Ask anything..."):

    # Show user message immediately
    with st.chat_message("user"):
        st.markdown(prompt)

    # Save user message
    st.session_state.messages.append(
        {
            "conv_id": st.session_state.conv_id['curr_conv'],
            "role": "user", 
            "content": prompt,
        }
    )

    config = {
        "configurable": {
            "user_id":st.session_state.user_id,
            "thread_id": st.session_state.conv_id['curr_conv']
        }
    }
    # print('thread_id from chat window',config)

    # # Invoke LangGraph
    # response = chat_state.invoke(
    #     {"message": [HumanMessage(content=prompt)]},
    #     config=config,
    # )

    # answer = response["message"][-1].content

    # Stream assistant output
    with st.chat_message("assistant"):

        # def stream_text(text):
        #     for chunk in text.split(" "):
        #         yield chunk + " "
        #         time.sleep(0.02)

        # st.write_stream(stream_text(answer))
        
        placeholder =st.empty()
        full_response = ""

        for chunk, metadata in chat_state.stream(
            {"message": [HumanMessage(content=prompt)]},
            config=config,
            stream_mode="messages"
        ):
            if chunk.content:
                full_response += chunk.content
                placeholder.markdown(full_response)

    # Save assistant message
    st.session_state.messages.append(
        {
            "conv_id": st.session_state.conv_id,
            "role": "assistant",
            "content": full_response,
        }
    )
    st.rerun()
