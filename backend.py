from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv

load_dotenv()
checkpointer = MemorySaver()


class ChatState(TypedDict):
    message : Annotated[list[BaseMessage], add_messages]

llm = ChatOpenAI()

def chat_model(state : ChatState):
    message = state['message']
    response = llm.invoke(message)
    return {'message':[response]}

graph = StateGraph(ChatState)
graph.add_node('chat_node',chat_model)

graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

compiled_graph = graph.compile(checkpointer=checkpointer)