from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()



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