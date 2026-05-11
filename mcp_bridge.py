import asyncio
import json
from typing import List, Any
from langchain_core.tools import StructuredTool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPBridge:
    """
    A utility class to connect to an MCP server as a subprocess 
    and convert its tools into LangChain-compatible tools.
    """
    def __init__(self, server_script_path: str):
        self.server_script_path = server_script_path
        # We use uv to run the python script in our virtual environment
        self.server_params = StdioServerParameters(
            command="uv", 
            args=["run", "python", self.server_script_path]
        )
        self._session = None
        self._exit_stack = None

    async def connect(self):
        """Connects to the local MCP server via Standard Input/Output."""
        from contextlib import AsyncExitStack
        self._exit_stack = AsyncExitStack()
        
        # Start the subprocess
        transport = await self._exit_stack.enter_async_context(stdio_client(self.server_params))
        read_stream, write_stream = transport
        
        # Initialize the MCP Session
        self._session = await self._exit_stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )
        await self._session.initialize()
        print(f"✅ Connected to MCP Server at {self.server_script_path}")

    async def disconnect(self):
        """Closes the connection gracefully."""
        if self._exit_stack:
            await self._exit_stack.aclose()

    async def get_langchain_tools(self) -> List[StructuredTool]:
        """
        Fetches tools from the MCP server and dynamically wraps them 
        into LangChain StructuredTools.
        """
        if not self._session:
            raise RuntimeError("Must call connect() before fetching tools.")

        # Ask the MCP server what tools it has
        response = await self._session.list_tools()
        langchain_tools = []

        for mcp_tool in response.tools:
            # Create a factory to correctly bind tool_name and session without exposing them to the LLM signature
            def create_tool(name: str, session: ClientSession, desc: str):
                async def tool_wrapper(**kwargs) -> str:
                    result = await session.call_tool(name, arguments=kwargs)
                    return "\n".join([content.text for content in result.content if content.type == "text"])
                
                # Create a dynamic Pydantic model for the args_schema
                from pydantic import create_model
                from typing import Any
                
                fields = {}
                properties = mcp_tool.inputSchema.get("properties", {})
                required = mcp_tool.inputSchema.get("required", [])
                
                for field_name, field_info in properties.items():
                    # For simplicity, we fallback to Any type. In a real setup, map JSON types to python types.
                    field_type = Any
                    if field_info.get("type") == "string": field_type = str
                    elif field_info.get("type") == "integer": field_type = int
                    elif field_info.get("type") == "number": field_type = float
                    elif field_info.get("type") == "boolean": field_type = bool
                    
                    default = ... if field_name in required else field_info.get("default", None)
                    fields[field_name] = (field_type, default)
                
                schema_model = create_model(f"{name}Schema", **fields)

                return StructuredTool.from_function(
                    coroutine=tool_wrapper,
                    name=name,
                    description=desc,
                    args_schema=schema_model
                )

            lc_tool = create_tool(mcp_tool.name, self._session, mcp_tool.description)
            langchain_tools.append(lc_tool)

        return langchain_tools
