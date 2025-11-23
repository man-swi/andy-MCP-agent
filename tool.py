from typing import Literal
from typing_extensions import TypedDict, Annotated


from typing import Optional
from pydantic import BaseModel, Field, constr
import json

from typing import Annotated

from langgraph.types import Command 
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage


from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

import asyncio 
from prompt import prompt

from dotenv import load_dotenv
load_dotenv()

from langchain.chat_models import init_chat_model

model = init_chat_model("devstral-medium-2507", model_provider="mistralai")

async def get_agent():
    client = MultiServerMCPClient({
        "calendar_server": {
            "command": "python",
            "args": [r"D:\Lessons\MCP-2\Investor-Relations-Market-Intelligence\All_Servers\calendar_tool.py"],
            "transport": "stdio"
        },

        
        "gmail_tool": {

            "command": "python",
            "args": [r"D:\Lessons\MCP-2\Investor-Relations-Market-Intelligence\All_Servers\gmail_tool_5.py"],
            "transport": "stdio"
        },
        })


    memory = MemorySaver()

    # tools = client.get_tools()
    tools = await client.get_tools()

    return tools



