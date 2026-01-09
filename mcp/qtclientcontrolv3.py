import json
import subprocess
import sys
import asyncio
import multiprocessing
import time
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
        self.process = None

    def start_process(self):
        """启动子进程"""
        try:
            # Starting a subprocess with pipes configured for communication
            self.process = subprocess.Popen(
                [
                    r'C:\dev\agi-ev\ai-sns\venv\Scripts\python.exe',
                    r'C:\dev\agi-ev\ai-sns\ai-sns\mcp\client_subprocessv2.py'
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0,  # 改为无缓冲
                universal_newlines=True,
                encoding='utf-8'
            )
            return True
        except Exception as e:
            self.error_occurred.emit(f"启动子进程失败: {str(e)}")
            return False

    def send_command(self, process, command, timeout=10):
        """发送命令并读取响应，添加超时控制"""
        try:
            print(f"发送命令: {command.strip()}")

            # 写入命令
            process.stdin.write(command)
            process.stdin.flush()

            # 使用非阻塞方式读取输出
            output_lines = []
            error_lines = []

            start_time = time.time()
            json_response_found = False

            # 读取stdout，直到找到JSON响应
            while time.time() - start_time < timeout:
                # 检查进程是否还活着
                if process.poll() is not None:
                    print("子进程已结束")
                    break

                try:
                    # Windows系统的处理方式
                    try:
                        line = process.stdout.readline()
                        if line:
                            line_stripped = line.strip()
                            output_lines.append(line)
                            print(f"读取输出行: {line_stripped}")

                            # 检查是否是JSON响应（命令的最终结果）
                            if line_stripped.startswith('{') and line_stripped.endswith('}'):
                                try:
                                    json.loads(line_stripped)  # 验证是否为有效JSON
                                    json_response_found = True
                                    print(f"找到JSON响应: {line_stripped}")
                                    break  # 找到JSON响应，结束读取
                                except json.JSONDecodeError:
                                    pass  # 不是有效JSON，继续读取

                        else:
                            # 没有更多输出，等待一下
                            time.sleep(0.1)
                    except Exception as read_error:
                        print(f"读取stdout时出错: {read_error}")
                        time.sleep(0.1)

                except Exception as e:
                    print(f"读取过程中出错: {e}")
                    break

            # 如果没有找到JSON响应，再等待一点时间
            if not json_response_found:
                print("未找到JSON响应，继续等待...")
                additional_wait = 2  # 额外等待2秒
                additional_start = time.time()

                while time.time() - additional_start < additional_wait:
                    try:
                        line = process.stdout.readline()
                        if line:
                            line_stripped = line.strip()
                            output_lines.append(line)
                            print(f"额外读取: {line_stripped}")

                            if line_stripped.startswith('{') and line_stripped.endswith('}'):
                                try:
                                    json.loads(line_stripped)
                                    json_response_found = True
                                    print(f"找到延迟JSON响应: {line_stripped}")
                                    break
                                except json.JSONDecodeError:
                                    pass
                        else:
                            time.sleep(0.1)
                    except:
                        time.sleep(0.1)

            output = ''.join(output_lines)
            errors = ''.join(error_lines)

            print(f"命令执行完成，输出长度: {len(output)}, 错误长度: {len(errors)}, JSON响应: {json_response_found}")

            return output, errors

        except Exception as e:
            error_msg = f"发送命令时出错: {str(e)}"
            print(error_msg)
            return "", error_msg

    def run(self):
        """主执行方法"""
        try:
            # 启动子进程
            if not self.start_process():
                return

            print("子进程启动成功")

            # 等待子进程初始化
            time.sleep(1)

            # 发送连接命令
            connect_command = '{"command": "connect", "args": {"path":"server.py"}}\n'
            print("准备发送连接命令...")

            connect_output, connect_errors = self.send_command(self.process, connect_command)

            print("Connect Output:", connect_output)
            print("Connect Errors:", connect_errors)

            if connect_errors:
                self.error_occurred.emit(f"连接错误: {connect_errors}")
            else:
                self.output_ready.emit(f"连接输出: {connect_output}")



        except Exception as e:
            error_msg = f"线程执行错误: {str(e)}"
            print(error_msg)
            self.error_occurred.emit(error_msg)


    def query(self):
        """主执行方法"""
        try:

            # 等待子进程初始化
            time.sleep(1)



            # 发送查询命令
            query_command = '{"command": "query", "args": {"text":"CA"}}\n'
            print("准备发送查询命令...")

            query_output, query_errors = self.send_command(self.process, query_command)

            print("Query Output:", query_output)
            print("Query Errors:", query_errors)

            if query_errors:
                self.error_occurred.emit(f"查询错误: {query_errors}")
            else:
                self.output_ready.emit(f"查询输出: {query_output}")

        except Exception as e:
            error_msg = f"线程执行错误: {str(e)}"
            print(error_msg)
            self.error_occurred.emit(error_msg)

        finally:
            # 清理子进程
            if self.process:
                try:
                    print("正在清理子进程...")
                    if self.process.stdin:
                        self.process.stdin.close()
                    if self.process.stdout:
                        self.process.stdout.close()
                    if self.process.stderr:
                        self.process.stderr.close()

                    # 等待进程结束
                    self.process.terminate()
                    self.process.wait(timeout=5)
                    print("子进程清理完成")
                except Exception as e:
                    print(f"清理子进程时出错: {e}")
                    # 强制杀死进程
                    try:
                        self.process.kill()
                    except:
                        pass


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
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
        self.send_query_btn.setEnabled(True)
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
        """连接按钮点击处理"""
        script_path = self.server_path_input.text().strip()
        if script_path:
            self.connect_thread.query()  # 启动线程
        else:
            self.display_error("服务器脚本路径不能为空")

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
