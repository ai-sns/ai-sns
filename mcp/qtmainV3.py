import sys
import asyncio
from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QTextEdit, QLineEdit, QLabel, QHBoxLayout,
    QMessageBox
)
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import Anthropic
from dotenv import load_dotenv
from contextlib import AsyncExitStack
import logging
import traceback

# 配置日志记录
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
load_dotenv()  # 加载环境变量


class MCPClientWorker(QObject):
    """异步任务工作器，在独立线程中运行事件循环"""
    response_ready = pyqtSignal(str)  # 处理完成信号
    error_occurred = pyqtSignal(str)  # 错误信号
    tools_listed = pyqtSignal(list)  # 工具列表信号
    connection_status = pyqtSignal(str)  # 连接状态信号
    connection_completed = pyqtSignal(bool)  # 连接完成信号

    def __init__(self, server_script_path: str):
        super().__init__()
        self.server_script_path = server_script_path
        self.loop = asyncio.new_event_loop()
        self.session: Optional[ClientSession] = None
        self.anthropic = Anthropic()
        self.connected = False
        self.exit_stack = AsyncExitStack()
        self.event_loop_running = False

    @pyqtSlot()
    def start_connection(self):
        """启动异步连接（在工作者线程中调用）"""
        try:
            # 确保设置事件循环
            asyncio.set_event_loop(self.loop)

            # 启动事件循环（在后台持续运行）
            self.loop.create_task(self._connect_to_server())
            self.loop.run_forever()
            self.event_loop_running = True
            logger.debug("事件循环已启动")
        except Exception as e:
            error_msg = f"启动事件循环错误: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            self.connection_status.emit("连接失败")
            self.connection_completed.emit(False)

    async def _connect_to_server(self):
        """建立服务器连接"""
        try:
            self.connection_status.emit("正在连接服务器...")
            logger.debug("开始连接服务器")

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

            # 添加超时处理
            try:
                # 尝试连接服务器，设置10秒超时
                stdio_transport = await asyncio.wait_for(
                    self.exit_stack.enter_async_context(stdio_client(server_params)),
                    timeout=10.0
                )
            except asyncio.TimeoutError:
                raise TimeoutError("连接服务器超时，请检查服务器是否已启动")

            stdio, write = stdio_transport
            self.session = await self.exit_stack.enter_async_context(ClientSession(stdio, write))

            # 初始化会话，设置5秒超时
            try:
                await asyncio.wait_for(self.session.initialize(), timeout=5.0)
            except asyncio.TimeoutError:
                raise TimeoutError("会话初始化超时")

            # 获取可用工具列表，设置5秒超时
            try:
                response = await asyncio.wait_for(self.session.list_tools(), timeout=5.0)
            except asyncio.TimeoutError:
                raise TimeoutError("获取工具列表超时")

            self.connected = True
            self.connection_status.emit("已连接到服务器")
            self.tools_listed.emit([tool.name for tool in response.tools])
            self.connection_completed.emit(True)
            logger.info("服务器连接成功")

        except Exception as e:
            error_msg = f"连接过程中出错: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            self.connection_status.emit("连接失败")
            self.connection_completed.emit(False)
            # 清理资源
            try:
                await self.exit_stack.aclose()
            except Exception as cleanup_error:
                logger.error(f"清理资源时出错: {cleanup_error}")

    @pyqtSlot(str)
    def process_query(self, query: str):
        """处理用户查询（线程安全入口点）"""
        try:
            if not self.connected:
                self.error_occurred.emit("错误：请先连接服务器")
                return

            logger.debug(f"开始处理查询: {query}")

            # 确保事件循环正在运行
            if not self.event_loop_running:
                logger.error("事件循环未运行，无法处理查询")
                self.error_occurred.emit("内部错误：事件循环未运行")
                return

            # 创建任务并添加到事件循环
            task = self.loop.create_task(self._process_query_async(query))
            task.add_done_callback(self._handle_query_result)

            logger.debug(f"查询任务已提交到事件循环: {task}")

        except Exception as e:
            error_msg = f"提交查询任务时出错: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)

    async def _process_query_async(self, query: str) -> str:
        """异步处理查询的核心逻辑"""
        try:
            logger.debug(f"进入查询处理函数: {query}")

            # 1. 首先获取可用工具定义
            logger.debug("获取可用工具列表...")
            tools_response = await self.session.list_tools()
            available_tools = [{
                "name": t.name,
                "description": t.description,
                "input_schema": t.inputSchema
            } for t in tools_response.tools]

            logger.debug(f"可用工具: {[t['name'] for t in available_tools]}")

            # 2. 调用Claude API
            logger.debug("调用Claude API...")
            response = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[{"role": "user", "content": query}],
                tools=available_tools
            )

            logger.debug(f"收到Claude响应: {response}")

            # 3. 处理多内容响应
            final_response = []
            for content in response.content:
                if content.type == 'text':
                    final_response.append(content.text)
                elif content.type == 'tool_use':
                    # 处理工具调用
                    tool_name = content.name
                    tool_args = content.input
                    logger.debug(f"调用工具: {tool_name} 参数: {tool_args}")

                    # 执行工具调用
                    tool_result = await self.session.call_tool(tool_name, tool_args)
                    logger.debug(f"工具调用结果: {tool_result}")

                    # 更新对话上下文
                    response = self.anthropic.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=1000,
                        messages=[
                            {"role": "user", "content": query},
                            {"role": "assistant", "content": f"调用工具 {tool_name}"},
                            {"role": "user", "content": f"工具结果: {tool_result}"}
                        ]
                    )
                    final_response.append(response.content[0].text)

            result = "\n".join(final_response)
            logger.debug(f"最终响应: {result}")
            return result

        except Exception as e:
            error_msg = f"处理查询时出错: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            return error_msg

    def _handle_query_result(self, future):
        """处理查询结果的回调"""
        try:
            result = future.result()
            logger.debug(f"查询处理完成，结果长度: {len(result)}")
            self.response_ready.emit(result)
        except Exception as e:
            error_msg = f"处理查询结果时出错: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)

    @pyqtSlot()
    def cleanup(self):
        """清理资源"""
        try:
            logger.debug("清理资源...")
            # 停止事件循环
            if self.event_loop_running:
                self.loop.call_soon_threadsafe(self.loop.stop)
                self.event_loop_running = False
                logger.debug("事件循环已停止")

            # 关闭异步退出栈
            asyncio.run_coroutine_threadsafe(self.exit_stack.aclose(), self.loop).result()
            logger.debug("资源清理完成")
        except Exception as e:
            logger.error(f"清理资源时出错: {e}")


class MainWindow(QMainWindow):
    """主界面实现"""

    def __init__(self, server_path: str):
        super().__init__()
        self.setWindowTitle("MCP客户端")
        self.setGeometry(100, 100, 800, 600)
        self.server_path = server_path

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
        self.tools_list.setMinimumHeight(100)

        # 查询区域
        self.query_label = QLabel("输入查询:")
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("在此输入您的问题...")
        self.submit_button = QPushButton("提交查询")

        # 响应区域
        self.response_label = QLabel("响应:")
        self.response_display = QTextEdit()
        self.response_display.setReadOnly(True)

        # 错误区域
        self.error_label = QLabel("错误信息:")
        self.error_display = QTextEdit()
        self.error_display.setReadOnly(True)
        self.error_display.setStyleSheet("color: red; background-color: #ffeeee;")
        self.error_display.setMaximumHeight(150)

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

        # 初始化工作线程
        self._init_worker()

        # 禁用查询功能直到连接成功
        self._set_query_enabled(False)

    def _init_worker(self):
        """初始化工作线程"""
        self.worker = MCPClientWorker(self.server_path)
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)

        # 连接工作线程信号
        self.worker.response_ready.connect(self.display_response)
        self.worker.error_occurred.connect(self.display_error)
        self.worker.tools_listed.connect(self.display_tools)
        self.worker.connection_status.connect(self.update_status)
        self.worker.connection_completed.connect(self.on_connection_completed)

        # 启动工作线程
        self.worker_thread.started.connect(self.worker.start_connection)
        self.worker_thread.start()

    def _connect_signals(self):
        """连接所有信号和槽"""
        # 连接按钮
        self.connect_button.clicked.connect(self.on_connect_clicked)

        # 查询按钮
        self.submit_button.clicked.connect(self.on_query_submit)

        # 按回车键提交查询
        self.query_input.returnPressed.connect(self.on_query_submit)

    def _set_query_enabled(self, enabled: bool):
        """设置查询功能启用状态"""
        self.query_input.setEnabled(enabled)
        self.submit_button.setEnabled(enabled)
        if enabled:
            self.query_input.setFocus()

    @pyqtSlot()
    def on_connect_clicked(self):
        """连接按钮点击处理"""
        self.connect_button.setEnabled(False)
        self.connect_button.setText("连接中...")
        self.status_label.setText("状态: 正在连接...")
        self.error_display.clear()
        self.response_display.clear()
        self.tools_list.clear()

        # 启动连接过程
        self.worker.start_connection()

    @pyqtSlot(bool)
    def on_connection_completed(self, success: bool):
        """连接完成处理"""
        if success:
            self._set_query_enabled(True)
            self.status_label.setText("状态: 已连接")
            self.connect_button.setText("已连接")
        else:
            self.connect_button.setEnabled(True)
            self.connect_button.setText("重试连接")
            self.status_label.setText("状态: 连接失败")

    @pyqtSlot()
    def on_query_submit(self):
        """提交查询处理"""
        query = self.query_input.text().strip()
        if query:
            self.response_display.append(f">> 用户: {query}")
            self.worker.process_query(query)
            self.query_input.clear()

    @pyqtSlot(str)
    def display_response(self, text):
        """显示API响应"""
        self.response_display.append(f">> 助手: {text}\n")
        self.response_display.verticalScrollBar().setValue(
            self.response_display.verticalScrollBar().maximum()
        )

    @pyqtSlot(str)
    def display_error(self, error):
        """显示错误信息"""
        self.error_display.append(error)
        self.error_display.verticalScrollBar().setValue(
            self.error_display.verticalScrollBar().maximum()
        )

        # 对于连接错误，显示警告对话框
        if "连接错误" in error or "连接失败" in error:
            QMessageBox.warning(self, "连接错误", error)

    @pyqtSlot(list)
    def display_tools(self, tools):
        """显示可用工具列表"""
        self.tools_list.clear()
        self.tools_list.append("\n".join(tools))

    @pyqtSlot(str)
    def update_status(self, status):
        """更新连接状态"""
        self.status_label.setText(f"状态: {status}")

    def closeEvent(self, event):
        """窗口关闭时清理资源"""
        logger.debug("关闭窗口，清理资源...")
        self.worker.cleanup()
        self.worker_thread.quit()
        self.worker_thread.wait()
        super().closeEvent(event)


if __name__ == "__main__":

    app = QApplication(sys.argv)

    # 从配置获取服务器路径（示例）
    server_path = "server.py"

    # 创建主窗口
    window = MainWindow(server_path)
    window.show()

    sys.exit(app.exec())
