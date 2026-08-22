import os
from contextlib import AsyncExitStack
from typing import Dict, Any, List
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPClient:
    """
    Model Context Protocol (MCP) Client for APEX.
    Enables connection to external tool servers.
    """
    def __init__(self):
        self.sessions: Dict[str, ClientSession] = {}
        self.server_params: Dict[str, StdioServerParameters] = {}
        self.exit_stack = AsyncExitStack()

    async def connect(self, server_name: str, command: str, args: List[str] = None, env: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Connects to an MCP server using stdio transport.
        """
        try:
            params = StdioServerParameters(
                command=command,
                args=args or [],
                env={**os.environ, **(env or {})}
            )
            
            # Connect via stdio and keep the connection alive using exit_stack
            read, write = await self.exit_stack.enter_async_context(stdio_client(params))
            session = await self.exit_stack.enter_async_context(ClientSession(read, write))
            
            await session.initialize()
            self.sessions[server_name] = session
            self.server_params[server_name] = params
                
            return {"success": True, "output": f"Connected to MCP server '{server_name}'."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invocates a tool on a connected MCP server.
        """
        if server_name not in self.sessions:
            return {"success": False, "error": f"Server '{server_name}' not connected."}
            
        try:
            session = self.sessions[server_name]
            result = await session.call_tool(tool_name, arguments)
            return {"success": True, "output": str(result.content)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def list_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """
        Lists tools available on a specific MCP server.
        """
        if server_name not in self.sessions:
            return []
            
        try:
            session = self.sessions[server_name]
            result = await session.list_tools()
            return [{"name": t.name, "description": t.description, "input_schema": t.inputSchema} for t in result.tools]
        except Exception as e:
            print(f"Error listing tools for {server_name}: {e}")
            return []

    async def shutdown(self):
        """
        Gracefully disconnects from all MCP servers.
        """
        await self.exit_stack.aclose()
        self.sessions.clear()
        self.server_params.clear()
