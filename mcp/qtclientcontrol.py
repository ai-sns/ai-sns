import subprocess
import sys
import asyncio
import multiprocessing
from contextlib import AsyncExitStack
from typing import Optional, Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QThread, QTimer
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit,
                             QVBoxLayout, QWidget, QPushButton, QLineEdit)
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import Anthropic
from dotenv import load_dotenv

from PyQt6.QtCore import QThread, pyqtSignal

class ConnectThread(QThread):
    """在单独的线程中执行连接操作"""
    output_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, script_path: str, parent=None):
        super().__init__(parent)
        self.script_path = script_path

    def run(self):
        """线程的执行函数"""
        try:
            # 启动子进程
            process = subprocess.Popen(
                [r'C:\dev\agi-ev\ai-sns\venv\Scripts\python.exe',
                 r'C:\dev\agi-ev\ai-sns\ai-sns\mcp\client_subprocess.py'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                encoding='utf-8'
            )

            # 向子进程发送连接命令
            input_data = '{"command": "connect", "args": {"path":"server.py"}}\n'
            process.stdin.write(input_data)
            process.stdin.flush()

            # 发送示例查询
            input_data = '{"command": "query", "args": {"text":"CA"}}\n'
            process.stdin.write(input_data)
            process.stdin.flush()

            # 可选：读取子进程的输出
            output, errors = process.communicate()

            if output:
                self.output_ready.emit(f"Output from subprocess: {output}")
            if errors:
                self.error_occurred.emit(f"Errors from subprocess: {errors}")

        except Exception as e:
            self.error_occurred.emit(f"连接过程中发生错误: {str(e)}")

load_dotenv()


class MCPClientWorker:
    """异步任务工作器，在独立进程中执行"""

    def __init__(self, server_script_path: str,
                 command_queue: multiprocessing.Queue,
                 response_queue: multiprocessing.Queue):
        """
        初始化工作器
        :param server_script_path: 服务器脚本路径
        :param command_queue: 用于接收命令的队列
        :param response_queue: 用于发送响应的队列
        """
        self.server_script_path = server_script_path
        self.command_queue = command_queue
        self.response_queue = response_queue
        self._running = True
        self.session: Optional[ClientSession] = None
        self._exit_stack: Optional[AsyncExitStack] = None
        self.anthropic = Anthropic()

    async def run(self):
        """主事件循环"""
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

        loop = asyncio.get_event_loop()
        await self._connect_to_server()

        # 主事件循环，处理命令和保持连接
        while self._running:
            # 非阻塞检查命令队列
            if not self.command_queue.empty():
                command = self.command_queue.get()
                if command[0] == 'query':
                    await self._process_query_async(command[1])
                elif command[0] == 'stop':
                    self._running = False

            await asyncio.sleep(0.1)

        # 清理资源
        await self._close_resources()
        self.response_queue.put(('shutdown_complete',))

    async def _connect_to_server(self):
        """建立服务器连接并获取工具列表"""
        try:
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
            # 使用AsyncExitStack管理资源
            self._exit_stack = AsyncExitStack()
            stdio_transport = await self._exit_stack.enter_async_context(stdio_client(server_params))
            stdio, write = stdio_transport
            self.session = await self._exit_stack.enter_async_context(ClientSession(stdio, write))
            await self.session.initialize()
            # 获取并缓存可用工具列表
            response = await self.session.list_tools()
            available_tools = [tool.name for tool in response.tools]
            self.response_queue.put(('tools_listed', available_tools))
        except Exception as e:
            self.response_queue.put(('error_occurred', f"连接错误: {str(e)}"))

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

    async def _process_query_async(self, query: str):
        """处理查询的核心逻辑，整合了工具调用功能"""
        try:
            # 示例工具调用
            tool_result = await self._call_tool_async("get_alerts", {"state": "CA"})
            self.response_queue.put(('tool_result_received', tool_result))
            self.response_queue.put(('response_ready', "get tool result ok"))
        except Exception as e:
            self.response_queue.put(('error_occurred', f"处理错误: {str(e)}"))

    async def _close_resources(self):
        """异步关闭所有资源"""
        try:
            if self._exit_stack:
                await self._exit_stack.aclose()
        except Exception as e:
            self.response_queue.put(('error_occurred', f"资源关闭错误: {str(e)}"))
        finally:
            self._exit_stack = None
            self.session = None


def worker_process_entry(server_script_path: str,
                         command_queue: multiprocessing.Queue,
                         response_queue: multiprocessing.Queue):
    """工作进程入口点"""
    worker = MCPClientWorker(server_script_path, command_queue, response_queue)
    asyncio.run(worker.run())


class ProcessManager(QObject):
    """管理工作进程和进程间通信"""
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    tools_listed = pyqtSignal(list)
    tool_result_received = pyqtSignal(dict)
    shutdown_complete = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.command_queue = multiprocessing.Queue()
        self.response_queue = multiprocessing.Queue()
        self.process = None
        self.poll_timer = None
        self.server_script_path = None

    def start(self, server_script_path: str):
        """启动工作进程"""
        self.server_script_path = server_script_path
        self.process = multiprocessing.Process(
            target=worker_process_entry,
            args=(self.server_script_path, self.command_queue, self.response_queue),
            daemon=True
        )
        self.process.start()

        # 设置定时器轮询响应队列
        self.poll_timer = QTimer()
        self.poll_timer.timeout.connect(self.check_responses)
        self.poll_timer.start(100)  # 每100ms检查一次

    def check_responses(self):
        """检查并处理来自工作进程的响应"""
        while not self.response_queue.empty():
            msg_type, data = self.response_queue.get()
            if msg_type == 'response_ready':
                self.response_ready.emit(data)
            elif msg_type == 'error_occurred':
                self.error_occurred.emit(data)
            elif msg_type == 'tools_listed':
                self.tools_listed.emit(data)
            elif msg_type == 'tool_result_received':
                self.tool_result_received.emit(data)
            elif msg_type == 'shutdown_complete':
                self.shutdown_complete.emit()
                if self.poll_timer:
                    self.poll_timer.stop()

    def send_query(self, query: str):
        """发送查询到工作进程"""
        self.command_queue.put(('query', query))

    def stop(self):
        """停止工作进程"""
        if self.process and self.process.is_alive():
            self.command_queue.put(('stop',))
            self.process.join(timeout=2.0)
            if self.process.is_alive():
                self.process.terminate()
            self.process = None
        if self.poll_timer:
            self.poll_timer.stop()
            self.poll_timer = None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.process_manager = ProcessManager(self)
        self._closing = False
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
        # 服务器路径输入
        self.server_path_input = QLineEdit()
        self.server_path_input.setPlaceholderText("输入服务器脚本路径...")
        self.server_path_input.setFixedHeight(40)
        self.server_path_input.setText("server.py")  # 默认值
        # 查询输入框
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("输入查询内容...")
        self.query_input.setFixedHeight(40)
        # 发送查询按钮
        self.send_query_btn = QPushButton("发送查询")
        self.send_query_btn.setFixedHeight(40)
        self.send_query_btn.setEnabled(False)
        # 状态显示区域
        self.status_display = QTextEdit()
        # self.status_display.setReadOnly(True)
        # 布局组装
        layout.addWidget(self.connect_btn)
        layout.addWidget(self.server_path_input)
        layout.addWidget(self.query_input)
        layout.addWidget(self.send_query_btn)
        layout.addWidget(self.status_display)
        central_widget.setLayout(layout)

    def connect_signals(self):
        """连接信号与槽"""
        self.connect_btn.clicked.connect(self.on_connect_clicked)
        self.send_query_btn.clicked.connect(self.on_send_query_clicked)
        self.process_manager.response_ready.connect(self.display_response)
        self.process_manager.error_occurred.connect(self.display_error)
        self.process_manager.tools_listed.connect(self.display_tools)
        self.process_manager.tool_result_received.connect(self.display_tool_result)
        self.process_manager.shutdown_complete.connect(self.on_worker_shutdown)

    def on_connect_clicked(self):
        """连接按钮点击处理"""
        script_path = self.server_path_input.text().strip()
        if script_path:
            self.connect_thread = ConnectThread(script_path)
            self.connect_thread.output_ready.connect(self.display_response)
            self.connect_thread.error_occurred.connect(self.display_error)
            self.connect_thread.start()  # 启动线程
        else:
            self.display_error("服务器脚本路径不能为空")

    def on_send_query_clicked(self):
        """发送查询按钮点击处理"""
        query = self.query_input.text().strip()
        if query:
            self.status_display.append(f"用户查询: {query}")

            # 连接一次性信号，处理完成后自动断开
            def handle_response(response):
                print("收到响应:", response)
                self.process_manager.response_ready.disconnect(handle_response)

            self.process_manager.response_ready.connect(handle_response)


            self.process_manager.send_query(query)
        else:
            self.status_display.append("查询内容不能为空")

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
        self.send_query_btn.setEnabled(True)

    def display_tool_result(self, result):
        """显示工具调用结果"""
        if "error" in result:
            self.status_display.append(f"工具调用错误: {result['tool_name']} - {result['error']}")
        else:
            self.status_display.append(
                f"工具调用成功: {result['tool_name']}\n"
                f"参数: {result['args']}\n"
                f"结果: {result['result']}"
            )

    def on_worker_shutdown(self):
        """工作进程关闭完成时的处理"""
        self.connect_btn.setEnabled(True)
        self.send_query_btn.setEnabled(False)
        if self._closing:
            self.close()

    def closeEvent(self, event):
        """窗口关闭时安全停止工作进程"""
        if self._closing:
            event.accept()
            return
        self._closing = True
        self.status_display.append("正在关闭...")
        self.process_manager.stop()
        event.accept()


if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
