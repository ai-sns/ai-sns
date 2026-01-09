import asyncio
import json
import sys  # 添加这个导入
from typing import Optional
from typing import Optional,Dict,Any
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from anthropic import Anthropic
from dotenv import load_dotenv
import time

load_dotenv()  # load environment variables from .env


class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()

    async def connect_to_serverbak(self, server_script_path: str):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")
        server_script_path="C:\\dev\\agi-ev\\ai-sns\\ai-sns\\mcp\\"+server_script_path
        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("tools:", tools, flush=True)  # 添加 flush=True
        print("\nConnected to server with tools:", [tool.name for tool in tools], flush=True)

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """

        filename = "C:\\dev\\agi-ev\\ai-sns\\ai-sns\\coding\\" + server_script_path + ".py"

        with open(filename, "rt", encoding='utf-8') as file:
            config_content = file.read()

        config_json = json.loads(config_content)
        print(config_json)
        command = config_json["mcpServers"]["duckduckgo"]["command"]
        print(command, flush=True)
        args = config_json["mcpServers"]["duckduckgo"]["args"]
        env = config_json["mcpServers"]["duckduckgo"].get("env", None)

        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=env
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("tools:", tools, flush=True)  # 添加 flush=True
        print("\nConnected to server with tools:", [tool.name for tool in tools], flush=True)

    async def run_tool(self, tool_name: str,tool_args:Dict[str, Any]) -> str:
        result = await self.session.call_tool(tool_name, tool_args)
        print("result:", result, flush=True)  # 添加 flush=True
        return result

    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available tools"""
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]
        tool_name = "get_alerts"
        tool_args = {"state": query}
        result = await self.session.call_tool(tool_name, tool_args)
        print("result:", result, flush=True)  # 添加 flush=True

        response = await self.session.list_tools()
        available_tools = [{
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in response.tools]

        print("available_tools", available_tools, flush=True)  # 添加 flush=True

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
                    "content": result.content
                })

                # Get next response from Claude
                response = self.anthropic.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=messages,
                )

                final_text.append(response.content[0].text)

        return "\n".join(final_text)

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!", flush=True)
        print("Type your queries or 'quit' to exit.", flush=True)

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)
                print("\n" + response, flush=True)

            except Exception as e:
                print(f"\nError: {str(e)}", flush=True)

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()


async def read_stdin_line():
    """异步读取stdin的辅助函数"""
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)

    try:
        line = await reader.readline()
        return line.decode('utf-8').strip() if line else None
    except Exception as e:
        print(f"读取stdin错误: {e}", flush=True)
        return None


async def main():
    client = MCPClient()
    print("MCP Client Started!cjrok你好呀！", flush=True)

    try:
        print("go get input in try", flush=True)

        # 设置stdin为非阻塞模式（仅在Unix系统上）
        if sys.platform != 'win32':
            import fcntl
            import os
            fd = sys.stdin.fileno()
            fl = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

        # Wait for commands from stdin
        while True:
            print("second level try", flush=True)
            try:
                print("trying to read command...", flush=True)

                # 方法1: 使用简单的同步读取（推荐）
                try:
                    line = sys.stdin.readline()
                    if not line:
                        print("stdin closed, breaking", flush=True)
                        break

                    command = line.strip()
                    if not command:
                        print("empty command, continuing", flush=True)
                        continue

                except EOFError:
                    print("EOF reached, breaking", flush=True)
                    break

                # 方法2: 如果上面不行，使用这个异步版本
                # command_line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                # if not command_line:
                #     print("stdin closed, breaking", flush=True)
                #     break
                #
                # command = command_line.strip()
                # if not command:
                #     print("empty command, continuing", flush=True)
                #     continue

                print(f"get command: {command}", flush=True)

                try:
                    cmd_data = json.loads(command)
                    print(f"parsed command: {cmd_data}", flush=True)
                except json.JSONDecodeError as e:
                    print(json.dumps({"error": f"Invalid JSON format: {str(e)}"}), flush=True)
                    continue

                if cmd_data["command"] == "connect":
                    print("executing connect command", flush=True)
                    try:
                        await client.connect_to_server(cmd_data["args"]["path"])
                        result = {"status": "connected"}
                        print(json.dumps(result), flush=True)
                    except Exception as e:
                        error_result = {"error": f"Connection failed: {str(e)}"}
                        print(json.dumps(error_result), flush=True)

                elif cmd_data["command"] == "query":
                    print("executing query command", flush=True)
                    try:
                        result = await client.process_query(cmd_data["args"]["text"])
                        response = {"result": result}
                        print(json.dumps(response), flush=True)
                    except Exception as e:
                        error_result = {"error": f"Query failed: {str(e)}"}
                        print(json.dumps(error_result), flush=True)

                elif cmd_data["command"] == "quit":
                    print("quit command received", flush=True)
                    break

                else:
                    tool_name = cmd_data["command"]
                    print("tool_namecjrok：",tool_name)
                    tool_args = cmd_data["args"]
                    print("tool_argscjrok：",tool_args)

                    result = await client.run_tool(tool_name,tool_args)
                    print("duckgoresult：",result)
                    response = {"result": result}
                    print(json.dumps(response), flush=True)
                    # error_result = {"error": f"Unknown command: {cmd_data['command']}"}
                    # print(json.dumps(error_result), flush=True)


            except Exception as e:
                error_result = {"error": f"Command processing error: {str(e)}"}
                print(json.dumps(error_result), flush=True)

    except KeyboardInterrupt:
        print("Interrupted by user", flush=True)
    except Exception as e:
        print(f"Main loop error: {str(e)}", flush=True)
    finally:
        print("cleaning up...", flush=True)
        await client.cleanup()
        print("cleanup complete", flush=True)


if __name__ == "__main__":
    try:
        # 确保在Windows上使用正确的事件循环策略
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

        asyncio.run(main())
    except Exception as e:
        print(f"Failed to start: {str(e)}", flush=True)
        sys.exit(1)
