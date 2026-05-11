
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    This defines the memory payload that gets passed between our agents.
    Every node in our graph will receive this State, read from it, and return updates to it.
    """
    # The list of messages (chat history). 
    # `add_messages` tells LangGraph to APPEND new messages, not overwrite the list.
    messages: Annotated[Sequence[BaseMessage], add_messages]
    
    # Keeps track of which agent is currently speaking/working.
    sender: str