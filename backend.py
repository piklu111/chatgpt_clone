from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
import streamlit as st

conn = sqlite3.connect('chatbot.db', check_same_thread= False)

checkpointer = SqliteSaver(conn = conn)



class ChatState(TypedDict):
    message : Annotated[list[BaseMessage],add_messages]

def create_graph(api_key,model_name,temp):
    llm =ChatOpenAI(model=model_name,api_key=api_key,temperature=temp, streaming=True)
    
    def chat_model(state : ChatState):
        message = state['message']
        response = llm.invoke(message)
        return {'message':response.content}

    graph = StateGraph(ChatState)
    graph.add_node('chat_node',chat_model)
    graph.add_edge(START, 'chat_node')
    graph.add_edge('chat_node', END)

    return graph.compile(checkpointer= checkpointer)

def get_thread_id(user_id):
    checkpoint_lst = []
    for checkpoint in checkpointer.list(None):
        print('checkpoint', checkpoint)
        user_id = checkpoint.metadata['user_id']
        print('user_id', user_id)
        if user_id == st.session_state.user_id:
            thread_id = checkpoint.config['configurable']['thread_id']
            if thread_id not in checkpoint_lst:
                checkpoint_lst.append(thread_id)
    return checkpoint_lst

def delete_thread(thread_id: str):
    with conn:
        conn.execute("DELETE FROM checkpoints WHERE thread_id = ?", (thread_id,))
        conn.execute("DELETE FROM writes WHERE thread_id = ?", (thread_id,))