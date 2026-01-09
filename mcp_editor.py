import subprocess
import datetime
import sys
import json
import signal
import threading
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QPalette, QColor
from i18n import lt

from pluginsmanager.plugins_gui.plugin_interface import PluginInterface
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QGroupBox, QLineEdit, QRadioButton,QCheckBox, QLabel, QDialog
from PyQt6 import QtWidgets
from pluginsmanager.plugins_gui.plugins import syntax_pars
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QPlainTextEdit
import os
import webbrowser
from db.DBFactory import query_mcp_mng,add_mcp_mng,update_mcp_mng
from util import generate_random_id
import autogen
from autogen import AssistantAgent, UserProxyAgent

from pathlib import Path

from autogen.coding import CodeBlock, LocalCommandLineCodeExecutor



class CodeEditor(QWidget,PluginInterface):
    def __init__(self,mcp_manager):
        super().__init__()
        self.mcp_manager=mcp_manager
        self.mcp_id = ""
        self.changesSaved=True
        self.inspector_running = False
        self.process = None  # 用于存储子进程的引用
        # 初始化用户界面
        # self.init_ui(content)

    def re_init(self):
        self.filename = ""
        self.changesSaved = True
        self.is_first = False
        self.editor.setPlainText("")
        self.mcp_name_input.setText("")
        self.instruction_input.setText("")
        self.mcp_description_input.setText("")
        self.publish_check.setChecked(False)
        self.sns_check.setChecked(False)
        self.detail_text_edit.setPlainText("")

    def create_widget(self, *args, **kwagrs):
        content=kwagrs.get("content","")
        # 创建主布局
        # 创建主布局
        layout = QVBoxLayout()

        # 创建文本编辑器控件
        self.editor = QPlainTextEdit()
        self.editor.setObjectName("code_editor")
        # 设置文本编辑器样式
        self.editor.setStyleSheet("""QPlainTextEdit{
                    font-family: 'Consolas'; 
                    color: #ccc; 
                    background-color: #2b2b2b;
                }""")

        # 设置语法高亮
        self.highlighter = syntax_pars.PythonHighlighter(self.editor.document())

        # 设置初始内容
        self.editor.setPlainText(content)
        self.editor.textChanged.connect(self.changed)

        # 将编辑器添加到布局
        layout.addWidget(self.editor)

        # 创建 QGroupBox
        group_box = QGroupBox("配置信息")  # 设置 QGroupBox 的标题
        group_layout = QVBoxLayout()  # 创建 GroupBox 的布局

        # 创建水平布局，用于放置函数名输入框和发布单选按钮
        mcp_layout = QHBoxLayout()

        # 创建标签（函数名）
        mcp_label = QLabel("名称:")
        mcp_layout.addWidget(mcp_label)

        # 创建单行输入框（函数名）
        self.mcp_name_input = QLineEdit()
        self.mcp_name_input.setPlaceholderText("请输入名称")
        palette = self.mcp_name_input.palette()
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("gray"))  # 可以改为其他颜色
        self.mcp_name_input.setPalette(palette)

        mcp_layout.addWidget(self.mcp_name_input)

        self.instruction_input = QLineEdit()
        self.instruction_input.setPlaceholderText(lt("Input instrunction and how to call,for example  tq:the city to search","请输入指令及格式如：tq:要查询的城市"))
        palette = self.instruction_input.palette()
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("gray"))  # 可以改为其他颜色
        self.instruction_input.setPalette(palette)

        mcp_layout.addWidget(self.instruction_input)

        group_layout.addLayout(mcp_layout)

        mcp_desc_layout = QHBoxLayout()
        mcp_description_label = QLabel("简介:")
        mcp_desc_layout.addWidget(mcp_description_label)

        # 创建单行输入框（函数名）
        self.mcp_description_input = QLineEdit()
        self.mcp_description_input.setPlaceholderText("简明扼要")
        self.mcp_description_input.setMaxLength(350)
        palette = self.mcp_description_input.palette()
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("gray"))  # 可以改为其他颜色
        self.mcp_description_input.setPalette(palette)

        mcp_desc_layout.addWidget(self.mcp_description_input)

        group_layout.addLayout(mcp_desc_layout)

        # # 创建状态标签（状态）
        # status_label = QLabel("状态:")
        # mcp_layout.addWidget(status_label)

        # # 创建单选按钮（发布）
        # self.publish_radio = QRadioButton("发布")
        # mcp_layout.addWidget(self.publish_radio)
        # # 将函数布局添加到 GroupBox 布局中

        #
        # if self.mcp_manager.type_str=="2":
        #     status_label.setHidden(True)
        #     self.publish_radio.setHidden(True)
        detail_layout = QHBoxLayout()
        # 创建多行文本框（描述）
        mcp_detail_label = QLabel("工具:")

        self.detail_text_edit = QTextEdit()
        self.detail_text_edit.setPlaceholderText("请输入工具的schema描述")
        palette = self.detail_text_edit.palette()
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("gray"))  # 可以改为其他颜色
        self.detail_text_edit.setPalette(palette)
        self.detail_text_edit.setFixedHeight(70)  # 设置多行文本框的高度
        detail_layout.addWidget(mcp_detail_label)

        detail_layout.addWidget(self.detail_text_edit)

        group_layout.addLayout(detail_layout)
        # 将 GroupBox 的布局应用到 QGroupBox
        group_box.setLayout(group_layout)
        group_box.setFixedHeight(170)  # 限制 QGroupBox 的高度

        # 将 QGroupBox 添加到主布局
        layout.addWidget(group_box)





        # 创建按钮的水平布局
        button_layout = QHBoxLayout()

        # 创建添加按钮
        return_button = QPushButton("关闭")
        return_button.clicked.connect(self.go_back)  # 连接按钮点击事件到添加函数
        button_layout.addWidget(return_button)

        # 创建保存按钮
        save_button = QPushButton("保存")
        save_button.clicked.connect(self.save_file)  # 连接保存事件
        button_layout.addWidget(save_button)

        # 创建运行按钮
        preview_button = QPushButton("验证")
        preview_button.clicked.connect(self.run_mcp)  # 连接预览事件
        button_layout.addWidget(preview_button)

        # 创建运行按钮
        inspector_button = QPushButton("调试")
        inspector_button.clicked.connect(self.inspect_mcp)  # 连接预览事件
        button_layout.addWidget(inspector_button)


        if self.mcp_manager.type_str=="2":
            preview_button.setHidden(True)

        # 创建单选按钮（发布）
        # status_label = QLabel("状态:")
        # mcp_layout.addWidget(status_label)

        self.publish_check = QCheckBox(lt("Published", "发布"))

        # 将函数布局添加到 GroupBox 布局中
        # button_layout.addWidget(status_label)
        button_layout.addWidget(self.publish_check)

        if self.mcp_manager.type_str == "2":
            # status_label.setHidden(True)
            self.publish_check.setHidden(True)

        self.sns_check = QCheckBox(lt("Used in SNS","能被用于SNS"))
        button_layout.addWidget(self.sns_check)



        # 将按钮布局添加到主布局
        layout.addLayout(button_layout)

        # 设置窗口布局
        self.setLayout(layout)
        # 设置窗口标题
        self.setWindowTitle("Code Editor")
        # 设置窗口大小
        self.resize(600, 400)

    def go_back(self):

        self.parent().setCurrentWidget(self.mcp_manager)

    def changed(self):
        self.changesSaved = False


    def add_hello_world(self, editor=None):
        """向文本编辑器中添加 'Hello World2'"""
        parent = self.parent().parent()
        if parent:
            # 获取并打印父控件的类型
            print(f"按钮的父控件类型是: {type(parent).__name__}")
            current_index = parent.currentIndex()  # 获取当前选中的 Tab 的索引
            if current_index != -1:  # 确保有 Tab 被选中
                parent.removeTab(current_index)  # 移除当前选中的 Tab
        else:
            print("按钮没有父控件。")

        if editor is None:
            # 如果没有传入 editor，则向主编辑器添加
            editor = self.editor
        editor.appendPlainText("Hello World2")




    def save_file(self):
        mcp_id=""
        if not self.filename:
            mcp_id = generate_random_id()
            name = self.mcp_name_input.text()
            instruction = self.instruction_input.text()
            self.mcp_id = mcp_id
            self.filename = os.path.join(os.getcwd(), "mcp",   name + ".json")
            #coding

            description = self.mcp_description_input.text()
            detail = self.detail_text_edit.toPlainText()
            file_path = name
            requirement = ""
            parameter = ""
            if self.publish_check.isChecked():
                mcp_type = "1"
            else:
                mcp_type="0"

            if self.sns_check.isChecked():
                used_in_sns = 1
            else:
                used_in_sns=0


            mcp_event = ""
            creator = ""
            record_id=add_mcp_mng(mcp_id, name,instruction, file_path,requirement,parameter, description,detail, mcp_type, mcp_event,
                     creator,used_in_sns)
            self.is_first = True
        else:
            mcp_id = self.mcp_id
            name = self.mcp_name_input.text()
            instruction = self.instruction_input.text()
            description = self.mcp_description_input.text()
            detail = self.detail_text_edit.toPlainText()
            requirement = ""
            parameter = ""
            if self.publish_check.isChecked():
                mcp_type = "1"
            else:
                mcp_type = "0"

            if self.sns_check.isChecked():
                used_in_sns = 1
            else:
                used_in_sns=0


            create_time = datetime.datetime.now()
            update_mcp_mng(mcp_id,name=name,instruction=instruction,description=description,detail=detail,mcp_type=mcp_type,create_time=create_time,used_in_sns=used_in_sns)

        if self.filename:

            with open(self.filename, 'w', encoding='utf-8') as file:
                file.write(self.editor.toPlainText())  # 将文本写入文件

            self.changesSaved = True

        if self.is_first == True:

            self.is_first = False


    def run_mcp(self):
        """保存文件并在浏览器中打开"""
        content = self.editor.toPlainText()
        trimmed_content = content.strip()
        code = trimmed_content
        last_str =code[-7:]
        if last_str.lower()=="</html>":
            type_str = "html"
        else:
            type_str = "python"



        if type_str=="html":
            self.save_file()  # 先保存文件
            # 获取文件路径
            file_path = os.path.join("coding", "mycode.html")
            webbrowser.open(f"file://{os.path.abspath(file_path)}")  # 使用默认浏览器打开文件
        else:
            work_dir = Path("coding")
            work_dir.mkdir(exist_ok=True)


            executor = LocalCommandLineCodeExecutor(work_dir=work_dir)


            execute_result=executor.execute_code_blocks(
                code_blocks=[
                    CodeBlock(language="python", code=code),
                ]
            )
            print(execute_result)
            print("exit_code",execute_result.exit_code)
            print("output",execute_result.output)
            print("code_file",execute_result.code_file)

            self.console = QDialog()
            self.te = QTextEdit(self.console)
            self.te.append(f"exit_code:\n{execute_result.exit_code}\n")
            self.te.append(f"code_file:\n{execute_result.code_file}\n")
            self.te.append(f"output:\n{execute_result.output}")
            self.te.setReadOnly(True)
            vl = QVBoxLayout()
            vl.addWidget(self.te)
            self.console.setLayout(vl)

            self.console.setWindowTitle("Output Console")
            self.console.resize(QSize(1024, 500))
            self.console.exec()
            # self.console.raise_()

    def inspect_mcpbak(self):
        subprocess.Popen(
            r'cmd /c "npx @modelcontextprotocol/inspector --config C:\Users\IDD\mcp.json --server howtocook-mcp"',
            shell=True
        )

        pass

    def inspect_mcpbak2(self):
        # 启动子进程
        if self.process is None or self.process.poll() is not None:  # 检查是否已有子进程在运行
            self.process = subprocess.Popen(
                r'cmd /c "npx @modelcontextprotocol/inspector --config C:\Users\IDD\mcp.json --server howtocook-mcp"',
                shell=True
            )
            print("子进程已启动。")
            webbrowser.open("http://127.0.0.1:6274/")  # 使用默认浏览器打开文件
        else:
            print("子进程已经在运行，无法重新启动。")
            self.stop_mcp()

    def stop_mcpbak2(self):
        # 关闭子进程
        if self.process is not None:
            try:
                self.process.terminate()  # 尝试正常终止子进程
                self.process.wait()  # 等待子进程结束
                self.process = None  # 清空进程引用
                print("子进程已停止。")
            except Exception as e:
                print(f"停止子进程时发生错误: {e}")
        else:
            print("没有正在运行的子进程。")

    def inspect_mcpbakok(self):
        """启动MCP检查器子进程"""
        if self.process is None or self.process.poll() is not None:
            try:
                # 使用列表形式传递参数更安全，避免shell注入风险
                # 分离命令和参数，提高可读性和安全性
                self.process = subprocess.Popen(
                    [
                        'cmd', '/c',
                        'npx', '@modelcontextprotocol/inspector',
                        '--config', r'C:\Users\IDD\mcp.json',
                        '--server', 'howtocook-mcp'
                    ],
                    shell=False,  # 禁用shell更安全
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP  # Windows下允许发送CTRL_BREAK信号
                )
                print("子进程已启动。PID:", self.process.pid)
                webbrowser.open("http://127.0.0.1:6274/")  # 使用默认浏览器打开文件
            except Exception as e:
                print(f"启动子进程失败: {e}")
        else:
            print(f"子进程已在运行(PID: {self.process.pid})，无法重新启动。")
            # self.stop_mcp()
            thread = threading.Thread(target=self.stop_mcp)
            thread.start()

    def inspect_mcpbakok2(self):
        """启动MCP检查器子进程"""

        content = self.editor.toPlainText()
        trimmed_content = content.strip()
        config_content = trimmed_content

        if self.process is None or self.process.poll() is not None:
            try:
                # 检查操作系统类型
                is_windows = os.name == 'nt'

                # 配置通用命令和参数
                command = [
                    'npx', '@modelcontextprotocol/inspector',
                    '--config', os.path.join('C:', os.sep, 'Users', 'IDD', 'mcp.json'),
                    '--server', 'howtocook-mcp'
                ]

                # 如果是 Windows，则使用 'cmd' 和 '/c'
                if is_windows:
                    command = ['cmd', '/c'] + command
                    creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
                else:
                    creationflags = 0

                # 启动子进程
                self.process = subprocess.Popen(
                    command,
                    shell=False,  # 禁用shell更安全
                    creationflags=creationflags
                )


                print("子进程已启动。PID:", self.process.pid)
                webbrowser.open("http://127.0.0.1:6274/")  # 使用默认浏览器打开文件
            except Exception as e:
                print(f"启动子进程失败: {e}")
        else:
            print(f"子进程已在运行(PID: {self.process.pid})，无法重新启动。")
            # self.stop_mcp()
            thread = threading.Thread(target=self.stop_mcp)
            thread.start()

    def inspect_mcpok3(self):
        """启动MCP检查器子进程"""

        content = self.editor.toPlainText()
        trimmed_content = content.strip()
        config_content = trimmed_content

        # 创建 mcp 目录（如果不存在）
        mcp_directory = os.path.join(os.getcwd(), 'mcp')
        os.makedirs(mcp_directory, exist_ok=True)

        # 保存 config_content 到 inspectmcpserver.json
        config_file_path = os.path.join(mcp_directory, 'inspectmcpserver.json')
        with open(config_file_path, 'w') as config_file:
            config_file.write(config_content)

        if self.process is None or self.process.poll() is not None:
            try:
                # 检查操作系统类型
                is_windows = os.name == 'nt'

                # 配置通用命令和参数
                command = [
                    'npx', '@modelcontextprotocol/inspector',
                    '--config', config_file_path,  # 使用保存的文件路径
                    '--server', 'amap-maps'
                ]

                # 如果是 Windows，则使用 'cmd' 和 '/c'
                if is_windows:
                    command = ['cmd', '/c'] + command
                    creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
                else:
                    creationflags = 0

                # 启动子进程
                self.process = subprocess.Popen(
                    command,
                    shell=False,  # 禁用shell更安全
                    creationflags=creationflags
                )

                print("子进程已启动。PID:", self.process.pid)
                webbrowser.open("http://127.0.0.1:6274/")  # 使用默认浏览器打开文件
            except Exception as e:
                print(f"启动子进程失败: {e}")
        else:
            print(f"子进程已在运行(PID: {self.process.pid})，无法重新启动。")
            # self.stop_mcp()
            thread = threading.Thread(target=self.stop_mcp)
            thread.start()

    def inspect_mcp(self):
        """启动MCP检查器子进程"""

        # 获取并修剪编辑器内容
        config_content = self.editor.toPlainText().strip()

        # 创建 mcp 目录（如果不存在）
        mcp_directory = os.path.join(os.getcwd(), 'mcp')
        os.makedirs(mcp_directory, exist_ok=True)

        # 保存 config_content 到 inspectmcpserver.json
        config_file_path = os.path.join(mcp_directory, 'inspectmcpserver.json')
        with open(config_file_path, 'w') as config_file:
            config_file.write(config_content)

        # 从 JSON 内容中获取服务器名称
        try:
            config_json = json.loads(config_content)
            server_name = list(config_json["mcpServers"].keys())[0]  # 获取第一个服务器名称
        except (json.JSONDecodeError, KeyError) as e:
            print(f"解析配置内容失败: {e}")
            return

        if self.process is None or self.process.poll() is not None:
            try:
                os.environ['DANGEROUSLY_OMIT_AUTH'] = 'true'
                # 检查操作系统类型
                is_windows = os.name == 'nt'

                # 配置通用命令和参数
                command = [
                    'npx', '@modelcontextprotocol/inspector',
                    '--config', config_file_path,  # 使用保存的文件路径
                    '--server', server_name  # 使用从JSON中提取的服务器名称
                ]

                # 如果是 Windows，则使用 'cmd' 和 '/c'
                if is_windows:
                    command = ['cmd', '/c'] + command
                    creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
                else:
                    creationflags = 0

                # 启动子进程
                self.process = subprocess.Popen(
                    command,
                    shell=False,  # 禁用shell更安全
                    creationflags=creationflags
                )

                print("子进程已启动。PID:", self.process.pid)
                webbrowser.open("http://127.0.0.1:6274/")  # 使用默认浏览器打开文件
            except Exception as e:
                print(f"启动子进程失败: {e}")
        else:
            print(f"子进程已在运行(PID: {self.process.pid})，无法重新启动。")
            # 启动停止子进程的线程
            thread = threading.Thread(target=self.stop_mcp)
            thread.start()

    def stop_process():
        self.process.terminate()
        self.process.wait()



    def stop_mcp(self):
        """停止MCP检查器子进程"""
        if self.process is None:
            print("没有正在运行的子进程。")
            return
        try:
            # Windows下使用CTRL_BREAK信号更可靠
            if sys.platform == 'win32':
                self.process.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                self.process.terminate()

            # 设置超时防止无限等待
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print("子进程未响应，强制终止...")
                self.process.kill()
                self.process.wait()

            print(f"子进程(PID: {self.process.pid})已停止。")
        except Exception as e:
            print(f"停止子进程时发生错误: {e}")
        finally:
            self.process = None  # 确保引用被清除

    def loadFile(self):

        if not self.changesSaved:

            popup = QtWidgets.QMessageBox()
            popup.setWindowTitle("AI-SNS")

            popup.setIcon(QtWidgets.QMessageBox.Warning)

            popup.setText("The document has been modified")

            popup.setInformativeText("Do you want to save your changes?")

            popup.setStandardButtons(QtWidgets.QMessageBox.Save   |
                                      QtWidgets.QMessageBox.Cancel |
                                      QtWidgets.QMessageBox.Discard)

            popup.setDefaultButton(QtWidgets.QMessageBox.Save)

            answer = popup.exec()

            if answer == QtWidgets.QMessageBox.Save:
                self.save_file()

        self.re_init()

        mcp_id =self.mcp_id
        if mcp_id=="" and self.mcp_manager.type_str != "2":
            return
        else:
            record =query_mcp_mng(mcp_id=mcp_id)
            if record:
                filename=record.file_path
                filename = os.path.join(os.getcwd(), "mcp", filename + ".json")

                self.filename=filename
                self.mcp_id = record.mcp_id


                self.mcp_name_input.setText(record.name)
                self.instruction_input.setText(record.instruction)
                self.mcp_description_input.setText(record.description)

                if record.mcp_type=="1":
                    self.publish_check.setChecked(True)
                else:
                    self.publish_check.setChecked(False)

                if record.used_in_sns==1:
                    self.sns_check.setChecked(True)
                else:
                    self.sns_check.setChecked(False)


                self.detail_text_edit.setPlainText(record.detail)

        if filename:
            if os.path.exists(filename):
                with open(filename,"rt", encoding='utf-8') as file:
                    self.editor.setPlainText(file.read())

        self.changesSaved = True


# 主入口
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    # 创建代码编辑器窗口并设置初始内容
    editor_widget = CodeEditor(content="def cjrok():")
    editor_widget.create_widget("def cjrok():")
    editor_widget.show()  # 显示窗口
    app.exec()  # 运行应用程序的事件循环
