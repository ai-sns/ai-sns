import sys
import asyncio
from contextlib import AsyncExitStack
from typing import Optional, Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QPushButton
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


class MCPClientWorker(QObject):
    """异步任务工作器，整合了工具调用功能"""
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    tools_listed = pyqtSignal(list)
    tool_result_received = pyqtSignal(dict)  # 新增：工具调用结果信号

    def __init__(self, server_script_path: str):
        super().__init__()
        self.server_script_path = server_script_path
        self.loop = asyncio.new_event_loop()
        self.session: Optional[ClientSession] = None
        self.anthropic = Anthropic()
        self.available_tools: list = []

    @pyqtSlot()
    def start_connection(self):
        """启动异步连接"""
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self._connect_to_server())
        except Exception as e:
            self.error_occurred.emit(f"连接错误: {str(e)}")

    async def _connect_to_server(self):
        """建立服务器连接并获取工具列表"""
        is_python = self.server_script_path.endswith('.py')
        is_js = self.server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("服务器脚本必须是.py或.js文件")
        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[self.server_script_path],
            env=None
        )
        async with AsyncExitStack() as exit_stack:
            stdio_transport = await exit_stack.enter_async_context(stdio_client(server_params))
            stdio, write = stdio_transport
            self.session = await exit_stack.enter_async_context(ClientSession(stdio, write))
            await self.session.initialize()
            # 获取并缓存可用工具列表
            response = await self.session.list_tools()
            self.available_tools = [{
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            } for tool in response.tools]

            self.tools_listed.emit([tool["name"] for tool in self.available_tools])

    @pyqtSlot(str)
    def process_query(self, query: str):
        """处理用户查询的线程安全入口"""
        future = asyncio.run_coroutine_threadsafe(
            self._process_query_async(query),
            self.loop
        )
        future.add_done_callback(self._handle_query_result)

    @pyqtSlot(str, dict)
    def call_tool(self, tool_name: str, tool_args: Dict[str, Any]):
        """调用工具的线程安全入口"""
        future = asyncio.run_coroutine_threadsafe(
            self._call_tool_async(tool_name, tool_args),
            self.loop
        )
        future.add_done_callback(self._handle_tool_result)

    async def _call_tool_async(self, tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
        """异步调用工具的核心逻辑"""
        if not self.session:
            raise RuntimeError("未连接到服务器")

        try:
            result = await self.session.call_tool(tool_name, tool_args)
            return {
                "tool_name": tool_name,
                "args": tool_args,
                "result": result
            }
        except Exception as e:
            return {
                "tool_name": tool_name,
                "error": str(e)
            }

    async def _process_query_async(self, query: str) -> str:
        """处理查询的核心逻辑，整合了工具调用功能"""
        try:
            # 1. 示例工具调用
            tool_result = await self._call_tool_async("get_alerts", {"state": "CA"})
            self.tool_result_received.emit(tool_result)
            # 2. 调用Claude API处理查询
            response = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[{"role": "user", "content": query}],
                tools=self.available_tools
            )
            # 3. 处理响应中的工具调用请求
            tool_results = []
            for content in response.content:
                if content.type == 'tool_use':
                    tool_result = await self._call_tool_async(content.name, content.input)
                    tool_results.append(tool_result)
                    self.tool_result_received.emit(tool_result)
            # 4. 返回文本响应
            return "\n".join(
                content.text for content in response.content
                if content.type == 'text'
            )
        except Exception as e:
            return f"处理错误: {str(e)}"

    def _handle_query_result(self, future):
        """处理查询结果的回调"""
        try:
            result = future.result()
            self.response_ready.emit(result)
        except Exception as e:
            self.error_occurred.emit(str(e))

    def _handle_tool_result(self, future):
        """处理工具调用结果的回调"""
        try:
            result = future.result()
            if "error" in result:
                self.error_occurred.emit(f"工具 {result['tool_name']} 调用失败: {result['error']}")
            else:
                self.response_ready.emit(
                    f"工具调用成功: {result['tool_name']}\n"
                    f"参数: {result['args']}\n"
                    f"结果: {result['result']}"
                )
        except Exception as e:
            self.error_occurred.emit(f"处理工具结果错误: {str(e)}")


class MainWindow(QMainWindow):
    def __init__(self, worker):
        super().__init__()
        self.worker = worker
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """初始化UI组件"""
        self.setWindowTitle("MCP客户端")
        self.setGeometry(100, 100, 800, 600)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        # 连接按钮
        self.connect_btn = QPushButton("连接服务器")
        self.connect_btn.setFixedHeight(40)
        # 状态显示区域
        self.status_display = QTextEdit()
        self.status_display.setReadOnly(True)
        # 工具调用测试按钮
        self.test_tool_btn = QPushButton("测试工具调用")
        self.test_tool_btn.setFixedHeight(40)
        self.test_tool_btn.setEnabled(False)
        layout.addWidget(self.connect_btn)
        layout.addWidget(self.test_tool_btn)
        layout.addWidget(self.status_display)
        central_widget.setLayout(layout)

    def connect_signals(self):
        """连接信号与槽"""
        self.connect_btn.clicked.connect(self.on_connect_clicked)
        self.test_tool_btn.clicked.connect(self.on_test_tool_clicked)
        self.worker.response_ready.connect(self.display_response)
        self.worker.error_occurred.connect(self.display_error)
        self.worker.tools_listed.connect(self.display_tools)
        self.worker.tool_result_received.connect(self.display_tool_result)

    def on_connect_clicked(self):
        """连接按钮点击处理"""
        self.status_display.append("正在连接服务器...")
        self.connect_btn.setEnabled(False)
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_thread.started.connect(self.worker.start_connection)
        self.worker_thread.start()

    def on_test_tool_clicked(self):
        """测试工具调用"""
        self.worker.call_tool("get_alerts", {"state": "CA"})

    def display_response(self, text):
        """显示API响应"""
        self.status_display.append(f"响应: {text}")

    def display_error(self, error):
        """显示错误信息"""
        self.status_display.append(f"错误: {error}")

    def display_tools(self, tools):
        """显示可用工具列表"""
        self.status_display.append("可用工具:")
        for tool in tools:
            self.status_display.append(f"- {tool}")
        self.test_tool_btn.setEnabled(True)

    def display_tool_result(self, result):
        """显示工具调用结果"""
        self.status_display.append(f"工具调用结果: {result}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    worker = MCPClientWorker("server.py")
    window = MainWindow(worker)
    window.show()
    sys.exit(app.exec())
