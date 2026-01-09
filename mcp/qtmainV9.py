import sys
import asyncio
from contextlib import AsyncExitStack
from typing import Optional, Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QProcess
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QPushButton, QLineEdit
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import Anthropic
from dotenv import load_dotenv
import multiprocessing
from multiprocessing.connection import Connection
import pickle

load_dotenv()


class MCPClientWorkerProcess(multiprocessing.Process):
    """运行在独立进程中的工作器"""

    def __init__(self, server_script_path: str, conn: Connection):
        super().__init__()
        self.server_script_path = server_script_path
        self.conn = conn
        self.daemon = True  # 确保主进程退出时子进程也会退出

    def run(self):
        """进程主循环"""
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        worker = ProcessWorker(self.server_script_path, self.conn)
        loop.run_until_complete(worker.run())


class ProcessWorker:
    """实际执行工作的异步类，运行在子进程中"""

    def __init__(self, server_script_path: str, conn: Connection):
        self.server_script_path = server_script_path
        self.conn = conn
        self.session: Optional[ClientSession] = None
        self.anthropic = Anthropic()
        self.available_tools: list = []
        self._running = True
        self._exit_stack: Optional[AsyncExitStack] = None

    async def run(self):
        """主工作循环"""
        try:
            await self._connect_to_server()

            while self._running:
                if self.conn.poll(0.1):  # 非阻塞检查消息
                    try:
                        msg = self.conn.recv()
                        if msg['type'] == 'query':
                            result = await self._process_query_async(msg['data'])
                            self.conn.send({'type': 'response', 'data': result})
                        elif msg['type'] == 'stop':
                            break
                    except (EOFError, ConnectionError):
                        break
                await asyncio.sleep(0.1)

        except Exception as e:
            self.conn.send({'type': 'error', 'data': str(e)})
        finally:
            await self._close_resources()
            self.conn.send({'type': 'shutdown_complete'})

    async def _connect_to_server(self):
        """建立服务器连接"""
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
            self._exit_stack = AsyncExitStack()
            stdio_transport = await self._exit_stack.enter_async_context(stdio_client(server_params))
            stdio, write = stdio_transport
            self.session = await self._exit_stack.enter_async_context(ClientSession(stdio, write))
            await self.session.initialize()
            response = await self.session.list_tools()
            self.available_tools = [{
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            } for tool in response.tools]
            self.conn.send({'type': 'tools_listed', 'data': [tool["name"] for tool in self.available_tools]})
        except Exception as e:
            self.conn.send({'type': 'error', 'data': f"连接错误: {str(e)}"})

    async def _process_query_async(self, query: str) -> str:
        """处理查询的核心逻辑"""
        try:
            tool_result = await self._call_tool_async("get_alerts", {"state": "CA"})
            self.conn.send({'type': 'tool_result', 'data': tool_result})
            return "get tool result ok"
        except Exception as e:
            return f"处理错误: {str(e)}"

    async def _call_tool_async(self, tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
        """异步调用工具"""
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

    async def _close_resources(self):
        """关闭所有资源"""
        try:
            if self._exit_stack:
                await self._exit_stack.aclose()
        except Exception as e:
            self.conn.send({'type': 'error', 'data': f"资源关闭错误: {str(e)}"})
        finally:
            self._exit_stack = None
            self.session = None


class MCPClientWorker(QObject):
    """主进程中的工作器代理，与子进程通信"""

    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    tools_listed = pyqtSignal(list)
    tool_result_received = pyqtSignal(dict)
    shutdown_complete = pyqtSignal()

    def __init__(self, server_script_path: str):
        super().__init__()
        self.server_script_path = server_script_path
        self._process = None
        self._parent_conn = None
        self._running = False

    @pyqtSlot()
    def start_connection(self):
        """启动子进程"""
        if self._running:
            return
        self._parent_conn, child_conn = multiprocessing.Pipe()
        self._process = MCPClientWorkerProcess(self.server_script_path, child_conn)
        self._process.start()
        self._running = True

    @pyqtSlot(str)
    def process_query(self, query: str):
        """发送查询到子进程"""
        if not self._running or not self._parent_conn:
            self.error_occurred.emit("工作进程未运行")
            return
        try:
            self._parent_conn.send({'type': 'query', 'data': query})
        except Exception as e:
            self.error_occurred.emit(f"发送查询失败: {str(e)}")

    @pyqtSlot()
    def stop(self):
        """停止子进程"""
        if not self._running or not self._parent_conn:
            return
        try:
            self._parent_conn.send({'type': 'stop'})
            self._running = False
        except Exception as e:
            self.error_occurred.emit(f"停止工作进程失败: {str(e)}")

    def check_messages(self):
        """检查来自子进程的消息"""
        if not self._parent_conn or not self._running:
            return
        while self._parent_conn.poll():
            try:
                msg = self._parent_conn.recv()
                if msg['type'] == 'response':
                    self.response_ready.emit(msg['data'])
                elif msg['type'] == 'error':
                    self.error_occurred.emit(msg['data'])
                elif msg['type'] == 'tools_listed':
                    self.tools_listed.emit(msg['data'])
                elif msg['type'] == 'tool_result':
                    self.tool_result_received.emit(msg['data'])
                elif msg['type'] == 'shutdown_complete':
                    self.shutdown_complete.emit()
            except (EOFError, ConnectionError):
                self.error_occurred.emit("与工作进程的连接已断开")
                self._running = False
                break


class MainWindow(QMainWindow):
    def __init__(self, worker):
        super().__init__()
        self.worker = worker
        self.setup_ui()
        self.connect_signals()
        self._closing = False
        self._timer = None  # 用于定期检查消息的定时器

    def setup_ui(self):
        """初始化UI组件"""
        self.setWindowTitle("MCP客户端")
        self.setGeometry(100, 100, 800, 600)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        self.connect_btn = QPushButton("连接服务器")
        self.connect_btn.setFixedHeight(40)
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("输入查询内容...")
        self.query_input.setFixedHeight(40)
        self.send_query_btn = QPushButton("发送查询")
        self.send_query_btn.setFixedHeight(40)
        self.send_query_btn.setEnabled(False)
        self.status_display = QTextEdit()
        self.status_display.setReadOnly(True)
        layout.addWidget(self.connect_btn)
        layout.addWidget(self.query_input)
        layout.addWidget(self.send_query_btn)
        layout.addWidget(self.status_display)
        central_widget.setLayout(layout)

    def connect_signals(self):
        """连接信号与槽"""
        self.connect_btn.clicked.connect(self.on_connect_clicked)
        self.send_query_btn.clicked.connect(self.on_send_query_clicked)
        self.worker.response_ready.connect(self.display_response)
        self.worker.error_occurred.connect(self.display_error)
        self.worker.tools_listed.connect(self.display_tools)
        self.worker.tool_result_received.connect(self.display_tool_result)
        self.worker.shutdown_complete.connect(self.on_worker_shutdown)
        # 设置定时器定期检查消息
        self._timer = self.startTimer(100)  # 每100毫秒检查一次

    def timerEvent(self, event):
        """定时器事件处理"""
        self.worker.check_messages()

    def on_connect_clicked(self):
        """连接按钮点击处理"""
        self.status_display.append("正在连接服务器...")
        self.connect_btn.setEnabled(False)
        self.worker.start_connection()

    def on_send_query_clicked(self):
        """发送查询按钮点击处理"""
        query = self.query_input.text().strip()
        if query:
            self.status_display.append(f"用户查询: {query}")
            self.worker.process_query(query)
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
        if self._closing:
            self.close()

    def closeEvent(self, event):
        """窗口关闭时安全停止工作进程"""
        if self._closing:
            event.accept()
            return
        self._closing = True
        self.status_display.append("正在关闭...")

        # 停止工作进程
        self.worker.stop()

        # 延迟关闭，等待资源释放完成
        event.ignore()


if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # 确保在Windows上使用spawn方法
    if sys.platform == 'win32':
        multiprocessing.freeze_support()
        multiprocessing.set_start_method('spawn')

    app = QApplication(sys.argv)
    worker = MCPClientWorker("server.py")
    window = MainWindow(worker)
    window.show()
    sys.exit(app.exec())
