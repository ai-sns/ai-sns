import sys
import asyncio
from contextlib import AsyncExitStack
from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
from PyQt6.QtWidgets import QApplication
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import Anthropic
from dotenv import load_dotenv

from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QPushButton, QLineEdit
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget

load_dotenv()  # 加载环境变量


class MCPClientWorker(QObject):
    """异步任务工作器，在独立线程中运行事件循环"""
    response_ready = pyqtSignal(str)  # 处理完成信号
    error_occurred = pyqtSignal(str)  # 错误信号
    tools_listed = pyqtSignal(list)  # 工具列表信号

    def __init__(self, server_script_path: str):
        super().__init__()
        self.server_script_path = server_script_path
        self.loop = asyncio.new_event_loop()
        self.session: Optional[ClientSession] = None
        self.anthropic = Anthropic()

    @pyqtSlot()
    def start_connection(self):
        """启动异步连接（在工作者线程中调用）"""
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self._connect_to_server())
        except Exception as e:
            self.error_occurred.emit(f"连接错误: {str(e)}")

    async def _connect_to_server(self):
        """建立服务器连接"""
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

            # 获取可用工具列表
            response = await self.session.list_tools()
            self.tools_listed.emit([tool.name for tool in response.tools])

    @pyqtSlot(str)
    def process_query(self, query: str):
        """处理用户查询（线程安全入口点）"""
        future = asyncio.run_coroutine_threadsafe(
            self._process_query_async(query),
            self.loop
        )
        future.add_done_callback(self._handle_query_result)

    async def _process_query_async(self, query: str) -> str:
        """异步处理查询的核心逻辑"""
        try:
            # 工具调用示例（根据实际需求修改）
            tool_result = await self.session.call_tool("get_alerts", {"state": "CA"})

            # 获取可用工具定义
            tools_response = await self.session.list_tools()
            available_tools = [{
                "name": t.name,
                "description": t.description,
                "input_schema": t.inputSchema
            } for t in tools_response.tools]
            # 调用Claude API
            response = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[{"role": "user", "content": query}],
                tools=available_tools
            )
            # 处理多内容响应
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


from PyQt6.QtWidgets import (QMainWindow, QPushButton,
                             QVBoxLayout, QWidget, QTextEdit)


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

        # 主控件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        # 连接按钮
        self.connect_btn = QPushButton("连接服务器")
        self.connect_btn.setFixedHeight(40)

        # 状态显示区域
        self.status_display = QTextEdit()
        self.status_display.setReadOnly(True)

        # 组装界面
        layout.addWidget(self.connect_btn)
        layout.addWidget(self.status_display)
        central_widget.setLayout(layout)

    def connect_signals(self):
        """连接信号与槽"""
        # 按钮点击事件
        self.connect_btn.clicked.connect(self.on_connect_clicked)

        # 工作线程信号
        self.worker.response_ready.connect(self.display_response)
        self.worker.error_occurred.connect(self.display_error)
        self.worker.tools_listed.connect(self.display_tools)

    def on_connect_clicked(self):
        """连接按钮点击处理"""
        self.status_display.append("正在连接服务器...")
        self.connect_btn.setEnabled(False)  # 防止重复点击

        # 创建工作线程
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)

        # 线程结束时自动清理
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        # 启动线程
        self.worker_thread.started.connect(self.worker.start_connection)
        self.worker_thread.start()

    def display_response(self, text):
        """显示API响应"""
        self.status_display.append(f"响应: {text}")
        self.connect_btn.setEnabled(True)  # 恢复按钮状态

    def display_error(self, error):
        """显示错误信息"""
        self.status_display.append(f"错误: {error}")
        self.connect_btn.setEnabled(True)  # 恢复按钮状态

    def display_tools(self, tools):
        """显示可用工具列表"""
        self.status_display.append("可用工具:")
        for tool in tools:
            self.status_display.append(f"- {tool}")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 从配置获取服务器路径（示例）
    server_path = "server.py"

    # 创建工作器和主窗口
    worker = MCPClientWorker(server_path)
    window = MainWindow(worker)
    window.show()

    sys.exit(app.exec())
