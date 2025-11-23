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
import os
import sys
import traceback
import shutil
from prompt import prompt

from dotenv import load_dotenv
load_dotenv()

from langchain.chat_models import init_chat_model

model = init_chat_model("mistral-large-2411", model_provider="mistralai")
memory = MemorySaver()

# Global cache for agent and client
_agent_cache = None
_client_cache = None

# MCP server paths - use local files in the workspace
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CALENDAR_SERVER_PATH = os.path.join(_BASE_DIR, "All_Servers", "calendar_tool.py")
GMAIL_SERVER_PATH = os.path.join(_BASE_DIR, "All_Servers", "gmail_tool_5.py")


def _get_python_command():
    """Get the Python command to use for subprocess"""
    # Use the same Python interpreter that's running this script
    python_exe = sys.executable
    if python_exe:
        return python_exe
    # Fallback to 'python' or 'python3'
    if shutil.which("python"):
        return "python"
    elif shutil.which("python3"):
        return "python3"
    else:
        return "python"  # Default fallback


def _validate_server_paths():
    """Validate that MCP server scripts exist"""
    errors = []
    if not os.path.exists(CALENDAR_SERVER_PATH):
        errors.append(f"Calendar server not found: {CALENDAR_SERVER_PATH}")
    if not os.path.exists(GMAIL_SERVER_PATH):
        errors.append(f"Gmail server not found: {GMAIL_SERVER_PATH}")
    return errors


async def get_agent():
    global _agent_cache, _client_cache
    
    # Return cached agent if it exists
    if _agent_cache is not None:
        return _agent_cache
    
    # Validate server paths first
    path_errors = _validate_server_paths()
    if path_errors:
        error_msg = "MCP server path validation failed:\n" + "\n".join(path_errors)
        raise Exception(error_msg)
    
    try:
        # Get Python command
        python_cmd = _get_python_command()
        
        # Create MCP client
        client = MultiServerMCPClient({
            "calendar_server": {
                "command": python_cmd,
                "args": [CALENDAR_SERVER_PATH],
                "transport": "stdio"
            },
            "gmail_tool": {
                "command": python_cmd,
                "args": [GMAIL_SERVER_PATH],
                "transport": "stdio"
            },
        })
        
        # Cache the client
        _client_cache = client
        
        # Get tools from MCP servers
        tools = await client.get_tools()
        
        # Create agent
        agent = create_react_agent(
            model=model,
            tools=tools,
            checkpointer=memory,
            name="MCP-Agent",
            prompt=prompt,
        )
        
        # Cache the agent
        _agent_cache = agent
        
        return agent
        
    except BaseExceptionGroup as eg:
        # Handle BaseExceptionGroup to extract the actual exception
        error_messages = []
        for i, exc in enumerate(eg.exceptions):
            exc_type = type(exc).__name__
            exc_msg = str(exc)
            exc_tb = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            error_messages.append(f"Exception {i+1} ({exc_type}): {exc_msg}\nTraceback:\n{exc_tb}")
        
        error_msg = f"Failed to initialize MCP agent (ExceptionGroup with {len(eg.exceptions)} sub-exception(s)):\n\n" + "\n\n---\n\n".join(error_messages)
        # Clear cache on error so we can retry
        _agent_cache = None
        _client_cache = None
        raise Exception(error_msg) from eg
    except Exception as e:
        # Clear cache on error so we can retry
        _agent_cache = None
        _client_cache = None
        exc_tb = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        error_msg = f"Failed to initialize MCP agent: {str(e)}\n\nTraceback:\n{exc_tb}"
        raise Exception(error_msg) from e


