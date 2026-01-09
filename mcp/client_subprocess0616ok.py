import asyncio
import json
import sys
import aiohttp
from typing import Optional, Dict, Any, Union
from contextlib import AsyncExitStack
from enum import Enum

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.session import ClientSession as BaseClientSession

from anthropic import Anthropic
from dotenv import load_dotenv
import time

load_dotenv()


class ConnectionType(Enum):
    STDIO = "stdio"
    SSE = "sse"
    HTTP = "streamable-http"


class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()
        self.connection_type: Optional[ConnectionType] = None
        self.http_session: Optional[aiohttp.ClientSession] = None

    async def connect_to_server(self, config_path: str, connection_type: str = "auto"):
        """Connect to an MCP server with support for multiple connection types

        Args:
            config_path: Path to the configuration file or server script
            connection_type: Type of connection ("stdio", "sse", "http", or "auto")
        """
        # Load configuration
        config = await self._load_config(config_path)
        # Determine connection type
        if connection_type == "auto":
            detected_type = self._detect_connection_type(config)
        else:
            detected_type = ConnectionType(connection_type)

        self.connection_type = detected_type

        # Connect based on type
        if detected_type == ConnectionType.STDIO:
            await self._connect_stdio(config)
        elif detected_type == ConnectionType.SSE:
            await self._connect_sse(config)
        elif detected_type == ConnectionType.HTTP:
            await self._connect_http(config)
        else:
            raise ValueError(f"Unsupported connection type: {detected_type}")

        # Initialize session and list tools
        await self._initialize_session()

    async def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file or return direct config"""
        if config_path.endswith('.json'):
            # Direct JSON config file
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Python file containing JSON config
            filename = f"C:\\dev\\agi-ev\\ai-sns\\ai-sns\\mcp\\{config_path}.json"
            with open(filename, 'rt', encoding='utf-8') as f:
                config_content = f.read()
            return json.loads(config_content)

    def _detect_connection_typebak(self, config: Dict[str, Any]) -> ConnectionType:
        """Auto-detect connection type from config"""
        if "url" in config or "endpoint" in config:
            if "sse" in config.get("url", "").lower() or config.get("type") == "sse":
                return ConnectionType.SSE
            else:
                return ConnectionType.HTTP
        elif "command" in config or "mcpServers" in config:
            return ConnectionType.STDIO
        else:
            # Default fallback
            return ConnectionType.STDIO

    def _detect_connection_type(self, config: Dict[str, Any]) -> ConnectionType:
        """Auto-detect connection type from config"""
        # Handle mcpServers structure
        if "mcpServers" in config:
            # Get the first (and usually only) server config
            server_configs = config["mcpServers"]
            if not server_configs:
                raise ValueError("mcpServers is empty")

            # Get the first server configuration
            server_name = list(server_configs.keys())[0]
            server_config = server_configs[server_name]

            print(f"Detecting connection type for server: {server_name}", flush=True)
            print(f"Server config: {server_config}", flush=True)

            # Check for explicit type specification
            if "type" in server_config:
                connection_type = server_config["type"].upper()
                if connection_type == "SSE":
                    return ConnectionType.SSE
                elif connection_type == "STREAMABLE-HTTP":
                    return ConnectionType.HTTP
                elif connection_type == "STDIO":
                    return ConnectionType.STDIO
                else:
                    print(f"Warning: Unknown type '{connection_type}', falling back to auto-detection", flush=True)

            # Auto-detect based on available fields
            if "url" in server_config:
                url = server_config["url"].lower()
                if "sse" in url or "/sse" in url:
                    return ConnectionType.SSE
                else:
                    return ConnectionType.HTTP
            elif "endpoint" in server_config:
                return ConnectionType.HTTP
            elif "command" in server_config:
                return ConnectionType.STDIO
            else:
                print(f"Warning: Cannot determine connection type from config, defaulting to STDIO", flush=True)
                return ConnectionType.STDIO

        # Handle direct config (not wrapped in mcpServers)
        else:
            # Check for explicit type
            if "type" in config:
                connection_type = config["type"].upper()
                if connection_type == "SSE":
                    return ConnectionType.SSE
                elif connection_type == "HTTP":
                    return ConnectionType.HTTP
                elif connection_type == "STDIO":
                    return ConnectionType.STDIO

            # Auto-detect based on available fields
            if "url" in config:
                url = config["url"].lower()
                if "sse" in url or "/sse" in url:
                    return ConnectionType.SSE
                else:
                    return ConnectionType.HTTP
            elif "endpoint" in config:
                return ConnectionType.HTTP
            elif "command" in config:
                return ConnectionType.STDIO
            else:
                # Default fallback
                print("Warning: Cannot determine connection type, defaulting to STDIO", flush=True)
                return ConnectionType.STDIO

    async def _connect_stdio(self, config: Dict[str, Any]):
        """Connect using stdio transport"""
        print("Connecting via stdio...", flush=True)

        if "mcpServers" in config:
            # Extract from mcpServers structure
            server_config = list(config["mcpServers"].values())[0]
            command = server_config["command"]
            args = server_config["args"]
            env = server_config.get("env", None)
        else:
            # Direct config
            command = config["command"]
            args = config["args"]
            env = config.get("env", None)

        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=env
        )

        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )

    async def _connect_sse(self, config: Dict[str, Any]):
        """Connect using SSE transport"""
        print("Connecting via SSE...", flush=True)

        if "mcpServers" in config:
            # Extract from mcpServers structure
            server_config = list(config["mcpServers"].values())[0]
            url = server_config.get("url") or server_config.get("endpoint")
            headers = server_config.get("headers", {})
            api_key = server_config.get("api_key") or server_config.get("key")
        else:
            # Direct config
            url = config.get("url") or config.get("endpoint")
            headers = config.get("headers", {})
            api_key = config.get("api_key") or config.get("key")

        if not url:
            raise ValueError("SSE connection requires 'url' or 'endpoint' in config")

        # Add authentication if provided
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        print(f"Connecting to SSE endpoint: {url}", flush=True)

        try:
            sse_transport = await self.exit_stack.enter_async_context(
                sse_client(url, headers=headers)
            )
            # 关键修复：解构读写流[1][3]
            read_stream, write_stream = sse_transport

            # 正确初始化会话（两个参数）
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )
        except Exception as e:
            raise ConnectionError(f"Failed to connect via SSE: {str(e)}")

    async def _connect_httpok(self, config: Dict[str, Any]):
        """Connect using HTTP transport (custom implementation)"""
        print("Connecting via HTTP...", flush=True)

        if "mcpServers" in config:
            # Extract from mcpServers structure
            server_config = list(config["mcpServers"].values())[0]
            base_url = server_config.get("url") or server_config.get("endpoint")
            headers = server_config.get("headers", {})
            api_key = server_config.get("api_key") or server_config.get("key")
        else:
            # Direct config
            base_url = config.get("url") or config.get("endpoint")
            headers = config.get("headers", {})
            api_key = config.get("api_key") or config.get("key")

        if not base_url:
            raise ValueError("HTTP connection requires 'url' or 'endpoint' in config")

        # Add authentication if provided
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        print(f"Connecting to HTTP endpoint: {base_url}", flush=True)

        # timeout=30
        # http_transport = await self.exit_stack.enter_async_context(
        #     streamablehttp_client(url=base_url)
        # )
        # # 关键修复：解构读写流[1][3]
        # read_stream, write_stream,_ = http_transport
        #
        # # 正确初始化会话（两个参数）
        # self.session = await self.exit_stack.enter_async_context(
        #     ClientSession(read_stream, write_stream)
        # )

        async with streamablehttp_client("http://localhost:3088/mcp") as transport:
            async with ClientSession(transport[0], transport[1]) as session:
                self.session = session
                await self.session.initialize()

                # List available tools
                response = await self.session.list_tools()
                tools = response.tools
                print("Available tools:", [tool.name for tool in tools], flush=True)
                print("Connection established successfully!", flush=True)

        # async with streamablehttp_client("http://localhost:3088/mcp/") as (
        #         read_stream,
        #         write_stream,
        #         _,
        # ):
        #     # Create a session using the client streams
        #     async with ClientSession(read_stream, write_stream) as session:
        #         # Initialize the connection
        #         init_response = await session.initialize()
        #         print("Server info:", init_response.serverInfo, flush=True)

    async def _connect_http(self, config: Dict[str, Any]):
        """Connect using HTTP transport (custom implementation)"""
        print("Connecting via HTTP...", flush=True)

        if "mcpServers" in config:
            # Extract from mcpServers structure
            server_config = list(config["mcpServers"].values())[0]
            base_url = server_config.get("url") or server_config.get("endpoint")
            headers = server_config.get("headers", {})
            api_key = server_config.get("api_key") or server_config.get("key")
        else:
            # Direct config
            base_url = config.get("url") or config.get("endpoint")
            headers = config.get("headers", {})
            api_key = config.get("api_key") or config.get("key")

        if not base_url:
            raise ValueError("HTTP connection requires 'url' or 'endpoint' in config")

        # Add authentication if provided
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        print(f"Connecting to HTTP endpoint: {base_url}", flush=True)

        # timeout=30
        # http_transport = await self.exit_stack.enter_async_context(
        #     streamablehttp_client(url=base_url)
        # )
        # # 关键修复：解构读写流[1][3]
        # read_stream, write_stream,_ = http_transport
        #
        # # 正确初始化会话（两个参数）
        # self.session = await self.exit_stack.enter_async_context(
        #     ClientSession(read_stream, write_stream)
        # )

        transport = None
        session = None

        # 手动创建并管理会话生命周期，避免上下文管理器自动关闭
        try:
            # 建立传输连接
            transport = await self.exit_stack.enter_async_context(
                streamablehttp_client("http://localhost:3088/mcp")
            )
            # await transport.__aenter__()
            # Create a client session with the transport
            self.session = ClientSession(transport[0], transport[1])
            await self.session.__aenter__()

            # Initialize the session
            await self.session.initialize()

            # List available tools
            response = await self.session.list_tools()
            tools = response.tools

            # Log available tools
            tool_names = [tool.name for tool in tools]
            print("Available tools:", tool_names, flush=True)
            print("Connection established successfully!", flush=True)
        except Exception as e:
            # 异常时确保清理已分配资源
            if hasattr(self, 'session'):
                await self.session.close()

        # async with streamablehttp_client("http://localhost:3088/mcp/") as (
        #         read_stream,
        #         write_stream,
        #         _,
        # ):
        #     # Create a session using the client streams
        #     async with ClientSession(read_stream, write_stream) as session:
        #         # Initialize the connection
        #         init_response = await session.initialize()
        #         print("Server info:", init_response.serverInfo, flush=True)

    async def _initialize_session(self):
        """Initialize session and list available tools"""
        return
        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("Available tools:", [tool.name for tool in tools], flush=True)
        print("Connection established successfully!", flush=True)

    async def run_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> Any:
        """Run a tool with given arguments"""
        if not self.session:
            raise RuntimeError("Not connected to any server")

        response = await self.session.list_tools()
        tools = response.tools
        print("Available tools:", [tool.name for tool in tools], flush=True)
        print("Connection established successfully!", flush=True)

        tool_args = {"code": "print(12)",
                     "languageId": "python"
                     }
        result = await self.session.call_tool(tool_name, tool_args)
        print(f"Tool {tool_name} result:", result, flush=True)
        return result

    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available tools"""
        if not self.session:
            raise RuntimeError("Not connected to any server")

        messages = [{"role": "user", "content": query}]

        # Get available tools for Claude
        response = await self.session.list_tools()
        available_tools = [{
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in response.tools]

        print("Available tools for Claude:", [tool["name"] for tool in available_tools], flush=True)

        # Initial Claude API call
        response = self.anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=messages,
            tools=available_tools
        )

        # Process response and handle tool calls
        tool_results = []
        final_text = []

        for content in response.content:
            if content.type == 'text':
                final_text.append(content.text)
            elif content.type == 'tool_use':
                tool_name = content.name
                tool_args = content.input

                # Execute tool call
                result = await self.session.call_tool(tool_name, tool_args)
                tool_results.append({"call": tool_name, "result": result})
                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

                # Continue conversation with tool results
                if hasattr(content, 'text') and content.text:
                    messages.append({
                        "role": "assistant",
                        "content": content.text
                    })
                messages.append({
                    "role": "user",
                    "content": str(result.content) if hasattr(result, 'content') else str(result)
                })

                # Get next response from Claude
                response = self.anthropic.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=messages,
                )

                final_text.append(response.content[0].text)

        return "\n".join(final_text)

    async def get_server_info(self) -> Dict[str, Any]:
        """Get server information"""
        if not self.session:
            raise RuntimeError("Not connected to any server")

        info = {
            "connection_type": self.connection_type.value if self.connection_type else "unknown",
            "tools": [],
            "resources": []
        }

        try:
            # Get tools
            tools_response = await self.session.list_tools()
            info["tools"] = [tool.name for tool in tools_response.tools]
        except Exception as e:
            info["tools_error"] = str(e)

        try:
            # Get resources if available
            resources_response = await self.session.list_resources()
            info["resources"] = [resource.name for resource in resources_response.resources]
        except Exception as e:
            info["resources_error"] = str(e)

        return info

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()


class HTTPTransport:
    """Custom HTTP transport for MCP over HTTP"""

    def __init__(self, session: aiohttp.ClientSession, base_url: str):
        self.session = session
        self.base_url = base_url

    async def send(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send a message via HTTP POST"""
        async with self.session.post("/mcp", json=message) as response:
            if response.status != 200:
                raise ConnectionError(f"HTTP request failed: {response.status}")
            return await response.json()

    async def close(self):
        """Close the transport"""
        if not self.session.closed:
            await self.session.close()


async def main():
    client = MCPClient()
    print("MCP Client Started! 支持多种连接方式", flush=True)

    try:
        # Wait for commands from stdin
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break

                command = line.strip()
                if not command:
                    continue

                try:
                    cmd_data = json.loads(command)
                    print(f"Received command: {cmd_data}", flush=True)
                except json.JSONDecodeError as e:
                    print(json.dumps({"error": f"Invalid JSON: {str(e)}"}), flush=True)
                    continue

                if cmd_data["command"] == "connect":
                    try:
                        config_path = cmd_data["args"]["path"]
                        connection_type = cmd_data["args"].get("type", "auto")

                        await client.connect_to_server(config_path, connection_type)

                        # Get server info
                        server_info = await client.get_server_info()
                        result = {
                            "status": "connected",
                            "connection_type": server_info["connection_type"],
                            "tools": server_info["tools"],
                            "resources": server_info.get("resources", [])
                        }
                        print(json.dumps(result), flush=True)
                    except Exception as e:
                        error_result = {"error": f"Connection failed: {str(e)}"}
                        print(json.dumps(error_result), flush=True)

                elif cmd_data["command"] == "query":
                    try:
                        result = await client.process_query(cmd_data["args"]["text"])
                        response = {"result": result}
                        print(json.dumps(response), flush=True)
                    except Exception as e:
                        error_result = {"error": f"Query failed: {str(e)}"}
                        print(json.dumps(error_result), flush=True)

                elif cmd_data["command"] == "info":
                    try:
                        info = await client.get_server_info()
                        print(json.dumps(info), flush=True)
                    except Exception as e:
                        error_result = {"error": f"Info failed: {str(e)}"}
                        print(json.dumps(error_result), flush=True)

                elif cmd_data["command"] == "quit":
                    break

                else:
                    # Treat as tool call
                    tool_name = cmd_data["command"]
                    tool_args = cmd_data["args"]

                    try:
                        result = await client.run_tool(tool_name, tool_args)
                        response = {"result": str(result)}
                        print(json.dumps(response), flush=True)
                    except Exception as e:
                        error_result = {"error": f"Tool execution failed: {str(e)}"}
                        print(json.dumps(error_result), flush=True)

            except Exception as e:
                error_result = {"error": f"Command processing error: {str(e)}"}
                print(json.dumps(error_result), flush=True)

    except KeyboardInterrupt:
        print("Interrupted by user", flush=True)
    except Exception as e:
        print(f"Main loop error: {str(e)}", flush=True)
    finally:
        print("Cleaning up...", flush=True)
        await client.cleanup()
        print("Cleanup complete", flush=True)


if __name__ == "__main__":
    try:
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        asyncio.run(main())
    except Exception as e:
        print(f"Failed to start: {str(e)}", flush=True)
        sys.exit(1)
