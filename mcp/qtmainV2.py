import sys
import asyncio
from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QTextEdit, QLineEdit, QLabel, QHBoxLayout
)
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import Anthropic
from dotenv import load_dotenv
from contextlib import AsyncExitStack

load_dotenv()  # 加载环境变量


class MCPClientWorker(QObject):
    """异步任务工作器，在独立线程中运行事件循环"""
    response_ready = pyqtSignal(str)  # 处理完成信号
    error_occurred = pyqtSignal(str)  # 错误信号
    tools_listed = pyqtSignal(list)  # 工具列表信号
    connection_status = pyqtSignal(str)  # 连接状态信号

    def __init__(self, server_script_path: str):
        super().__init__()
        self.server_script_path = server_script_path
        self.loop = asyncio.new_event_loop()
        self.session: Optional[ClientSession] = None
        self.anthropic = Anthropic()
        self.connected = False

    @pyqtSlot()
    def start_connection(self):
        """启动异步连接（在工作者线程中调用）"""
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self._connect_to_server())
            self.connected = True
            self.connection_status.emit("已连接到服务器")
        except Exception as e:
            self.error_occurred.emit(f"连接错误: {str(e)}")
            self.connection_status.emit("连接失败")

    async def _connect_to_server(self):
        """建立服务器连接"""
        self.connection_status.emit("正在连接服务器...")
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
        if not self.connected:
            self.error_occurred.emit("错误：请先连接服务器")
            return

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


class MainWindow(QMainWindow):
    """主界面实现"""

    def __init__(self, server_path: str):
        super().__init__()
        self.setWindowTitle("MCP客户端")
        self.setGeometry(100, 100, 800, 600)

        # 创建工作器和线程
        self.worker = MCPClientWorker(server_path)
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)

        # 创建UI组件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # 连接状态区域
        self.connection_layout = QHBoxLayout()
        self.connect_button = QPushButton("连接服务器")
        self.status_label = QLabel("状态: 未连接")
        self.connection_layout.addWidget(self.connect_button)
        self.connection_layout.addWidget(self.status_label)

        # 工具列表区域
        self.tools_label = QLabel("可用工具:")
        self.tools_list = QTextEdit()
        self.tools_list.setReadOnly(True)

        # 查询区域
        self.query_label = QLabel("输入查询:")
        self.query_input = QLineEdit()
        self.submit_button = QPushButton("提交查询")

        # 响应区域
        self.response_label = QLabel("响应:")
        self.response_display = QTextEdit()
        self.response_display.setReadOnly(True)

        # 错误区域
        self.error_label = QLabel("错误信息:")
        self.error_display = QTextEdit()
        self.error_display.setReadOnly(True)
        self.error_display.setStyleSheet("color: red;")

        # 添加组件到布局
        self.layout.addLayout(self.connection_layout)
        self.layout.addWidget(self.tools_label)
        self.layout.addWidget(self.tools_list)
        self.layout.addWidget(self.query_label)
        self.layout.addWidget(self.query_input)
        self.layout.addWidget(self.submit_button)
        self.layout.addWidget(self.response_label)
        self.layout.addWidget(self.response_display)
        self.layout.addWidget(self.error_label)
        self.layout.addWidget(self.error_display)

        # 连接信号和槽
        self._connect_signals()

        # 启动工作线程
        self.worker_thread.start()

    def _connect_signals(self):
        """连接所有信号和槽"""
        # 连接按钮
        self.connect_button.clicked.connect(self.on_connect_clicked)

        # 查询按钮
        self.submit_button.clicked.connect(self.on_query_submit)

        # 工作线程信号
        self.worker.response_ready.connect(self.display_response)
        self.worker.error_occurred.connect(self.display_error)
        self.worker.tools_listed.connect(self.display_tools)
        self.worker.connection_status.connect(self.update_status)

    @pyqtSlot()
    def on_connect_clicked(self):
        """连接按钮点击处理"""
        self.connect_button.setEnabled(False)
        self.connect_button.setText("连接中...")
        self.status_label.setText("状态: 正在连接...")
        self.worker_thread.started.connect(self.worker.start_connection)
        self.worker_thread.start()

    @pyqtSlot()
    def on_query_submit(self):
        """提交查询处理"""
        query = self.query_input.text().strip()
        if query:
            self.worker.process_query(query)
            self.query_input.clear()

    @pyqtSlot(str)
    def display_response(self, text):
        """显示API响应"""
        self.response_display.append(f">> {text}\n")

    @pyqtSlot(str)
    def display_error(self, error):
        """显示错误信息"""
        self.error_display.append(f"错误: {error}")

    @pyqtSlot(list)
    def display_tools(self, tools):
        """显示可用工具列表"""
        self.tools_list.clear()
        self.tools_list.append("\n".join(tools))

    @pyqtSlot(str)
    def update_status(self, status):
        """更新连接状态"""
        self.status_label.setText(f"状态: {status}")
        if "已连接" in status:
            self.connect_button.setText("已连接")
            self.connect_button.setEnabled(False)
        elif "失败" in status:
            self.connect_button.setText("重试连接")
            self.connect_button.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 从配置获取服务器路径（示例）
    server_path = "server.py"

    # 创建主窗口
    window = MainWindow(server_path)
    window.show()

    sys.exit(app.exec())
