import subprocess
import json
import time
import sys
from typing import Optional, Dict, Any
import os


class MCPClientController:
    def __init__(self, client_script_path: str = "client_subprocess.py"):
        """
        Initialize client controller with robust subprocess management

        Changes:
        1. Added explicit flushing for stdout/stderr
        2. Separated stdout/stderr handling to prevent blocking
        3. Improved timeout handling with readline
        """
        # self.process = subprocess.Popen(
        #     ["C:\\dev\\agi-ev\\ai-sns\\venv\\Scripts\\python.exe", client_script_path],
        #     stdin=subprocess.PIPE,
        #     stdout=subprocess.PIPE,
        #     stderr=subprocess.PIPE,
        #     text=True,
        #     bufsize=1,  # Line buffered
        #     universal_newlines=True
        # )
        # self._wait_for_ready()
        python_interpreter = r"C:\dev\agi-ev\ai-sns\venv\Scripts\python.exe"

        # 将路径转换为原始字符串并添加双引号防止空格路径问题
        command = f'C:\\dev\\agi-ev\\ai-sns\\venv\\Scripts\\python.exe C:\\dev\\agi-ev\\ai-sns\\ai-sns\\mcp\\client_subprocess.py'

        # 使用os.system实现同步执行（替代方案见下方说明）
        print("before os.system")
        # os.system(command)
        # result = subprocess.run([f'C:\\dev\\agi-ev\\ai-sns\\venv\\Scripts\\python.exe', 'C:\\dev\\agi-ev\\ai-sns\\mcp\\client_subprocess.py'], capture_output=True, text=True)
        # process  = subprocess.Popen([f'C:\\dev\\agi-ev\\ai-sns\\venv\\Scripts\\python.exe', 'C:\\dev\\agi-ev\\ai-sns\\ai-sns\\mcp\\client_subprocess.py'], stdout=None, stderr=None)
        # 启动子进程，并允许通过标准输入与之交互
        process = subprocess.Popen(
            [r'C:\dev\agi-ev\ai-sns\venv\Scripts\python.exe', r'C:\dev\agi-ev\ai-sns\ai-sns\mcp\client_subprocess.py'],
            stdin=subprocess.PIPE,  # 启用标准输入管道
            stdout=subprocess.PIPE,  # 启用标准输出管道
            stderr=subprocess.PIPE,  # 启用标准错误管道
            text=True,  # 自动编码/解码文本
            bufsize=1,  # 行缓冲模式(立即刷新)
            universal_newlines=True,  # 与text=True相同，保持向后兼容
            encoding = 'utf-8'
        )

        # 示例：向子进程的标准输入写入数据
        input_data = '{"command": "connect", "args": {"path":"server.py"}}\n'
        process.stdin.write(input_data)  # 向标准输入写入数据
        process.stdin.flush()  # 确保数据被发送
        #
        # time.sleep(6)
        # 示例：向子进程的标准输入写入数据
        input_data = '{"command": "query", "args": {"text":"CA"}}\n'
        process.stdin.write(input_data)  # 向标准输入写入数据
        process.stdin.flush()  # 确保数据被发送

        # 可选：读取子进程的输出
        output, errors = process.communicate()  # 等待进程完成并获取输出和错误
        if output:
            print("Output from subprocess:", output)
        if errors:
            print("Errors from subprocess:", errors)




        while True:

            pass

        print("after os.system")
        # print(stdout.decode())
        # self.process = subprocess.Popen(
        #     ['C:\\dev\\agi-ev\\ai-sns\\venv\\Scripts\\python.exe', 'C:\\dev\\agi-ev\\ai-sns\\mcp\\client_subprocess.py'],
        #     stdout=subprocess.PIPE,
        #     stderr=subprocess.PIPE,
        #     text=True
        # )
        #
        # # 后续可通过 process.communicate() 获取完整输出
        # output, errors = self.process.communicate()
        # print(output)

    def _wait_for_ready(self, timeout: int = 10):
        """Wait for client startup message with timeout"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            line = self.process.stdout.readline()
            if "MCP Client Started!" in line:
                print("Client ready signal received")
                return
            # Handle stderr to prevent blocking
            while True:
                err_line = self.process.stderr.readline()
                if not err_line:
                    break
                print(f"[Client ERR] {err_line.strip()}", file=sys.stderr)
        raise TimeoutError("Client startup timed out")

    def _send_command(self, command: str, args: Dict[str, Any]) -> Optional[Dict]:
        """
        Send command and read response with robust error handling

        Changes:
        1. Added newline after command
        2. Full response reading implementation
        3. Separate stderr monitoring
        """
        try:
            # Send command with newline delimiter
            cmd_json = json.dumps({"command": command, "args": args}) + "\n"
            self.process.stdin.write(cmd_json)
            self.process.stdin.flush()

            # Read response with timeout
            response_line = self.process.stdout.readline().strip()
            if not response_line:
                return None

            return json.loads(response_line)

        except (json.JSONDecodeError, subprocess.SubprocessError) as e:
            print(f"Command failed: {str(e)}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Unexpected error: {str(e)}", file=sys.stderr)
            return None

    # ... (connect_to_server, process_query, close methods remain unchanged) ...
    # ... (example usage remains unchanged) ...

    def connect_to_server(self, server_script_path: str) -> bool:
        """
        Connect to the specified server script

        Args:
            server_script_path: Path to server script (.py or .js)

        Returns:
            True if connection succeeded
        """
        response = self._send_command("connect", {"path": server_script_path})
        return response.get("status") == "connected" if response else False

    def process_query(self, query: str) -> Optional[str]:
        """
        Process a query through the client

        Args:
            query: The query string to process

        Returns:
            The response text or None if failed
        """
        response = self._send_command("query", {"text": query})
        return response.get("result") if response else None

    def close(self):
        """Clean up the subprocess"""
        try:
            # self.process.stdin.write(json.dumps({"command": "quit"}) + "\n")
            # self.process.stdin.flush()
            # self.process.wait(timeout=2)
            pass
        except subprocess.TimeoutExpired:

            pass
        finally:
            pass


# Example usage
if __name__ == "__main__":
    controller = MCPClientController()
    #控制台输入命令：{"command": "connect", "args": {"path":"server.py"}} {"command": "query", "args": {"text":"CA"}}
    try:
        print("aa")
        # Connect to server
        # if controller.connect_to_server("server.py"):
        #     print("Successfully connected to server")
        #
        #     # Process queries
        #     while True:
        #         query = input("Enter query (or 'quit' to exit): ").strip()
        #         if query.lower() == 'quit':
        #             break
        #
        #         response = controller.process_query(query)
        #         print("Response:", response)
        # else:
        #     print("Failed to connect to server")
    finally:
        #
        pass
