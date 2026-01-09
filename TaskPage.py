import os

import threading


import openai
import shutil
import urllib
from datetime import datetime
import requests
import os
from PyQt6 import QtGui, QtCore
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtWidgets import QWidget, QFileDialog, QMessageBox, QDialog, QTreeWidgetItemIterator, QPlainTextEdit,QFrame

from PyQt6.QtCore import QSettings, Qt, QUrl, QFile, QFileInfo, pyqtSlot
from PyQt6.QtGui import QIcon, QStandardItemModel, QStandardItem
from PyQt6 import QtCore, QtGui, QtWidgets
from langchainhandler import getvectorkm_String
from speaker import Speaker
from ui.ui_TaskPageWidget import Ui_TaskPageWidget, MessageHandler
import hashlib
import webbrowser
from db.DBFactory import add_AgentTask,query_AgentCfg,get_all_prompt_by_modelname,query_llm_frequents
import http.client
import json
from pluginsmanager import PluginEngine, PluginType

import argparse

from pluginsmanager import FileSystem

import urllib.request
import re

import sys
import re
import os

import threading


import openai
import shutil
import urllib
from datetime import datetime
import requests
import os
from PyQt6 import QtGui, QtCore
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtWidgets import QWidget, QFileDialog, QMessageBox, QDialog, QTreeWidgetItemIterator, QPlainTextEdit,QFrame

from PyQt6.QtCore import QSettings, Qt, QUrl, QFile, QFileInfo, pyqtSlot
from PyQt6.QtGui import QIcon, QStandardItemModel, QStandardItem
from PyQt6 import QtCore, QtGui, QtWidgets
from langchainhandler import getvectorkm_String
from speaker import Speaker
from ui.ui_TaskPageWidget import Ui_TaskPageWidget, MessageHandler
import hashlib
import webbrowser
from db.DBFactory import add_AgentTask,query_AgentCfg,get_all_prompt_by_modelname,query_llm_frequents
import http.client
import json
from pluginsmanager import PluginEngine, PluginType

import argparse

from pluginsmanager import FileSystem

import urllib.request
import re

import sys
import re
sys.path.append("..")
sys.path.append("../..")
from kmselect import FreezeTableDialog as KmFreezeTableDialog
from pluginselect_llm import FreezeTableDialog as PluginFreezeTableDialog, ComboBoxDelegate, ButtonDelegate, ButtonDelegateFrequent
from pluginselect_tool import FreezeTableDialog as PluginFreezeTableDialogTool, ComboBoxDelegate as ComboBoxDelegateTool, ButtonDelegate as ButtonDelegateTool

from db.DBFactory import add_KMCfg, query_KMCfg_All, update_KMCfg, delete_KMCfg, query_KMCfg,update_AgentTask,query_workflow_mng,query_function_mng
from db.DBFactory import add_PluginMng, query_PluginMng_All, update_PluginMng, delete_PluginMng, query_PluginMng, query_PluginMng_All_Tool,query_mcp_mng_all,query_mcp_mng
from db.DBFactory import update_AgentCfg,query_AgentTask,query_workflow_mng_all,get_prompt_by_title,query_function_mng_all,query_skill_mng_all,query_skill_mng,query_chat_preset_msg_all,delete_chat_preset_msg,add_chat_preset_msg
from globals import global_plugin_list
from globals import global_buddy_list
import globals
import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QThread, pyqtSignal
from RPAStocksHandle import StocksHandle
from Agent import Agent, AgentMode
import pyautogui
import pyperclip
import os
import time
import threading
import threading
import subprocess
import re
import logging
from i18n import lt
from pynput import mouse, keyboard

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLineEdit, QPushButton, QVBoxLayout, QWidget, QMenu, QHBoxLayout
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QKeySequence, QAction, QShortcut
from pluginsmanager.plugins_gui.tab_plugin import load_plugin
from pluginsmanager.plugins_headless.plugin_mng import load_plugin as load_plugin_headless
from PyQt6.QtWidgets import  QSizePolicy
pyautogui.PAUSE = 0.5
from pathlib import Path
from util import generate_random_id, add_msg_to_message_window, add_msg_to_message_windowv3, get_user_ask_msg_title_formatted, get_user_ask_msg_content_formatted, get_agent_reply_msg_title_formatted, get_agent_reply_msg_content_formatted, toggle_msg_loading_status, add_agent_reply_msg_to_message_window, add_msg_to_message_window_with_markdown_and_highlight, add_attachment_to_message_window, image_to_base64, generate_img_tag
import util
from skilllearning.learn_operation import LearnOperationBar
from skilllearning.auto_operate import AutoOperateBar
import llm_manager as llmmgr
from llm_message_manager import LLMMessageManager
from speaker import Speaker_Log
current_agent = None


# 全局诗歌列表，用于在QTextEdit控件中显示
import random
from PyQt6.QtCore import QSettings, Qt, QUrl, QFile, QFileInfo, QTimer
from aimapcfgdialog import ConfigDialog

class TextEditHandler(logging.Handler):
    """自定义日志处理器，将日志输出到 QTextEdit"""

    def __init__(self, text_edit):
        super().__init__()
        self.text_edit = text_edit

    def emit(self, record):
        """重写 emit 方法，将日志消息添加到 QTextEdit"""
        log_entry = self.format(record)
        self.text_edit.append(log_entry)  # 将日志消息添加到 QTextEdit


class WorkerThread(QThread):
    finished = pyqtSignal(str, str, int)

    def __init__(self, agent, task_id, is_first, question, messages, llm_full_name, system_role_id, system_role_prompt, vector_path, embedding_model_name, modelname, web_browser, speaker, attachment_content_list, plugin_tool_record_selected_list, parent=None,sleep_time=0):
        super(WorkerThread, self).__init__(parent)
        global current_agent
        self.agent = agent
        current_agent = self.agent
        agent_cfg = agent.agent_cfg
        self.agentcfg = agent_cfg
        self.task_id = task_id
        self.is_first = is_first
        self.agent_name = agent_cfg.name
        self.question = question
        self.messages = messages
        self.llm_full_name = llm_full_name
        self.system_role_id = system_role_id
        self.system_role_prompt = system_role_prompt
        self.vector_path = vector_path
        self.embedding_model_name = embedding_model_name
        self.modelname = modelname
        self.web_browser = web_browser
        self.browser_page = web_browser.page()
        self.speaker = speaker
        self.attachment_content_list = attachment_content_list
        self.plugin_tool_record_selected_list = plugin_tool_record_selected_list
        self.sleep_time = sleep_time

    def run(self):
        if self.sleep_time>0:
            time.sleep(self.sleep_time)
        agent = self.agent
        browser_page = self.browser_page

        agent.set_mode(AgentMode.ChatOnly)
        agent.give_it_llm(self.llm_full_name)
        agent.give_it_role(self.system_role_id, self.system_role_prompt)
        agent.give_it_plugin_tool(self.plugin_tool_record_selected_list)
        agent.give_it_attachment_content_list(self.attachment_content_list)
        agent.give_it_km(self.vector_path, self.embedding_model_name)
        # browser_page.runJavaScript("alert('你好呀001-1');")
        agent.give_it_speaker(self.speaker)
        question = self.question
        answer = agent.ask_it(question, self.messages, browser_page, self.task_id)
        attachment_content_list = json.dumps(agent.attachment_content_list, ensure_ascii=False)  # km部分已经在agent中进行了处理，添加进去了
        # attachment_doc_content=json.dumps(agent.attachment_doc_content)
        # attachment_image_list=json.dumps(agent.attachment_image_list)

        if agent.is_running_workflow:
            question=self.speaker.latest_human_feedback

        elif agent.chat_mode == "task":
            # question="用户发出了上述指令"
            question = "exit"

        record = query_AgentTask(task_id=self.task_id)
        if record:
            self.is_first = False

        record_id = add_AgentTask(self.task_id, question, question, answer, self.modelname, self.agentcfg.user_id, self.is_first, attachment_content_list)

        agent.remove_all_attachment()
        self.finished.emit(question, answer, record_id)

    def stop(self):
        print("thread stopping....")
        del self.agent
        print("del agent....")

class WorkerThreadBackGround(QThread):
    finished = pyqtSignal(str, str)
    ask_command_finished = pyqtSignal(str, str)

    def __init__(self, agent, question, messages, web_browser, task_id, parent=None, type_flag="message"):
        super(WorkerThreadBackGround, self).__init__(parent)

        self.agent = agent

        agent_cfg = agent.agent_cfg
        self.agentcfg = agent_cfg
        self.task_id = task_id
        self.agent_name = agent_cfg.name
        self.question = question
        self.messages = messages
        self.web_browser = web_browser
        self.browser_page = web_browser.page()
        self.type_flag = type_flag


    def run(self):
        agent = self.agent
        browser_page = self.browser_page
        agent.set_mode(AgentMode.ChatOnly)
        question = self.question
        answer = agent.ask_it(question, self.messages, browser_page, self.task_id)
        if self.type_flag == "command":
            self.ask_command_finished.emit(question, answer)
        else:
            self.finished.emit(question, answer)

    def stop(self):
        print("thread stopping....")
        del self.agent
        print("del agent....")


class WorkerThreadGP(QThread):

    def __init__(self):
        super(WorkerThreadGP, self).__init__(None)
        print("ok")

    def run(self):
        stocks_handle = StocksHandle()
        companies = ['google', 'amazon', 'meta', 'apple']
        stocks_handle.get_Stocks(companies)
        print("准备发文件...")
        os.startfile("C:\Program Files (x86)\Tencent\WeChat\WeChat.exe")
        time.sleep(1)
        self.click_image_position("search.png")
        name = '文件传输助手'
        pyperclip.copy(name)
        # 模拟按下和释放Ctr1键和V键
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press('enter')
        time.sleep(1)  # 避免操作过快
        self.click_image_position("sendfile.png")
        directory = os.path.join(Path(__file__).resolve().parent, "temp", "market")
        NOW = datetime.now()
        PPTX = f'{directory}-{NOW.month}-{NOW.year}.pptx'
        file_path = PPTX
        pyperclip.copy(file_path)
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press('enter')
        time.sleep(1)
        pyautogui.press('enter')


class TaskPage(QWidget, Ui_TaskPageWidget):
    def __init__(self, application, agent):
        super(TaskPage, self).__init__()
        # 设置日志
        self.process_manager = None
        self.agent = agent
        agent_cfg = agent.agent_cfg
        self.agent_cfg = agent_cfg
        self.name = agent_cfg.name
        self.application = application
        self.qurl_remote_url = None
        self.qurl_local_url = None
        self.task_id = ""
        self.is_first = True
        self.task_type = 'single'
        self.is_learning_skill = False
        self.is_running_skill = False
        self.page_index = 0
        self.system_role_id = -1
        self.system_role_prompt = ""

        # 后面可能会有system提示，这句在这个地方，可能会导致像百川这样不允许多个system的role的提示语，会报错，百度不允许有system这个角色
        # self.messages = [{"role": "system", "content": f"{self.system_role_prompt}"}]
        self.messages_debug_model = []
        self.messages_debug_prompt = []

        self.messages = []
        self.updown_message_index = -1  # 上移指针（初始为-1表示起始位置）
        self.messages_mng = LLMMessageManager()
        self.task_command = ""
        self.is_transfer_to_workflow = False

        self.pre_system_role_prompt = ""
        self.work_flow_title = ""
        self.work_flow_label = ""
        self.work_flow_desc = ""

        self.messages_attachment_list = {}
        self.messages_km_list = {}
        self.messages_attachment_content = {}
        self.messages_km_content = {}
        self.words = ""
        self.words_count = 0

        # 指定历史(指定上下文相关)
        self.selected_history_messages = []
        self.selected_history_index = []
        self.selected_history_id = []

        # 附件信息相关
        self.current_attachment_list = []
        # self.current_attachment_content="___________以下是相关附件信息,供你参考___________"
        # self.current_attachment_content = ""  # 合并后的附件内容
        self.attachment_content_list = []  # 附件内容列表
        self.attachment_labels = []  # 存储所有附件标签

        self.llm_fullname_selected_list = []

        self.conten_menu_closing = False  # 是否正在关闭内容菜单，用于给全选按钮做判断条件
        self.content_menu_group_box_showed = False
        self.multi_model_comparison = False
        self.model_reply_a = ""
        self.model_reply_b = ""
        self.model_reply_c = ""
        self.model_replying_flag_a = False
        self.model_replying_flag_b = False
        self.model_replying_flag_c = False
        self.model_hidden_flag_a = False
        self.model_hidden_flag_b = False
        self.model_hidden_flag_c = False

        self.setupUi(self)

        # webengineview去掉了
        # self.messageBrowser.setPlainText("")
        # self.messageBrowser.setOpenLinks(False)

        self.messageEdit.setFocus()
        self.messageEdit.installEventFilter(self)

        self.sendButton.clicked.connect(self.sendMessage)
        self.stopButton.clicked.connect(self.stopMessage)
        self.upButton.clicked.connect(self.upMessage)
        self.downButton.clicked.connect(self.downMessage)
        self.plugin_button.clicked.connect(self.opendialog_plugin_tool)
        self.newButton.clicked.connect(self.new_task_by_btn)
        self.attach_button.clicked.connect(self.add_attachment)
        self.kmButton.clicked.connect(self.opendialogkm)
        self.model_select_checkbox.stateChanged.connect(self.toggle_model_select_type)
        self.task_mode_checkbox.stateChanged.connect(self.toggle_chat_mode)
        self.history_mode_checkbox.stateChanged.connect(self.toggle_history_mode)
        self.prompt_combobox.currentIndexChanged.connect(self.set_prompt_string)
        self.model_combobox.currentIndexChanged.connect(self.set_current_model)
        # self.manage_button.clicked.connect(self.on_manage_button_clicked)#由下面这句替代了
        self.manage_button.mousePressEvent = self.manage_button_mousePressEvent

        self.update_prompts_in_combobox(True)
        self.set_llm_frequent_in_combobox(True)

        self.shortcut = QShortcut(QKeySequence('Ctrl+F'), self)
        self.shortcut.activated.connect(self.toggle_search_box)

        self.tab_plugin = None

        self.kmselectedList = []

        if agent_cfg.uselastkms:
            if agent_cfg.last_kms:
                self.set_km_selected(agent_cfg.last_kms.split(","))

        print(self.kmselectedList)

        self.pluginselectedList_tool = []
        self.plugin_tool_record_selected_list = []
        self.plugin_tool_loaded_list = {}

        if agent_cfg.uselastplugins:
            if agent_cfg.last_plugins:
                self.set_plugin_tool_selected(agent_cfg.last_plugins.split(","))

        self.use_last_model = agent_cfg.uselastmodel
        self.use_last_role = agent_cfg.uselastrole
        self.call_plugin_by_instruct = agent_cfg.callpluginbyinstruct

        self.default_llm = agent_cfg.defaultmodel
        self.last_llm = agent_cfg.lastmodel
        if self.use_last_model:
            self.llm_fullname_selected_list.append(self.last_llm)
        else:
            self.llm_fullname_selected_list.append(self.default_llm)

        self.set_messagebox_placeholder()

        # self.messageBrowser.anchorClicked.connect(self.openLink)
        print(self.application.cjr)
        self.is_browser_page_loaded = False
        self.messageBrowser.page().loadFinished.connect(self.onLoadFinished)  # 第一次可能page没来得及load，所以需要在onload中处理

        self.auto_operate_bar = None

        self.learn_operation_bar = None
        self.current_ask_agent_to_instruct_flag = ""

        self.shortcut = QShortcut(QKeySequence('Ctrl+F1'), self)
        self.shortcut.activated.connect(self.toggle_search_box)
        self.task_status = ""

    def eventFilter(self, obj, event):
        """过滤事件以检测 '@' 键的按下，并显示选择对话框"""
        if obj == self.messageEdit and event.type() == QtCore.QEvent.KeyPress:
            # if event.text() == "@":  # 检测 '@' 键
            if event.text() == "@" and self.messageEdit.toPlainText()=="@c":
                self.showCompletionDialog("skill")  # 显示选择对话框
                return True  # 事件被处理，返回True
            elif event.text() == "@" and self.messageEdit.toPlainText()=="@w":
                self.showCompletionDialog("workflow")  # 显示选择对话框
                return True  # 事件被处理，返回True
            elif event.text() == "@" and self.messageEdit.toPlainText()=="@p":
                self.showCompletionDialog("tool")  # 显示选择对话框
                return True  # 事件被处理，返回True
            elif event.text() == "@" and self.messageEdit.toPlainText()=="@m":
                self.showCompletionDialog("mcp")  # 显示选择对话框
                return True  # 事件被处理，返回True
            elif event.text() == "@" and self.messageEdit.toPlainText()=="@f":
                self.showCompletionDialog("function")  # 显示选择对话框
                return True  # 事件被处理，返回True
            elif event.text() == "@" and self.messageEdit.toPlainText()=="@":
                self.showCompletionDialog("all")  # 显示选择对话框
                return True  # 事件被处理，返回True
            if event.key() == QtCore.Qt.Key.Key_I and event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier:
                self.showCompletionDialogV2()  # 显示选择对话框
                return True  # 事件被处理，返回True

        return super().eventFilter(obj, event)  # 其他事件交给基类处理

    def showCompletionDialog(self, type_str):
        """显示对话框，供用户选择内容"""
        choices = []

        # Define a function to query based on type_str
        def query_and_append(records,type_str=""):
            if type_str:
                choices.append(("--"+type_str+"--","Tool type"))
            if type_str=="Computer use":
                choices.append(("learn", "learn"))

            for record in records:
                choice = (getattr(record, 'name', getattr(record, 'title', '未知名称')),
                          record.instruction if record.instruction is not None else "")

                choices.append(choice)

        # Determine the query based on type_str
        if type_str == "skill":
            query_and_append(query_skill_mng_all(skill_type="1"))
        elif type_str == "workflow":
            query_and_append(query_workflow_mng_all(is_delete=0))
        elif type_str == "tool":
            query_and_append(query_PluginMng_All_Tool(is_delete=0))
        elif type_str == "function":
            query_and_append(query_function_mng_all(function_type="1"))
        elif type_str == "mcp":
            query_and_append(query_mcp_mng_all(mcp_type="1"))
        elif type_str == "all":
            # Collect all relevant records
            query_and_append(query_PluginMng_All_Tool(is_delete=0),type_str="Plugin")
            query_and_append(query_mcp_mng_all(mcp_type="1"),type_str="Mcp")
            query_and_append(query_skill_mng_all(skill_type="1"),type_str="Computer use")
            query_and_append(query_function_mng_all(function_type="1"),type_str="Function")
            query_and_append(query_workflow_mng_all(is_delete=0),type_str="Workflow")

        # Create QDialog as the dialog window
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("请选择")

        layout = QtWidgets.QVBoxLayout(dialog)
        list_widget = QtWidgets.QListView(dialog)

        model = QStandardItemModel(list_widget)
        list_widget.setModel(model)
        info_label = QtWidgets.QLabel()

        # Define the update_label function before connecting it
        def update_label():
            """更新 QLabel，以显示当前选中项的数据值"""
            selected_indexes = list_widget.selectedIndexes()

            if selected_indexes:
                # Get data from the first selected item
                selected_item = selected_indexes[0]
                data_value = model.itemFromIndex(selected_item).data(QtCore.Qt.UserRole)
                info_label.setText(f" {data_value}")
            else:
                info_label.setText("请选择一个项以查看数据")

        # Connect the selection change signal to the update_label function
        list_widget.selectionModel().selectionChanged.connect(update_label)




        # Add items to the list and set their data
        non_selectable_groups = {"--Plugin--", "--Mcp--", "--Computer use--", "--Function--", "--Workflow--"}
        for name, instruction in choices:
            item = QtGui.QStandardItem(name)
            item.setData(instruction, QtCore.Qt.UserRole)
            # 检查是否在不可选中不可编辑组中
            if name in non_selectable_groups:
                print("name not select",name)
                item.setFlags(Qt.ItemFlag.ItemIsEnabled)

                item.setForeground(Qt.GlobalColor.gray)
            else:
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable)  # 可选择和编辑

            model.appendRow(item)

        # 默认选中第一个项并更新标签
        if model.rowCount() > 0:  # 确保模型不为空
            list_widget.setCurrentIndex(model.index(0, 0))  # 指定列为0
            update_label()  # 更新标签以显示第一个项的数据

        layout.addWidget(list_widget)
        layout.addWidget(info_label)

        # Connect double click and key press events
        list_widget.doubleClicked.connect(lambda index: self.insertCompletion(model.itemFromIndex(index).data(QtCore.Qt.UserRole), dialog))
        list_widget.keyPressEvent = lambda event: self.handleKeyPress(event, list_widget, dialog,model)

        # Calculate and set dialog position based on cursor position
        cursor = self.messageEdit.textCursor()
        cursor_rect = self.messageEdit.cursorRect(cursor)
        global_position = self.messageEdit.mapToGlobal(QtCore.QPoint(cursor_rect.right(), cursor_rect.top() - dialog.sizeHint().height()))
        dialog.move(global_position.x(), global_position.y())

        dialog.exec()  # Display the dialog and wait for user interaction

    def handleKeyPress(self, event, list_widget, dialog,model):
        """处理键盘事件，特别是回车键"""
        if event.key() == QtCore.Qt.Key.Key_Return or event.key() == QtCore.Qt.Key.Key_Enter:
            # 获取当前选中的项

            selected_indexes = list_widget.selectedIndexes()
            if len(selected_indexes)==0:
                return
            selected_item = selected_indexes[0]
            current_item=model.itemFromIndex(selected_item)
            if current_item:
                # 如果有选中的项，则插入内容并关闭对话框
                if current_item.data(QtCore.Qt.UserRole) == "Tool type":
                    return
                self.insertCompletion(current_item.data(QtCore.Qt.UserRole), dialog)
        else:
            # 调用基类的keyPressEvent以处理其他按键
            super(QtWidgets.QListView, list_widget).keyPressEvent(event)

    def insertCompletion(self, completion, dialog):
        """插入用户选择的内容并关闭对话框"""
        if completion=="Tool type":
            return
        cursor = self.messageEdit.textCursor()  # 获取当前光标

        if len(self.messageEdit.toPlainText()) == 2:#处理@m,@c这种
           cursor.deletePreviousChar()


        # cursor.movePosition(QtGui.QTextCursor.Left, QtGui.QTextCursor.KeepAnchor, 1)  # 选择 '@'
        if ":" in completion:
            completion =completion.split(":",1)[0]
        cursor.insertText(completion + ":")

        self.messageEdit.setTextCursor(cursor)  # 更新光标位置
        dialog.accept()  # 关闭对话框


    def showCompletionDialogV2(self):
        """显示成员选择对话框，支持动态添加/删除选项"""
        # 初始化选项列表
        # 获取所有预设消息记录
        all_records = query_chat_preset_msg_all()
        # 将所有记录的 content 保存到 choices 列表中
        choices = [record.content for record in all_records]

        # 创建对话框及主布局
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("选择")
        main_layout = QtWidgets.QVBoxLayout(dialog)

        # 创建列表部件
        list_widget = QtWidgets.QListWidget()
        list_widget.addItems(choices)
        main_layout.addWidget(list_widget)
        # 创建按钮布局
        button_layout = QtWidgets.QHBoxLayout()

        # 新增按钮：弹出输入框添加选项
        btn_add = QtWidgets.QPushButton("新增")
        btn_add.clicked.connect(lambda: self._addListItem(list_widget))
        button_layout.addWidget(btn_add)

        # 删除按钮：移除选中项
        btn_delete = QtWidgets.QPushButton("删除")
        btn_delete.clicked.connect(lambda: self._removeSelectedItem(list_widget))
        button_layout.addWidget(btn_delete)

        main_layout.addLayout(button_layout)
        # 连接列表交互事件
        list_widget.itemDoubleClicked.connect(lambda item: self.insertCompletionV2(item.text(), dialog))
        list_widget.keyPressEvent = lambda event: self.handleKeyPressV2(event, list_widget, dialog)

        # 定位对话框到光标位置
        cursor = self.messageEdit.textCursor()
        cursor_rect = self.messageEdit.cursorRect(cursor)
        global_pos = self.messageEdit.mapToGlobal(
            QtCore.QPoint(cursor_rect.right(), cursor_rect.top() - dialog.sizeHint().height())
        )
        dialog.move(global_pos)

        dialog.exec()

    def _addListItem(self, list_widget):
        """添加新项到列表部件"""
        text, ok = QtWidgets.QInputDialog.getText(
            self, "新增项目", "输入内容:"
        )
        if ok and text.strip():
            list_widget.addItem(text.strip())
            add_chat_preset_msg(text.strip())

    def _removeSelectedItem(self, list_widget):
        """删除当前选中项，并请求用户确认"""
        selected_item = list_widget.currentItem()
        if selected_item:
            # 弹出确认对话框
            reply = QtWidgets.QMessageBox.question(
                self,
                "确认删除",
                f"确认删除选中的项: '{selected_item.text()}' 吗?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No
            )

            # 用户选择“是”则删除
            if reply == QtWidgets.QMessageBox.Yes:
                row = list_widget.row(selected_item)
                list_widget.takeItem(row)
                delete_chat_preset_msg(selected_item.text())

    def handleKeyPressV2(self, event, list_widget, dialog):
        """处理键盘事件，特别是回车键"""
        if event.key() == QtCore.Qt.Key.Key_Return or event.key() == QtCore.Qt.Key.Key_Enter:
            # 获取当前选中的项
            current_item = list_widget.currentItem()
            if current_item:
                # 如果有选中的项，则插入内容并关闭对话框
                self.insertCompletionV2(current_item.text(), dialog)
        else:
            # 调用基类的keyPressEvent以处理其他按键
            super(QtWidgets.QListWidget, list_widget).keyPressEvent(event)

    def insertCompletionV2(self, completion, dialog):
        """插入用户选择的内容并关闭对话框"""
        cursor = self.messageEdit.textCursor()  # 获取当前光标
        # cursor.movePosition(QtGui.QTextCursor.Left, QtGui.QTextCursor.KeepAnchor, 1)  # 选择 '@'
        # cursor.insertText("@" + completion + " ")  # 插入 '@' 和选择的文本
        cursor.insertText(completion)  # 插入 '@' 和选择的文本
        self.messageEdit.setTextCursor(cursor)  # 更新光标位置
        dialog.accept()  # 关闭对话框



    def onLoadFinished(self):
        self.is_browser_page_loaded = True
        self.messageEdit.setFocus()
        print("the url2:", self.messageBrowser.page().url())

    def keyPressEvent(self, event):
        # if event.key() == Qt.Key_F and event.modifiers() == Qt.ControlModifier:
        # if event.key() == Qt.Key_F and event.modifiers() == Qt.ControlModifier:
        if event.key() == Qt.Key.Key_F1 and event.modifiers() == Qt.KeyboardModifier.Control:

            print("Ctrl+F detected")
            self.toggle_search_box()

        if event.key() == Qt.Key_Slash and event.modifiers() == Qt.ControlModifier:
            print("你好")
            self.set_default_chat_template()

    def increment_page_index(self):
        self.page_index += 1
        return self.page_index

    def set_selected_history_index(self, i, id, status):
        print("set_selected_history_index i:", i)
        print("set_selected_history_index id", id)
        print("set_selected_history_index status", status)
        if status == "checked":
            self.add_selected_history_index(i)
            self.add_selected_history_id(id)
        else:
            self.remove_selected_history_index(i)
            self.remove_selected_history_id(id)
        self.get_selected_history_messages()

    def set_message_checked(self, i, id, status):
        print("set_selected_history_index i:", i)
        print("set_selected_history_index id", id)
        print("set_selected_history_index status", status)
        if status == "checked":
            self.messages_mng.append_specified_message_id(id)
        else:
            self.messages_mng.remove_specified_message_id(id)

    def toggle_content_menu(self, status="checked"):
        if status == "checked":
            # 还原指定上下文状态
            state = self.history_mode_checkbox.checkState()
            if state == QtCore.Qt.Checked:
                self.context_button.click()

            self.messages_mng.set_specified_status(True)

            self.content_menu_group_box.setVisible(True)
            self.content_menu_group_box_showed = True

            for i in range(self.hboxlayout.count()):
                item = self.hboxlayout.itemAt(i)
                if item.widget():
                    item.widget().setVisible(False)  # 隐藏每个控件

            for i in range(self.hboxlayout1.count()):
                item = self.hboxlayout1.itemAt(i)
                if item.widget():
                    item.widget().setVisible(False)  # 隐藏每个控件

            self.frame_bottom.setVisible(False)

            self.messageBrowser.page().runJavaScript("displayCheckboxes()")

        else:  # 由关闭按钮触发
            self.conten_menu_closing = True
            self.content_menu_group_box.setVisible(False)
            self.content_menu_group_box_showed = False

            for i in range(self.hboxlayout.count()):
                item = self.hboxlayout.itemAt(i)
                if item.widget():
                    item.widget().setVisible(True)  # 显示每个控件

            for i in range(self.hboxlayout1.count()):
                item = self.hboxlayout1.itemAt(i)
                if item.widget():
                    item.widget().setVisible(True)  # 显示每个控件

            self.stopButton.setVisible(False)
            self.output_checkbox.setVisible(False)
            self.history_mode_checkbox.setVisible(False)
            self.task_mode_checkbox.setVisible(False)
            self.frame_bottom.setVisible(True)

            self.task_mode_checkboxa.setChecked(False)
            # self.toggle_page_all_checkboxes_status(0)
            self.messageBrowser.page().runJavaScript('setAllCheckboxesChecked(false);')
            self.messageBrowser.page().runJavaScript("hideCheckboxes()")

    def edit_selected_content(self, code_type, text, file_name=""):
        tabs = self.tabWidget
        if code_type.lower() == "mermaid" or (code_type.lower() == "markdown" and "```mermaid" in text):
            plugin_cfg = query_PluginMng(plugin_id="EK202405K7170A7T190951")

        elif code_type.lower() == "mindmap" or (code_type.lower() == "markdown" and (("思维导图" in text and "##" in text) or ("mindmap" in text and "##" in text) or (text.startswith("#") and "##" in text))):
            plugin_cfg = query_PluginMng(plugin_id="AK2024Y5Q717U20711095")

        else:
            plugin_cfg = query_PluginMng(plugin_id="TP20230517670237197EF")

        plugin = self.load_plugin_to_tab(plugin_cfg)


        plugin.run(file_name, text)

    def add_selected_history_index(self, i):
        # Check if 'i' is already in 'self.selected_history_index'
        if i not in self.selected_history_index:
            # Insert 'i' into 'self.selected_history_index' in sorted order
            self.selected_history_index.append(i)
            self.selected_history_index.sort()

    def remove_selected_history_index(self, i):
        # Remove the first occurrence of 'i' from 'self.selected_history_index', if it exists
        if i in self.selected_history_index:
            self.selected_history_index.remove(i)

    def add_selected_history_id(self, id):
        # Check if 'i' is already in 'self.selected_history_index'
        if id not in self.selected_history_id:
            # Insert 'i' into 'self.selected_history_index' in sorted order
            self.selected_history_id.append(id)
            self.selected_history_id.sort()

    def remove_selected_history_id(self, id):
        # Remove the first occurrence of 'i' from 'self.selected_history_index', if it exists
        if id in self.selected_history_id:
            self.selected_history_id.remove(id)

    def get_selected_history_messages(self):
        # Clear the selected_history_messages list first
        self.selected_history_messages.clear()
        self.selected_history_messages = [{"role": "system", "content": f"{self.system_role_prompt}"}]
        # Get the messages corresponding to the indices in selected_history_index
        for index in self.selected_history_index:
            if 0 <= index < self.messages_mng.get_messages_length():
                self.selected_history_messages.append(self.messages_mng.get_messages()[index])

    def new_task(self):
        self.task_id = ""
        self.is_first = True
        # 后面可能会有system提示，这句在这个地方，可能会导致像百川这样不允许多个system的role的提示语，会报错，百度不允许有system这个角色
        # self.messages = [{"role": "system", "content": "You are a helpful assistant who provides concise and accurate information."}]
        self.messages = []
        self.messages_mng.re_init()
        self.updown_message_index = -1
        self.task_command = ""
        # self.messages = []
        self.page_index = 0
        self.selected_history_messages = []
        self.selected_history_index = []
        self.selected_history_id = []

        self.messages_attachment_list = {}
        self.messages_km_list = {}
        self.messages_attachment_content = {}
        self.messages_km_content = {}

        # 附件信息相关
        self.current_attachment_list = []
        # self.current_attachment_content="___________以下是相关附件信息,供你参考___________"
        # self.current_attachment_content = ""  # 合并后的附件内容
        self.attachment_content_list = []  # 附件内容列表
        self.attachment_labels = []  # 存储所有附件标签

        # 还原指定上下文状态
        state = self.history_mode_checkbox.checkState()
        if state == QtCore.Qt.Checked:
            self.context_button.click()

        if self.content_menu_group_box_showed:
            self.close_button.click()

        # ***********todo:附件的界面也要清除掉****************

        self.messageBrowser.page().runJavaScript('re_init()')

        self.setup_logging()

    def receiveMessage(self, event):
        message = f"""\n<strong><span style="color: darkblue">{self.name} :</span></strong> {event.getBody()}"""
        self.messageBrowser.append(message)

    def __description(self) -> str:
        return "Create your own anime meta data"

    def __usage(self) -> str:
        return "vrv-meta.py --service vrv"

    def __init_cli(self) -> argparse:
        parser = argparse.ArgumentParser(description=self.__description(), usage=self.__usage())
        parser.add_argument(
            '-l', '--log', default='DEBUG', help="""
            Specify log level which should use. Default will always be DEBUG, choose between the following options
            CRITICAL, ERROR, WARNING, INFO, DEBUG
            """
        )
        parser.add_argument(
            '-d', '--directory', default=f'{FileSystem.get_plugins_directory()}', help="""
            (Optional) Supply a directory where plugins should be loaded from. The default is ./plugins
            """
        )
        return parser

    def __print_program_end(self) -> None:
        print("-----------------------------------")
        print("End of execution")
        print("-----------------------------------")

    def __init_app(self, parameters: dict) -> None:
        return PluginEngine(options=parameters).start()

    def click_image_position(self, img):
        # time.sleep(1)
        image_1 = pyautogui.locateOnScreen(img, grayscale=True, confidence=0.7)
        # time.sleep(1)
        center = pyautogui.center(image_1)
        pyautogui.click(center)


    def sendMessage(self):
        if self.messageEdit.toPlainText():


            __cli_args = self.__init_cli().parse_args()
            print(__cli_args.log)

            if len(self.llm_fullname_selected_list) > 0:
                # self.pluginselectedList: [(1, '2', 'ChatGLM', 'chatglm_connector')]#row index,record id,plugin name,plugin alias
                # llm_full_name=self.pluginselectedList[0][2]
                # modelname=self.pluginselectedList[0][3]
                llm_full_name = self.llm_fullname_selected_list[0]
                llm_model_type = ""
                if ":" in llm_full_name:
                    llm_model_type = llm_full_name.split(":")[1]
                    llm_connector_name = llm_full_name.split(":")[0]

                llm = global_plugin_list[llm_connector_name]
                config = llm.get_config()
                if llm_model_type:
                    modelname = llm_model_type
                else:
                    modelname = config.get("model", "")

                modelname = llm_connector_name + f"({modelname})"

                # 增加以下语句，如果有选中的插件，则认为是指定了，而不是自动，暂时不要使用checkbox进行指定
                self.agent.model_select_type = 'specify'

            else:
                llm_connector_name = "ChatGLM"  # 设置缺省连接器
                modelname = "ChatGLM"  # 指定缺省模型
                # 增加以下语句，如果没选中插件，则认为是自动，暂时不要使用checkbox进行指定
                self.agent.model_select_type = 'auto'

            if self.agent.model_select_type == 'auto':
                if "天气" in self.messageEdit.toPlainText():
                    llm_connector_name = "百度文心"
                    llm = global_plugin_list[llm_connector_name]
                    config = llm.get_config()
                    modelname = "ERNIE-3.5-8K"
                    modelname = llm_connector_name + f"({modelname})"
                elif "编写" in self.messageEdit.toPlainText():
                    llm_connector_name = "通义千问"
                    llm = global_plugin_list[llm_connector_name]
                    config = llm.get_config()
                    modelname = "qwen-long"
                    modelname = llm_connector_name + f"({modelname})"
                elif "写一个" in self.messageEdit.toPlainText():
                    llm_connector_name = "通义千问"
                    llm = global_plugin_list[llm_connector_name]
                    config = llm.get_config()
                    modelname = "qwen-long"
                    modelname = llm_connector_name + f"({modelname})"

                elif "算法" in self.messageEdit.toPlainText():
                    llm_connector_name = "通义千问"
                    llm = global_plugin_list[llm_connector_name]
                    config = llm.get_config()
                    modelname = "qwen-long"
                    modelname = llm_connector_name + f"({modelname})"

                elif "介绍一下" in self.messageEdit.toPlainText():
                    llm_connector_name = "讯飞星火"
                    llm = global_plugin_list[llm_connector_name]
                    config = llm.get_config()
                    modelname = "general"
                    modelname = llm_connector_name + f"({modelname})"

            promptstr = ""
            print("the km list", self.kmselectedList)
            print("the km list length", len(self.kmselectedList))
            if len(self.kmselectedList) > 0:
                print("self.kmselectedList:")
                print(self.kmselectedList)
                self.logger.info("Used KM:" + self.kmselectedList[0])
                km_name = self.kmselectedList[0]
                km_record = query_KMCfg(name=km_name)
                vector_path = km_record.kmpath
                print("vector_path:", vector_path)
                self.logger.debug("vector_path:" + vector_path)
                # vector_path = "vector_store/vector"  # 先写死
                vector_path = os.path.join(os.getcwd(), "km", vector_path, "vector")
                print("vector_path2:", vector_path)
                embedding_model_name = km_record.embeddingmodel
            else:
                vector_path = ""
                embedding_model_name = ""

            question = self.messageEdit.toPlainText()
            self.task_command = question

            speaker = self.speaker

            # 处理插件
            plugin_tool_record_selected_list = self.plugin_tool_record_selected_list
            for record in plugin_tool_record_selected_list:
                if "previous_to_send_b" in record.plugin_event:
                    index_event = record.plugin_event.split(",").index("previous_to_send_b")
                    instruction_list = []
                    instruction = record.instruction
                    instructed_flag = False
                    run_plugin_flag = False
                    if instruction:
                        instruction_list = instruction.split(",")

                    for inst in instruction_list:
                        if inst in question:
                            instructed_flag = True

                    if instructed_flag:
                        run_plugin_flag = True

                    if run_plugin_flag:
                        plugin = self.plugin_tool_loaded_list[record.name]
                        result = plugin.handle_previous_to_send_b(self, question)
                        how_to_handle_executed_result = record.plugin_executed.split(",")[index_event]
                        if how_to_handle_executed_result == "get_output_as_final_result":
                            answer = result
                            return answer
                        else:
                            question = result
                            self.messageEdit.setPlainText(result)


            if self.messageEdit.toPlainText().startswith("@"):
                    instruct_content,question_content = self.messageEdit.toPlainText().split(":",1)
                    if instruct_content:
                        instruct_content = instruct_content[1:]
                    if instruct_content:
                        skill_record = query_skill_mng(instruction=instruct_content)
                        if skill_record:
                            self.run_computer_use(skill_record=skill_record)


            if self.messageEdit.toPlainText().lower().startswith("@learn:"):

                self.agent.give_it_answer_no_thinking(lt("I will record every step.", "我将记录下每个步骤。"))
                print("学习....")
                opr_file_name = self.messageEdit.toPlainText()
                opr_file_name = opr_file_name.replace("学习一下", "")
                opr_file_name = opr_file_name.replace("学习", "")
                learn_content = self.messageEdit.toPlainText()[7:]

                if self.learn_operation_bar is None:
                    self.learn_operation_bar = LearnOperationBar(self.application,learn_content)


                self.learn_operation_bar.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
                self.learn_operation_bar.show()
                self.learn_operation_bar.auto_start()

            if self.messageEdit.toPlainText() == "ymcymc":
                print(os.getcwd())
                print(os.path.join(os.getcwd(), "scripts", "index.html"))
                print(urllib.request.pathname2url(os.path.join(os.getcwd(), "index.html")))
                url_string = urllib.request.pathname2url(os.path.join(os.getcwd(), "scripts", "index.html"))
                print("transform")
                print(url_string)
                self.messageBrowser.page().load(QUrl(url_string))
                print("okcjrok")

            elif self.messageEdit.toPlainText() == "szrszr":
                url_string = "https://bridge.yfd.net:1443/"
                print("transform")
                print(url_string)
                self.messageBrowser.page().load(QUrl(url_string))
                print("szrszr")

            elif self.messageEdit.toPlainText() == "zdfzdf":
                self.application.stack_main_widget.setCurrentIndex(1)  # 首页
                self.application.show_ai_toolbox_stack()

                if "buddylist" in global_buddy_list:
                    buddylist = global_buddy_list["buddylist"]
                    buddylist.send_message("yangyang@xabber.de", "您好，我自动发")

            elif "to autogen:" in self.messageEdit.toPlainText():
                global current_agent

                current_agent.human_reply = self.messageEdit.toPlainText()[11:]
                message = f"""{current_agent.human_reply}"""
                self.messageBrowser.page().runJavaScript('document.body.innerHTML += "' + message + '<br><br>"')

            elif "*给我画*" in self.messageEdit.toPlainText():
                # 废弃掉不通过这个判断走了，现在是在Agent中走
                urls = self.generate_image(self.messageEdit.toPlainText())
                print("给我画url:", urls)

                message = f"""<strong><em><span style='color: darkred;font-size:14px;'>{lt("User","用户")}: </span><span style='color: #c0c0c0; font-size:14px;'>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</span></em></strong>"""
                self.messageBrowser.page().runJavaScript('document.getElementById("allcontent").innerHTML += "' + message + '<br>"')
                message = f"""{self.messageEdit.toPlainText()}"""
                self.messageBrowser.page().runJavaScript('document.getElementById("allcontent").innerHTML += "' + message + '<br><br>"')
                modelname = "Dall-e-3"
                message = f"""<strong><em><span style='color: darkblue; font-size:14px;'>{self.tr(modelname)}: </span><span style='color: #c0c0c0; font-size:14px;'>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</span></em></strong><br>"""
                self.messageBrowser.page().runJavaScript('document.getElementById("allcontent").innerHTML += "' + message + '"')

                # 创建新的附件元素

                img_element = ''.join(f"<img src='{url}'>&nbsp;&nbsp;&nbsp;&nbsp;<br>" for url in urls)
                print(img_element)
                # 添加附件元素到页面中
                self.messageBrowser.page().runJavaScript('document.getElementById("allcontent").innerHTML += `' + img_element + '`')

            elif "//股票" in self.messageEdit.toPlainText():
                print("股票")

                os.system("C:\\dev\\rpa\\Stocks_RPA_Python\\venv\\Scripts\\python.exe C:/dev/rpa/Stocks_RPA_Python/mainv2.py")

                # stocks_handle = StocksHandle()
                # companies = ['google', 'amazon', 'meta', 'apple']
                # stocks_handle.get_Stocks(companies)

                # self.thread = WorkerThreadGP()
                #
                # self.thread.start()

                # print("准备发文件...")
                # os.startfile("C:\Program Files (x86)\Tencent\WeChat\WeChat.exe")
                # time.sleep(1)
                # self.click_image_position("search.png")
                # name = '文件传输助手'
                # pyperclip.copy(name)
                # # 模拟按下和释放Ctr1键和V键
                # pyautogui.hotkey('ctrl', 'v')
                # pyautogui.press('enter')
                # time.sleep(1)  # 避免操作过快
                # self.click_image_position("sendfile.png")
                # directory = os.path.join(Path(__file__).resolve().parent, "temp", "market")
                # NOW = datetime.now()
                # PPTX = f'{directory}-{NOW.month}-{NOW.year}.pptx'
                # file_path = PPTX
                # pyperclip.copy(file_path)
                # pyautogui.hotkey('ctrl', 'v')
                # pyautogui.press('enter')
                # time.sleep(1)
                # pyautogui.press('enter')

                message = f"""<strong><em><span style='color: darkred;font-size:14px;'>{lt("User","用户")}: </span><span style='color: #c0c0c0; font-size:14px;'>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</span></em></strong>"""
                self.messageBrowser.page().runJavaScript('document.body.innerHTML += "' + message + '<br>"')
                message = f"""{self.messageEdit.toPlainText()}"""
                self.messageBrowser.page().runJavaScript('document.body.innerHTML += "' + message + '<br><br>"')

                message = f"""<strong><em><span style='color: darkblue; font-size:14px;'>{self.tr(modelname)}: </span><span style='color: #c0c0c0; font-size:14px;'>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</span></em></strong><br>"""
                self.messageBrowser.page().runJavaScript('document.body.innerHTML += "' + message + '"')

                message = f"""处理完毕！"""
                self.messageBrowser.page().runJavaScript('document.body.innerHTML += "' + message + '<br><br>"')

            elif "学习bak" in self.messageEdit.toPlainText():
                # stocks_handle = StocksHandle()
                # companies = ['google', 'amazon', 'meta', 'apple']
                # stocks_handle.get_Stocks(companies)

                # self.thread = WorkerThreadGP()
                #
                # self.thread.start()

                # print("准备发文件...")
                # os.startfile("C:\Program Files (x86)\Tencent\WeChat\WeChat.exe")
                # time.sleep(1)
                # self.click_image_position("search.png")
                # name = '文件传输助手'
                # pyperclip.copy(name)
                # # 模拟按下和释放Ctr1键和V键
                # pyautogui.hotkey('ctrl', 'v')
                # pyautogui.press('enter')
                # time.sleep(1)  # 避免操作过快
                # self.click_image_position("sendfile.png")
                # directory = os.path.join(Path(__file__).resolve().parent, "temp", "market")
                # NOW = datetime.now()
                # PPTX = f'{directory}-{NOW.month}-{NOW.year}.pptx'
                # file_path = PPTX
                # pyperclip.copy(file_path)
                # pyautogui.hotkey('ctrl', 'v')
                # pyautogui.press('enter')
                # time.sleep(1)
                # pyautogui.press('enter')

                message = f"""<strong><em><span style='color: darkred;font-size:14px;'>{lt("User","用户")}: </span><span style='color: #c0c0c0; font-size:14px;'>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</span></em></strong>"""
                self.messageBrowser.page().runJavaScript('document.body.innerHTML += "' + message + '<br>"')
                message = f"""{self.messageEdit.toPlainText()}"""
                self.messageBrowser.page().runJavaScript('document.body.innerHTML += "' + message + '<br><br>"')

                message = f"""<strong><em><span style='color: darkblue; font-size:14px;'>{self.tr(modelname)}: </span><span style='color: #c0c0c0; font-size:14px;'>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</span></em></strong><br>"""
                self.messageBrowser.page().runJavaScript('document.body.innerHTML += "' + message + '"')

                message = f"""好的，记录下每个步骤，并认真学习！"""
                self.messageBrowser.page().runJavaScript('document.body.innerHTML += "' + message + '<br><br>"')

                time.sleep(1)
                a="a"
                a.lower().startswith()
                print("学习....")
                opr_file_name = self.messageEdit.toPlainText()
                opr_file_name = opr_file_name.replace("学习一下", "")
                opr_file_name = opr_file_name.replace("学习", "")
                os.system(f"python C:/dev/ai-sns/record-and-play-pynput/record-and-play-pynput/record.py {opr_file_name} record-all")

            elif "learn how to" in self.messageEdit.toPlainText() or "//学习" in self.messageEdit.toPlainText() or "//xuexi" in self.messageEdit.toPlainText() or "//xue" in self.messageEdit.toPlainText():
                # message = f"""<strong><em><span style='color: darkred;font-size:14px;'>{lt("User","用户")}: </span><span style='color: #c0c0c0; font-size:14px;'>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</span></em></strong>"""
                # self.messageBrowser.page().runJavaScript('document.body.innerHTML += "' + message + '<br>"')
                page_index=1
                message = get_user_ask_msg_title_formatted(page_index)
                add_msg_to_message_window(self.messageBrowser.page(), message, 1)

                message = get_user_ask_msg_content_formatted(question)
                # add_msg_to_message_window(self.messageBrowser.page(), message, 2)
                add_msg_to_message_windowv3(self.messageBrowser.page(), message, 2)


                # message = f"""{self.messageEdit.toPlainText()}"""
                # self.messageBrowser.page().runJavaScript('document.body.innerHTML += "' + message + '<br><br>"')
                #
                # message = f"""<strong><em><span style='color: darkblue; font-size:14px;'>{self.tr(modelname)}: </span><span style='color: #c0c0c0; font-size:14px;'>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</span></em></strong><br>"""
                # self.messageBrowser.page().runJavaScript('document.body.innerHTML += "' + message + '"')
                #
                # message = f"""好的，记录下每个步骤，并认真学习！"""
                # self.messageBrowser.page().runJavaScript('document.body.innerHTML += "' + message + '<br><br>"')


                time.sleep(1)
                self.agent.give_it_answer_no_thinking(lt("I will record every step.", "我将记录下每个步骤。"))
                print("学习....")
                opr_file_name = self.messageEdit.toPlainText()
                opr_file_name = opr_file_name.replace("学习一下", "")
                opr_file_name = opr_file_name.replace("学习", "")

                if self.learn_operation_bar is None:
                    self.learn_operation_bar = LearnOperationBar(self.application)


                self.learn_operation_bar.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
                self.learn_operation_bar.show()
                self.learn_operation_bar.auto_start()

            elif "//中国象棋" in self.messageEdit.toPlainText():
                tabs = self.tabWidget
                load_plugin(tabs, "中国象棋", "chinese_chess", "ChineseChess", content="red")
                if not self.output_checkbox.isChecked():
                    self.output_checkbox.setChecked(True)
                    self.toggle_output_checkbox(self.output_checkbox.checkState())

            elif "//国际象棋bak" in self.messageEdit.toPlainText():
                tabs = self.tabWidget
                move_str = self.messageEdit.toPlainText().replace("//国际象棋", "")
                chess_view = tabs.findChild(QWebEngineView, "chess")
                if chess_view is None:
                    self.tab_plugin = load_plugin(tabs, "国际象棋", "chess", "Chess", content=move_str)

                    # 设置定时器，5秒后调用 my_function
                    # timer = threading.Timer(1, self.tab_plugin.handle_send_message(self, move_str))
                    #
                    # # 启动定时器
                    # timer.start()
                    return_msg = self.tab_plugin.handle_send_message(self, move_str)
                    # self.messageEdit.setPlainText(return_msg)
                    # self.sendMessage()
                else:
                    # chess_view.page().runJavaScript(f"document.getElementById('allcontent').innerHTML = `{svg}`")
                    return_msg = self.tab_plugin.handle_send_message(self, move_str)
                    self.messageEdit.setPlainText(return_msg)
                    self.sendMessage()

                if not self.output_checkbox.isChecked():
                    self.output_checkbox.setChecked(True)
                    self.toggle_output_checkbox(self.output_checkbox.checkState())

                # return False

            elif "//数字人" in self.messageEdit.toPlainText():
                tabs = self.tabWidget
                move_str = self.messageEdit.toPlainText().replace("//数字人", "")
                digital_human_view = tabs.findChild(QWebEngineView, "digital_human")
                if digital_human_view is None:
                    self.tab_plugin = load_plugin(tabs, lt("DigitalHuman","数字人"), "digital_human", "DigitalHuman", content=move_str)

                    # 设置定时器，5秒后调用 my_function
                    # timer = threading.Timer(1, self.tab_plugin.handle_send_message(self, move_str))
                    #
                    # # 启动定时器
                    # timer.start()
                    return_msg = self.tab_plugin.handle_send_message(self, move_str)
                    # self.messageEdit.setPlainText(return_msg)
                    # self.sendMessage()
                else:
                    # chess_view.page().runJavaScript(f"document.getElementById('allcontent').innerHTML = `{svg}`")
                    return_msg = self.tab_plugin.handle_send_message(self, move_str)
                    self.messageEdit.setPlainText(return_msg)
                    self.sendMessage()

                if not self.output_checkbox.isChecked():
                    self.output_checkbox.setChecked(True)
                    self.toggle_output_checkbox(self.output_checkbox.checkState())

                # return False

            elif self.speaker.status == "wait_for_feedback":
                self.speaker.human_feedback = self.messageEdit.toPlainText()

                page_index = self.increment_page_index()
                message = get_user_ask_msg_title_formatted(page_index)
                add_msg_to_message_window(self.messageBrowser.page(), message, 1)


                message = get_user_ask_msg_content_formatted(question)

                # add_msg_to_message_window(self.messageBrowser.page(), message, 2)
                add_msg_to_message_windowv3(self.messageBrowser.page(), message, 2)
                self.messageBrowser.page().runJavaScript("window.scrollTo(0, document.body.scrollHeight);")

                self.messages_mng.append_message(f"msg_div_{page_index}", {"role": "user", "content": self.messageEdit.toPlainText()})


                page_index = self.increment_page_index()
                # message = get_agent_reply_msg_title_formatted(modelname, page_index)
                message = get_agent_reply_msg_title_formatted(f"{self.agent_cfg.name}: Powered by {modelname}", page_index)
                add_msg_to_message_window(self.messageBrowser.page(), message, 1)



            else:
                task_id = self.task_id
                if task_id == "":
                    task_id = generate_random_id()
                    self.task_id = task_id
                    self.is_first = True

                if len(self.current_attachment_list) > 0:
                    directory_path = os.path.join('resource', 'attachment', 'chat', task_id)
                    os.makedirs(directory_path, exist_ok=True)

                for file_path in self.current_attachment_list:
                    try:
                        shutil.copy(file_path, directory_path)
                    except Exception as e:
                        print(f"Error copying file {file_path}: {e}")

                page_index = self.increment_page_index()
                if self.history_mode_checkbox.isChecked() == True:
                    message = get_user_ask_msg_title_formatted(page_index, show_checkbox="inline-block", checked="checked")
                    # self.set_selected_history_index(page_index, "id_t99999_a", "checked")  # cjr error
                    div_id = f"msg_div_{page_index}"
                    self.messages_mng.append_specified_message_id(div_id)

                else:
                    message = get_user_ask_msg_title_formatted(page_index)
                add_msg_to_message_window(self.messageBrowser.page(), message, 1)

                message = get_user_ask_msg_content_formatted(question)
                # add_msg_to_message_window(self.messageBrowser.page(), message, 2)
                add_msg_to_message_windowv3(self.messageBrowser.page(), message, 2)
                # self.messageBrowser.page().runJavaScript("window.scrollTo(0, document.body.scrollHeight);")#todo cjr 临时关了

                # 处理附件
                if len(self.current_attachment_list) > 0:
                    add_attachment_to_message_window(self.messageBrowser.page(), directory_path, self.current_attachment_list, 2)

                # 设置角色---ok
                # if self.messages[0]["role"] != "system":
                #     self.messages.insert(0, {"role": "system", "content": f"{self.system_role_prompt}"})
                # elif self.messages[0]["role"] == "system":
                #     self.messages[0]["content"] = self.system_role_prompt

                # if "百度" in modelname:#改到后面agent中处理****************cjr
                #     if self.messages[0]["role"] == "system":
                #         self.messages = self.messages[1:]

                self.messages_mng.append_message(f"msg_div_{page_index}", {"role": "user", "content": self.messageEdit.toPlainText()})

                page_index = self.increment_page_index()

                if self.history_mode_checkbox.isChecked() == True:
                    message = get_agent_reply_msg_title_formatted(f"{self.agent_cfg.name}: Powered by {modelname}", page_index, show_checkbox="inline-block", checked="checked")
                else:
                    message = get_agent_reply_msg_title_formatted(f"{self.agent_cfg.name}: Powered by {modelname}", page_index)

                add_msg_to_message_window(self.messageBrowser.page(), message, 1)

                # 挪到顶部了
                # message_handler = self.message_handler
                # web_browser = self.messageBrowser
                # speaker = Speaker(message_handler, web_browser)
                # self.speaker =speaker

                # if self.agent.history_mode == 'specify':
                #     # messages = [{"role": "system", "content": f"{self.system_role_prompt}"}] + self.selected_history_messages
                #     messages = self.selected_history_messages
                #     messages.append({"role": "user", "content": self.messageEdit.toPlainText()})
                # else:
                #     messages = self.messages[:]

                messages = self.messages_mng.get_messages()

                attachment_content_list = self.attachment_content_list

                self.thread = WorkerThread(self.agent, task_id, self.is_first, question, messages, llm_full_name, self.system_role_id, self.system_role_prompt, vector_path, embedding_model_name, modelname, self.messageBrowser, speaker, attachment_content_list, plugin_tool_record_selected_list)
                self.thread.finished.connect(self.onTaskFinished)
                self.thread.start()

                # ***************????????????

            self.messageEdit.clear()
            self.messageEdit.setAcceptRichText(False)
            self.messageEdit.setTextColor(QtGui.QColor(0, 0, 0))
            self.messageEdit.setPlainText("")
            self.messageEdit.setStyleSheet("""
                        QTextEdit {
            border: 0px solid #c0c0c0; /* 边框颜色 */
            border-radius: 8px;       /* 圆角半径 */
            padding: 2px;              /* 内边距 */
            background-color: #F0F0F0; /* 背景颜色 */
        }
            QTextEdit:focus {
                border-color: #146ebe; /* 设置焦点时的边框颜色 */
            }
                    """)
            # self.messageEdit.setAcceptRichText(True)
            if self.agent.chat_mode == 'chat':
                self.stopButton.setVisible(True)
                self.sendButton.setVisible(False)
            self.modelname = modelname
            self.messageEdit.setFocus()

            if self.multi_model_comparison:
                # self.msgbox_model_a.page().runJavaScript('re_init()')
                # self.msgbox_model_b.page().runJavaScript('re_init()')
                # self.msgbox_model_c.page().runJavaScript('re_init()')
                self.multi_model_reply(question, messages, vector_path, embedding_model_name, modelname, attachment_content_list, plugin_tool_record_selected_list)


    def multi_model_reply(self,question, messages, vector_path, embedding_model_name, modelname, attachment_content_list, plugin_tool_record_selected_list):
        task_id="temp_0000"

        if self.model_combobox_a.currentData() != "N/A":
            self.msgbox_model_a.page().runJavaScript('re_init()')
            self.llm_full_name_a =self.model_combobox_a.currentText()
            system_role_id_a = self.prompt_combobox_a.currentData()
            system_role_prompt_a = ""
            self.thread_a = WorkerThread(self.agent_a, task_id, False, question, messages, self.llm_full_name_a, system_role_id_a, system_role_prompt_a, vector_path, embedding_model_name, modelname, self.msgbox_model_a, self.speaker_a, attachment_content_list, plugin_tool_record_selected_list,None,1)
            self.thread_a.finished.connect(self.onTaskFinished_a)
            self.thread_a.start()
            self.button_accept_a.setVisible(False)
            if not self.model_hidden_flag_a:
                self.button_stop_a.setVisible(True)
            self.model_replying_flag_a = True

        if self.model_combobox_b.currentData() != "N/A":
            self.msgbox_model_b.page().runJavaScript('re_init()')
            self.llm_full_name_b =self.model_combobox_b.currentText()
            system_role_id_b = self.prompt_combobox_b.currentData()
            system_role_prompt_b = ""
            self.thread_b = WorkerThread(self.agent_b, task_id, False, question, messages, self.llm_full_name_b, system_role_id_b, system_role_prompt_b, vector_path, embedding_model_name, modelname, self.msgbox_model_b, self.speaker_b, attachment_content_list, plugin_tool_record_selected_list,None,2)
            self.thread_b.finished.connect(self.onTaskFinished_b)
            self.thread_b.start()
            self.button_accept_b.setVisible(False)
            if not self.model_hidden_flag_b:
                self.button_stop_b.setVisible(True)
            self.model_replying_flag_b = True

        if self.model_combobox_c.currentData() != "N/A":
            self.msgbox_model_c.page().runJavaScript('re_init()')
            self.llm_full_name_c =self.model_combobox_c.currentText()
            system_role_id_c = self.prompt_combobox_c.currentData()
            system_role_prompt_c = ""
            self.thread_c = WorkerThread(self.agent_c, task_id, False, question, messages, self.llm_full_name_c, system_role_id_c, system_role_prompt_c, vector_path, embedding_model_name, modelname, self.msgbox_model_c, self.speaker_c, attachment_content_list, plugin_tool_record_selected_list,None,3)
            self.thread_c.finished.connect(self.onTaskFinished_c)
            self.thread_c.start()
            self.button_accept_c.setVisible(False)
            if not self.model_hidden_flag_c:
                self.button_stop_c.setVisible(True)
            self.model_replying_flag_c = True

        multimodellastmodel = self.model_combobox_a.currentData() + ","+ self.model_combobox_b.currentData() + ","+self.model_combobox_c.currentData()
        multimodellastrole = str(self.prompt_combobox_a.currentData()) + "," + str(self.prompt_combobox_b.currentData()) + "," + str(self.prompt_combobox_c.currentData())
        agent_id = self.agent_cfg.id
        update_AgentCfg(agent_id,multimodellastmodel=multimodellastmodel,multimodellastrole=multimodellastrole)

    def stopMessage(self):
        try:
            self.thread.stop()
            del self.thread
        except:
            pass

        print("after deling2")
        self.speaker.stop_speaker = True
        self.stopButton.setVisible(False)
        self.sendButton.setVisible(True)

    def stopMessage_a(self):
        try:
            self.thread_a.stop()
            del self.thread_a
        except:
            pass
        self.speaker_a.stop_speaker = True
        self.button_stop_a.setVisible(False)
        self.button_accept_a.setVisible(True)

    def stopMessage_b(self):
        try:
            self.thread_b.stop()
            del self.thread_b
        except:
            pass
        self.speaker_b.stop_speaker = True
        self.button_stop_b.setVisible(False)
        self.button_accept_b.setVisible(True)

    def stopMessage_c(self):
        try:
            self.thread_c.stop()
            del self.thread_c
        except:
            pass
        self.speaker_c.stop_speaker = True
        self.button_stop_c.setVisible(False)
        self.button_accept_c.setVisible(True)


    def upMessage(self):
        """
        Navigate backward through user messages (from last to first).
        Updates the message editor with the found user message content.
        """
        messages = self.messages_mng.get_messages()

        # Filter messages to only include ones with role 'user'
        user_messages = [msg for msg in messages if msg.get('role') == 'user' and msg.get('content')]

        # Early return if no user messages available
        if not user_messages:
            return None

        # Adjust index for backward navigation
        if self.updown_message_index==0:
            return None
        self.updown_message_index = max(self.updown_message_index - 1, 0) if self.updown_message_index != -1 else len(user_messages) - 1
        if self.updown_message_index<0 or self.updown_message_index>len(user_messages) - 1:
            return None
        current_message = user_messages[self.updown_message_index]
        content = current_message.get("content", "")
        self.messageEdit.setPlainText(content)
        print(f"Up navigation - User message at index {self.updown_message_index}: {current_message}")

        return current_message

    def downMessage(self):
        """
        Navigate forward through user messages (from first to last).
        Updates the message editor with the found user message content.
        """
        messages = self.messages_mng.get_messages()

        # Filter messages to only include ones with role 'user'
        user_messages = [msg for msg in messages if msg.get('role') == 'user' and msg.get('content')]

        # Early return if no user messages available
        if not user_messages:
            return None

        # Adjust index for forward navigation
        if self.updown_message_index == len(user_messages) - 1:
            return None
        self.updown_message_index = min(self.updown_message_index + 1, len(user_messages) - 1) if self.updown_message_index != -1 else 0
        if self.updown_message_index<0 or self.updown_message_index>len(user_messages) - 1:
            return None
        current_message = user_messages[self.updown_message_index]
        content = current_message.get("content", "")
        self.messageEdit.setPlainText(content)
        print(f"Down navigation - User message at index {self.updown_message_index}: {current_message}")

        return current_message

    def onTaskFinished(self, question, content, record_id):
        if self.is_first == True:
            application = self.application
            agent_cfg = self.agent_cfg
            taskList = application.tasklist_list[agent_cfg.user_id]
            taskList.deselect_all_items()
            taskList.addItem(question.replace("\n", "")[:50], record_id, True, False, True)
            # new_item=taskList.addItem(question.replace("\n", "")[:50], record_id, True)
            # new_item.setSelected(True)
            # first_toplevel_item = taskList.topLevelItem(0)
            # first_subitem = first_toplevel_item.child(0)
            # first_subitem.setSelected(True)

        self.is_first = False
        toggle_msg_loading_status(self.messageBrowser.page())
        browser_page = self.messageBrowser.page()
        # add_agent_reply_msg_to_message_window(browser_page,content)已经在agent中处理了
        # self.messages.append({"role": "assistant", "content": content})#转移到后面处理了
        if self.tab_plugin:
            self.tab_plugin.handle_received_message(self, content)

        # 处理插件
        plugin_tool_record_selected_list = self.plugin_tool_record_selected_list
        for record in plugin_tool_record_selected_list:
            if "after_send_b" in record.plugin_event:
                index_event = record.plugin_event.split(",").index("after_send_b")
                instruction_list = []
                instruction = record.instruction
                instructed_flag = False
                run_plugin_flag = False
                if instruction:
                    instruction_list = instruction.split(",")

                for inst in instruction_list:
                    if inst in question:
                        instructed_flag = True

                if instructed_flag:
                    run_plugin_flag = True

                run_plugin_flag = True
                if run_plugin_flag:
                    plugin = self.plugin_tool_loaded_list[record.name]
                    result = plugin.handle_after_send_b(self, content)
                    how_to_handle_executed_result = record.plugin_executed.split(",")[index_event]
                    if how_to_handle_executed_result == "get_output_as_final_result":
                        answer = result
                        return answer
                    else:
                        answer = result

        # 1.将附件列表添加到相应的附件列表全局变量中 2.将附件内容加入相应的问题附件内容 3.将附件全部清理掉
        # 4.将相关的知识召回列表添加到全局变量中 5.将相关的知识召回内容添加到全局变量中 6.清理此次相关的知识召回的信息
        self.messages_attachment_list[self.page_index - 1] = self.current_attachment_list
        # self.messages_attachment_content[self.page_index-1] = self.current_attachment_content

        self.remove_all_attachments()

        question_div_id_old = f"msg_div_{self.page_index - 1}"
        answer_div_id_old = f"msg_div_{self.page_index}"
        question_div_id = "id_" + str(record_id) + "_a"
        answer_div_id = "id_" + str(record_id) + "_r"

        browser_page.runJavaScript('oldId=`' + question_div_id_old + '`')
        browser_page.runJavaScript('newId=`' + question_div_id + '`')
        browser_page.runJavaScript('setDivId(oldId,newId)')

        browser_page.runJavaScript('oldId=`' + answer_div_id_old + '`')
        browser_page.runJavaScript('newId=`' + answer_div_id + '`')
        browser_page.runJavaScript('setDivId(oldId,newId)')

        question_check_id_old = f"msg_checkbox_{self.page_index - 1}"
        answer_check_id_old = f"msg_checkbox_{self.page_index}"
        question_check_id = "id_" + str(record_id) + "_a"
        answer_check_id = "id_" + str(record_id) + "_r"

        browser_page.runJavaScript('oldId=`' + question_check_id_old + '`')
        browser_page.runJavaScript('newId=`' + question_check_id + '`')
        browser_page.runJavaScript('setCheckBoxId(oldId,newId)')

        browser_page.runJavaScript('oldId=`' + answer_check_id_old + '`')
        browser_page.runJavaScript('newId=`' + answer_check_id + '`')
        browser_page.runJavaScript('setCheckBoxId(oldId,newId)')

        if self.is_transfer_to_workflow:
            self.transfer_message_to_workflow(content)



        self.messages_mng.rename_last_key(question_div_id_old, question_div_id)
        self.messages_mng.append_message(answer_div_id, {"role": "assistant", "content": content})

        if self.history_mode_checkbox.isChecked() == True:
            self.messages_mng.append_specified_message_id(answer_div_id)

        if content.startswith("Agent will run Computer Use,@"):
            self.messageEdit.setPlainText(content[28:])
            self.sendMessage()

        self.stopButton.setVisible(False)
        self.sendButton.setVisible(True)

    def onTaskFinished_a(self, question, content, record_id):
        self.model_reply_a=content
        self.model_replying_flag_a=False
        if not self.model_hidden_flag_a:
            self.button_accept_a.setVisible(True)
        self.button_stop_a.setVisible(False)

    def onTaskFinished_b(self, question, content, record_id):
        self.model_reply_b=content
        self.model_replying_flag_b = False
        if not self.model_hidden_flag_b:
            self.button_accept_b.setVisible(True)
        self.button_stop_b.setVisible(False)

    def onTaskFinished_c(self, question, content, record_id):
        self.model_reply_c=content
        self.model_replying_flag_c = False
        if not self.model_hidden_flag_c:
            self.button_accept_c.setVisible(True)
        self.button_stop_c.setVisible(False)

    def run_computer_use(self, **kwargs):
        skill_record = kwargs.get("skill_record",None)
        if self.messageEdit.toPlainText():
            if skill_record:
                self.is_running_skill = True
                skill_id = skill_record.skill_id
                self.agent.give_it_answer_no_thinking(lt("I will run it now.","现在就运行。"))
                self.auto_operate_bar = None
                if self.auto_operate_bar is None:
                    self.auto_operate_bar = AutoOperateBar(self.application)
                self.auto_operate_bar.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
                self.auto_operate_bar.wait_for_input_from_ai_signal.connect(self.request_value_for_auto_operate_bar)
                self.auto_operate_bar.show()
                self.auto_operate_bar.set_skill_id(skill_id)
                self.auto_operate_bar.auto_start()




    def pick_a_tool_to_solve_problem(self, question):
        self.current_ask_agent_to_instruct_flag = "ask_agent_to_select_tool"
        role_prompt = get_prompt_by_title("__select_a_tool__")

        provided_tool_list = self.get_tool_list()

        provided_tool_list_str = json.dumps(provided_tool_list, indent=4, ensure_ascii=False)

        role_prompt = role_prompt.replace("__provided_tool_list__", provided_tool_list_str)
        print(provided_tool_list_str)

        self.ask_agent_and_get_instruction(question, role_prompt)


    def handle_agent_pick_a_tool_result(self, question,content):

        self.task_status = ""
        content = re.sub(r'^\s*```json\s*|\s*```\s*$', '', content, flags=re.DOTALL)
        result_list = json.loads(content)
        if result_list:
            # 使用max函数与lambda表达式来获取match_score最高的工具
            tool = max(result_list, key=lambda x: x["match_score"])
            print("get the tool:",tool)
            id = tool["id"]
            name = tool["name"]
            type_str = tool["type"]
            reason_for_selection = tool["reason_for_selection"]
            match_score = tool["match_score"]

            if type_str =="workflow":
                record = query_workflow_mng(workflow_id=id)
                instruction_content = record.instruction
                self.messageEdit.setPlainText(f"@{instruction_content}:{question}")
                self.sendMessage()

            elif type_str =="plugin":
                record = query_PluginMng(plugin_id=id)
                instruction_content = record.instruction
                self.messageEdit.setPlainText(f"@{instruction_content}:{question}")
                self.sendMessage()

            elif type_str =="function":
                record = query_function_mng(function_id=id)
                instruction_content = record.instruction
                self.messageEdit.setPlainText(f"@{instruction_content}:{question}")
                self.sendMessage()

            elif type_str =="mcp":
                record = query_mcp_mng(mcp_id=id)
                instruction_content = record.instruction
                self.messageEdit.setPlainText(f"@{instruction_content}:{question}")
                self.sendMessage()

            elif type_str =="skill":
                record = query_skill_mng(skill_id=id)
                instruction_content = record.instruction
                self.messageEdit.setPlainText(f"@{instruction_content}:{question}")
                self.sendMessage()

            # flag,res=self.call_tool(tool)


            # if flag=="success":
            #     self.taskmng.add_process_info_to_list("Use_tool使用工具成功，获得如下反馈："+res)
            #     self.taskmng.current_situation = "Use_tool使用工具成功，获得如下反馈：" + res
            #     ask_content = f"- 当前目标\n{self.taskmng.current_objective}\n- 当前进展\nUse_tool使用工具成功，获得如下反馈：{res}"
            #     self.taskmng.process_task(action="process_activity", ask_content=ask_content)
            # elif flag=="fail":
            #     self.taskmng.add_process_info_to_list("Use_tool使用工具失败，获得如下反馈："+res)
            #     self.taskmng.current_situation = "Use_tool使用工具失败，获得如下反馈：" + res
            #     ask_content = f"- 当前目标\n{self.taskmng.current_objective}\n- 当前进展\nUse_tool使用工具失败，获得如下反馈：{res}"
            #     self.taskmng.process_task(action="process_activity", ask_content=ask_content)


    def call_tool(self,tool):

        id = tool["id"]
        name = tool["name"]
        type_str = tool["type"]
        reason_for_selection = tool["reason_for_selection"]
        match_score = tool["match_score"]
        tool_list = self.get_tool_list()
        tool_full = self.get_dict_by_id(tool_list,id)
        if type_str=="Built_in_function":
            flag,result=self.call_built_in_function(tool_full)
            return flag,result
        else:
            flag = "fail"
            result = "任务失败。"
            return flag,result

    def call_built_in_function(self,tool):
        name = tool.get("name","")
        if name=="Check in":
           flag="success"
           result = "打卡成功"
           return flag,result

        elif name == "Get clues":
            flag = "success"
            result = "线索成功"
            return flag,result

        else:
            pass

    def get_dict_by_id(self,dict_list, target_id):
        """
        根据目标 id 从字典列表中查找并返回对应的字典

        :param dict_list: 包含若干字典的列表
        :param target_id: 目标 id 字符串
        :return: 对应 id 的字典，如果没有找到，则返回 None
        """
        # 使用字典推导式将列表转换为以 id 为键的字典，以实现 O(1) 的查找效率
        dict_map = {d['id']: d for d in dict_list}

        # 使用 get 方法返回目标字典，若目标 id 不存在，则返回 None
        return dict_map.get(target_id)


    def get_tool_list(self):

        workflow_list = self.get_workflow_list()
        # llm_list = self.get_llm_list()
        plugin_list = self.get_plugin_list()
        function_list = self.get_function_list()
        skill_list = self.get_skill_list()
        mcp_list = self.get_mcp_list()

        tool_list = workflow_list+plugin_list+function_list+skill_list+mcp_list
        print("tool_list:",tool_list)
        return tool_list

    def get_workflow_list(self):

        # 查询所有工作流程记录
        records = query_workflow_mng_all()

        # 如果没有记录，返回空列表
        if not records:
            return []

        # 使用列表推导式构建字典列表
        result_list = [
            {
                "id": record.workflow_id,  # 设置工作流程的ID
                "name": record.title,  # 设置工作流程的名称
                "description": record.description,  # 设置工作流程的描述
                "type": "workflow"  # 设置工作流程的类型，固定为"workflow"
            }
            for record in records  # 遍历所有记录
        ]

        return result_list  # 返回构建好的字典列表

    def get_llm_list(self):

        # 查询所有工作流程记录
        records = query_PluginMng_All(plugin_type="LLM_Connector")

        # 如果没有记录，返回空列表
        if not records:
            return []

        # 使用列表推导式构建字典列表
        result_list = [
            {
                "id": record.plugin_id,
                "name": record.name,
                "description": record.description,
                "type": "llm"
            }
            for record in records  # 遍历所有记录
        ]

        return result_list  # 返回构建好的字典列表

    def get_plugin_list(self):

        # 查询所有工作流程记录
        records = query_PluginMng_All_Tool(is_delete=0)

        # 如果没有记录，返回空列表
        if not records:
            return []

        # 使用列表推导式构建字典列表
        result_list = [
            {
                "id": record.plugin_id,
                "name": record.name,
                "description": record.description,
                "type": "plugin"
            }
            for record in records  # 遍历所有记录
        ]

        return result_list  # 返回构建好的字典列表

    def get_function_list(self):

        # 查询所有工作流程记录
        records = query_function_mng_all(function_type="1")

        # 如果没有记录，返回空列表
        if not records:
            return []

        # 使用列表推导式构建字典列表
        result_list = [
            {
                "id": record.function_id,  # 设置工作流程的ID
                "name": record.name,  # 设置工作流程的名称
                "description": record.description,  # 设置工作流程的描述
                "type": "function"
            }
            for record in records  # 遍历所有记录
        ]

        return result_list  # 返回构建好的字典列表

    def get_mcp_list(self):

        # 查询所有工作流程记录
        records = query_mcp_mng_all(mcp_type="1")

        # 如果没有记录，返回空列表
        if not records:
            return []

        # 使用列表推导式构建字典列表
        result_list = [
            {
                "id": record.mcp_id,  # 设置工作流程的ID
                "name": record.name,  # 设置工作流程的名称
                "description": record.description,  # 设置工作流程的描述
                "type": "mcp"
            }
            for record in records  # 遍历所有记录
        ]

        return result_list  # 返回构建好的字典列表

    def get_skill_list(self):

        # 查询所有工作流程记录
        records = query_skill_mng_all(skill_type="1")

        # 如果没有记录，返回空列表
        if not records:
            return []

        # 使用列表推导式构建字典列表
        result_list = [
            {
                "id": record.skill_id,
                "name": record.name,
                "description": record.description,
                "type": "skill"
            }
            for record in records  # 遍历所有记录
        ]

        return result_list  # 返回构建好的字典列表



    def setOpenFileName(self):
        openFileNameLabel = ""
        options = QFileDialog.Options()
        native = True
        if not native:
            options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,
                                                  "QFileDialog.getOpenFileName()", openFileNameLabel,
                                                  "All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            openFileNameLabel = fileName
        print(openFileNameLabel)
        return openFileNameLabel

    def new_task_by_btn(self):
        application = self.application
        application.create_new_task_chat(self.agent)

    def add_attachment(self):
        openFilesPath = ""
        openFileNamesLabel = ""
        options = QFileDialog.Options()
        native = True
        filter_extensions = ("Text and Document Files (*.txt *.docx *.csv *.xlsx *.xls *.pptx *.pdf *.md *.html *.htm *.js);;"
                             "Image Files (*.png *.jpg *.bmp *.jpeg *.gif);;"
                             "Text Files (*.txt);;"
                             "Microsoft Word (*.docx);;"
                             "CSV Files (*.csv);;"
                             "Excel Files (*.xlsx);;"
                             "Excel 97-2003 (*.xls);;"
                             "PowerPoint Files (*.pptx);;"
                             "PDF Files (*.pdf);;"
                             "Markdown Files (*.md);;"
                             "HTML Files (*.html *.htm);;"
                             "SQL Files (*.sql);;"
                             "Markdown Files (*.md)")
        if not native:
            options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self,
                                                "QFileDialog.getOpenFileNames()", openFilesPath,
                                                filter_extensions, options=options)

        self.add_attachment_area(files)

    def run_digital_human(self):
        # 使用subprocess启动另一个python应用
        subprocess.Popen(["C:\\dev\\rpa\\Stocks_RPA_Python\\venv\\Scripts\\python.exe",
                          "C:/dev/rpa/Stocks_RPA_Python/framelesswindowv2.py"])

    def opendialog_plugin_tool(self):
        pluginselectedList_tool = self.pluginselectedList_tool
        selected_items = []
        unselected_items = []

        records = query_PluginMng_All_Tool(is_delete=0)

        model = QStandardItemModel()
        header = ["", "plugin_id", lt("name","名称"), lt("Mode","运行模式"), lt("Version","版本"), lt("Desc","功能描述"), lt("Command","插件调用指令"), lt("Operate","操作")]
        model.setHorizontalHeaderLabels(header)

        def create_item(text, editable=False):
            item = QStandardItem(text)
            if not editable:
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            return item

        tool_dict = {f"{record.plugin_id}": record for record in records}

        # Process selected items first according to the order in pluginselectedList
        for selected in pluginselectedList_tool:
            if selected in tool_dict:
                tool = tool_dict.pop(selected)
                row_data = [
                    create_item(tool.plugin_id),
                    create_item(tool.name),
                    create_item({"back_end": lt("Run backend","后台运行"), "show_by_ai_call": lt("Show when called","AI调用时显示插件"), "show_when_activate": lt("Show when activated","启用时显示插件")}.get(tool.run_mode, lt("Run backend","后台运行"))),
                    create_item(tool.version),
                    create_item(tool.description),
                    create_item(tool.instruction),
                    create_item("操作")
                ]
                checkbox_item = QStandardItem()
                # checkbox_item.setCheckable(tool.run_mode=="show_when_activate")
                checkbox_item.setCheckable(True)
                checkbox_item.setCheckState(Qt.Checked)
                row_data.insert(0, checkbox_item)

                selected_items.append((tool, row_data))

        # Process the rest of the items
        for tool in tool_dict.values():
            row_data = [
                create_item(tool.plugin_id),
                create_item(tool.name),
                create_item({"back_end": lt("Run backend","后台运行"), "show_by_ai_call": lt("Show when called","AI调用时显示插件"), "show_when_activate": lt("Show when activated","启用时显示插件")}.get(tool.run_mode, lt("Run backend","后台运行"))),
                create_item(tool.version),
                create_item(tool.description),
                create_item(tool.instruction),
                create_item("操作")
            ]
            checkbox_item = QStandardItem()
            # checkbox_item.setCheckable(tool.run_mode=="show_when_activate")
            checkbox_item.setCheckable(True)
            row_data.insert(0, checkbox_item)
            unselected_items.append((tool, row_data))

        # Combine selected and unselected items
        all_items = selected_items + unselected_items

        # Add items to the model
        for row, (tool, item_row) in enumerate(all_items):
            for col, item in enumerate(item_row):
                model.setItem(row, col, item)

            # Placeholder for button, actual button will be inserted by delegate
            model.setItem(row, 7, QStandardItem())

        # Generate items_per_row based on the order of all_items
        items_per_row = {}
        for i, (tool, _) in enumerate(all_items):
            detail_json = json.loads(tool.detail)
            items_per_row[i] = detail_json.get("model_type", [])

        dialog = PluginFreezeTableDialogTool(model, items_per_row)

        button_delegate = ButtonDelegateTool(dialog.tableView, dialog)
        dialog.tableView.setItemDelegateForColumn(7, button_delegate)

        if dialog.exec_() == QDialog.Accepted:
            pluginselectedList_tool = dialog.getResult()

            self.set_plugin_tool_selected(pluginselectedList_tool)

            print("self.pluginselectedList:", self.pluginselectedList_tool)
            print("self.pluginselectedListjoin:", ",".join(self.pluginselectedList_tool))
            update_AgentCfg(self.agent_cfg.id, last_plugins=",".join(self.pluginselectedList_tool))
            self.agent.reload_agent_cfg()

            # self.plugin_tool_record_selected_list.clear()
            # if self.pluginselectedList_tool:
            #     for plugin_id in self.pluginselectedList_tool:
            #         if plugin_id=='23':
            #             print("数字人，go...")
            #             # 创建线程
            #             thread = threading.Thread(target=self.run_digital_human)
            #
            #             # 启动线程
            #             thread.start()
            #
            #             # 可选：等待线程完成
            #             thread.join()
            #
            #         record = query_PluginMng(plugin_id=plugin_id)
            #         self.plugin_tool_record_selected_list.append(record)
            #         if record.run_mode == "show_when_activate":
            #             self.load_plugin_to_tab(record)

    def open_llm_cfg_dialog(self):
        pluginselectedList = self.llm_fullname_selected_list
        selected_items = []
        unselected_items = []

        llm_records = query_PluginMng_All(is_delete=0, plugin_type="LLM_Connector")
        model = QStandardItemModel()
        header = ["", "plugin_id", lt("Name","名称"), lt("Abbrev","简称"), lt("Model Type","型号"), lt("Version","版本"), lt("Description","功能描述"), lt("Operation","操作"), lt("Favorate","加入常用")]
        model.setHorizontalHeaderLabels(header)

        def create_item(text, editable=False):
            item = QStandardItem(text)
            if not editable:
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            return item

        llm_record_dict = {f"{llmrecord.name}: {llmrecord.version}": llmrecord for llmrecord in llm_records}

        # Process selected items first according to the order in pluginselectedList
        for selected in pluginselectedList:
            if selected in llm_record_dict:
                llm_record = llm_record_dict.pop(selected)
                row_data = [
                    create_item(llm_record.plugin_id),
                    create_item(llm_record.name),
                    create_item(llm_record.alias_name),
                    create_item(json.dumps(llm_record.detail, ensure_ascii=False)),  # Convert JSON to string
                    create_item(llm_record.version),
                    create_item(llm_record.description),
                    create_item("操作"),
                    create_item("加入常用")
                ]
                checkbox_item = QStandardItem()
                checkbox_item.setCheckable(True)
                checkbox_item.setCheckState(Qt.Checked)
                row_data.insert(0, checkbox_item)

                selected_items.append((llm_record, row_data))

        # Process the rest of the items
        for llm_record in llm_record_dict.values():
            row_data = [
                create_item(llm_record.plugin_id),
                create_item(llm_record.name),
                create_item(llm_record.alias_name),
                create_item(json.dumps(llm_record.detail, ensure_ascii=False)),  # Convert JSON to string
                create_item(llm_record.version),
                create_item(llm_record.description),
                create_item("操作"),
                create_item("加入常用")
            ]
            checkbox_item = QStandardItem()
            checkbox_item.setCheckable(True)
            row_data.insert(0, checkbox_item)
            unselected_items.append((llm_record, row_data))

        # Combine selected and unselected items
        all_items = selected_items + unselected_items

        # Add items to the model
        for row, (llm_record, item_row) in enumerate(all_items):
            for col, item in enumerate(item_row):
                model.setItem(row, col, item)

            # Create a combo box for '型号'
            combo_item = QStandardItem("gpt-3.5-turbo")
            model.setItem(row, 4, combo_item)

            # Placeholder for button, actual button will be inserted by delegate
            model.setItem(row, 7, QStandardItem())
            model.setItem(row, 8, QStandardItem())

        # Generate items_per_row based on the order of all_items
        items_per_row = {}
        for i, (llm_record, _) in enumerate(all_items):
            detail_json = json.loads(llm_record.detail)
            # items_per_row[i] = detail_json.get("model_type", [])
            items_per_row[i] = llmmgr.get_model_type_list_by_connector_name(llm_record.name)

        dialog = PluginFreezeTableDialog(model, items_per_row, self)

        combo_delegate = ComboBoxDelegate(items_per_row, dialog.tableView)
        dialog.tableView.setItemDelegateForColumn(4, combo_delegate)
        button_delegate = ButtonDelegate(dialog.tableView, dialog)
        dialog.tableView.setItemDelegateForColumn(7, button_delegate)
        button_delegate_frequent = ButtonDelegateFrequent(dialog.tableView, dialog)
        dialog.tableView.setItemDelegateForColumn(8, button_delegate_frequent)
        # dialog.multi_model_checkbox.setChecked(self.multi_model_comparison)
        if self.multi_model_comparison:
            dialog.multi_model_checkbox.setCheckState(Qt.CheckState.Checked)

        if dialog.exec_() == QDialog.Accepted:
            select_llm = ""
            select_llm = dialog.getResult()
            if select_llm:
                self.llm_fullname_selected_list = select_llm
                print("self.pluginselectedList:", self.llm_fullname_selected_list)
                print("self.pluginselectedListjoin:", ",".join(self.llm_fullname_selected_list))
                # update_AgentCfg(self.agent_cfg.id, plugins=",".join(self.pluginselectedList))
                # self.agent.reset_cfg_plugin_llm()
                # tech_list = self.application.techlist_list[self.agent_cfg.user_id]
                # tech_list.reload()
                self.set_messagebox_placeholder()

            if self.llm_fullname_selected_list:
                select_llm = self.llm_fullname_selected_list[0]
                self.set_llm_frequent_in_combobox(False, select_llm)
            # if dialog.multi_model_checkbox.checkState()==Qt.CheckState.Checked:
            #     if self.multi_model_comparison==False:
            #         self.load_multi_model_tab()
            # else:
            #
            #     if self.multi_model_comparison == True:
            #         self.close_multi_model_tab()


    def opendialogkm(self):
        kmselectedList = self.kmselectedList
        print(kmselectedList)
        selected_items = []
        unselected_items = []

        agents = query_KMCfg_All(is_delete=0, vectorization=1)
        model = QStandardItemModel()
        header = ["", "km_id", lt("Name","名称"), lt("Desc","简介"), lt("Tag","标签"), lt("FilePath","路径")]
        model.setHorizontalHeaderLabels(header)

        def create_item(text, editable=False):
            item = QStandardItem(text)
            if not editable:
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            return item

        agent_dict = {agent.name: agent for agent in agents}

        # Process selected items first according to the order in kmselectedList
        for selected in kmselectedList:
            if selected in agent_dict:
                agent = agent_dict.pop(selected)
                row_data = [
                    create_item(agent.km_id),
                    create_item(agent.name),
                    create_item(agent.memo),
                    create_item(agent.label),
                    create_item(agent.kmpath)
                ]
                checkbox_item = QStandardItem()
                checkbox_item.setCheckable(True)
                checkbox_item.setCheckState(Qt.Checked)
                row_data.insert(0, checkbox_item)
                selected_items.append(row_data)

        # Process the rest of the items
        for agent in agent_dict.values():
            row_data = [
                create_item(agent.km_id),
                create_item(agent.name),
                create_item(agent.memo),
                create_item(agent.label),
                create_item(agent.kmpath)
            ]
            checkbox_item = QStandardItem()
            checkbox_item.setCheckable(True)
            row_data.insert(0, checkbox_item)
            unselected_items.append(row_data)

        # Add selected items to model first
        row = 0
        for item_row in selected_items + unselected_items:
            for col, item in enumerate(item_row):
                model.setItem(row, col, item)
            row += 1

        dialog = KmFreezeTableDialog(model)
        if dialog.exec_() == QDialog.Accepted:
            kmselectedList = dialog.getResult()

            self.set_km_selected(kmselectedList)

            print("self.kmselectedList", self.kmselectedList)
            print("self.kmselectedList:", ",".join(self.kmselectedList))
            update_AgentCfg(self.agent_cfg.id, last_kms=",".join(self.kmselectedList))
            self.agent.reload_agent_cfg()
            # tech_list = self.application.techlist_list[self.agent_cfg.user_id]
            # tech_list.reload()

    def reload_agent_cfg(self):
        self.agent_cfg = query_AgentCfg(id=self.agent_cfg.id)

    def openLink(self, url):
        webbrowser.open(url.toString())

    def generate_imagebak(self, prompt, model="dall-e-3", n=1, size="1024x1024"):
        url = "https://api.openai.com/v1/images/generations"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer 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"  # 确保你已设置环境变量 OPENAI_API_KEY
        }
        data = {
            "model": model,
            "prompt": prompt,
            "n": n,
            "size": size
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            response_json = response.json()
            # 提取 URL 列表
            urls = [item['url'] for item in response_json.get('data', [])]
            return urls  # 返回生成的图像 URL 列表
        else:
            response.raise_for_status()  # 抛出错误以便调试

    def generate_image(self, prompt, model="dall-e-3", n=1, size="1024x1024"):
        # ***dall-e-3的n必须是1
        openai.api_key = "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"
        response = openai.images.generate(
            model=model,
            prompt=prompt,
            n=n,
            size=size,
            response_format="url",
        )

        # 提取 URL 列表
        # urls = [data['url'] for data in response['data']]
        urls = [datum.url for datum in response.data]
        return urls  # 返回生成的图像 URL 列表

    def set_messagebox_placeholder(self):
        if len(self.llm_fullname_selected_list) > 0:
            pluginname = self.llm_fullname_selected_list[0]
            model_type = ""
            if ":" in pluginname:
                model_type = pluginname.split(":")[1]
                pluginname = pluginname.split(":")[0]

            llm = global_plugin_list[pluginname]
















































            config = llm.get_config()
            if model_type:
                modelname = model_type
            else:
                modelname = config.get("model", "")

            modelname = pluginname + f"({modelname})"

            # self.messageEdit.setPlaceholderText("Powered by " + modelname)
            # self.model_label.setText("Powered by " + modelname)
            self.model_label.setText(modelname)

    def save_task_output(self, output):
        print("cjrok the task output:", output)
        question = self.task_command
        answer = output
        attachment_content_list = json.dumps(self.attachment_content_list, ensure_ascii=False)  # km部分已经在agent中进行了处理，添加进去了

        record_id = add_AgentTask(self.task_id, question, question, answer, self.modelname, self.agent_cfg.user_id, self.is_first, attachment_content_list)
        self.onTaskFinished(question, answer, record_id)

        browser_page = self.messageBrowser.page()
        browser_page.runJavaScript('toggleOperatorDisplay()')

    def load_plugin_to_tab(self, plugin_cfg, *args, **kwagrs):
        if not plugin_cfg.name in self.plugin_tool_loaded_list:
            plugin = load_plugin(self, plugin_cfg, *args, **kwagrs)
            self.plugin_tool_loaded_list[plugin_cfg.name] = plugin
        else:
            plugin = self.plugin_tool_loaded_list[plugin_cfg.name]

        if not self.output_checkbox.isChecked():
            # self.output_checkbox.setChecked(True)
            # self.toggle_output_checkbox(self.output_checkbox.checkState())
            self.toggle_sidepane_mode()

        return plugin

    def load_multi_model_tab(self):
        self.multi_model_comparison = True
        # 多模型对比
        self.tab_models = QtWidgets.QWidget()
        self.tab_models.setObjectName("tab_models")
        self.tabLayout_models = QVBoxLayout(self.tab_models)
        self.tabLayout_models.setContentsMargins(0, 0, 0, 0)
        # self.tab_models.setLayout(self.tabLayout_models)

        # self.msgbox_model_a = QtWidgets.QTextEdit(self.tab_models)
        # # self.msgbox_model_a.setFixedHeight(100)
        # self.msgbox_model_a.setReadOnly(True)
        # agent_cfg_a = query_AgentCfg(user_id="001")
        agent_cfg_a = self.agent_cfg
        self.agent_a = Agent(agent_cfg_a)
        self.msgbox_model_a = QWebEngineView(self.tab_models)
        # self.msgbox_model_a.setFixedHeight(140)
        self.msgbox_model_a.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,  # 水平策略
            QtWidgets.QSizePolicy.Policy.Expanding  # 垂直策略
        )
        self.msgbox_model_a.setZoomFactor(0.75)

        global channel_a
        global message_handler_a
        channel_a = QWebChannel()
        message_handler_a = MessageHandler()
        self.message_handler_a = message_handler_a
        self.channel_a = channel_a
        channel_a.registerObject("message_handler", message_handler_a)

        self.msgbox_model_a.page().setWebChannel(channel_a)

        message_handler_a.on_message_runJavaScript.connect(self.runJavaScript_a)

        self.speaker_a = Speaker(message_handler_a, self.msgbox_model_a)
        # self.speaker_a = Speaker_Log()

        self.tabLayout_models.addWidget(self.msgbox_model_a, stretch=1)

        self.hblayout_model_a_opr = QtWidgets.QHBoxLayout(self.tab_models)




        self.model_combobox_a = QtWidgets.QComboBox(self.tab_models)
        self.prompt_combobox_a = QtWidgets.QComboBox(self.tab_models)
        self.model_combobox_a.setMinimumWidth(198)
        self.prompt_combobox_a.setMinimumWidth(120)

        self.button_accept_a = QtWidgets.QPushButton(self.tab_models)
        self.button_accept_a.setText(lt("Take it", "采纳"))
        # self.button_accept_a.clicked.connect(self.accept_model_reply_a)
        self.button_accept_a.mousePressEvent = self.accept_model_reply_a
        self.button_stop_a = QtWidgets.QPushButton(self.tab_models)
        self.button_stop_a.setText(lt("Stop", "停止"))
        self.button_stop_a.clicked.connect(self.stopMessage_a)
        self.button_stop_a.setVisible(False)
        self.button_max_a = QtWidgets.QPushButton(self.tab_models)
        self.button_max_a.setText(lt("Maximum", "放大"))
        self.button_max_a.clicked.connect(lambda:self.multi_model_max("a"))
        self.button_max_a.setShortcut(QtGui.QKeySequence(Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier | Qt.Key.Key_1))
        self.button_restore_a = QtWidgets.QPushButton(self.tab_models)
        self.button_restore_a.setText(lt("Restore", "恢复"))
        self.button_restore_a.clicked.connect(self.multi_model_restore)
        self.button_restore_a.setVisible(False)
        self.button_accept_a.setMaximumWidth(50)
        self.button_stop_a.setMaximumWidth(50)
        self.button_max_a.setMaximumWidth(70)
        self.button_restore_a.setMaximumWidth(70)

        self.hblayout_model_a_opr.addWidget(self.model_combobox_a)
        self.hblayout_model_a_opr.addWidget(self.prompt_combobox_a)
        self.hblayout_model_a_opr.addWidget(self.button_accept_a)
        self.hblayout_model_a_opr.addWidget(self.button_stop_a)
        self.hblayout_model_a_opr.addWidget(self.button_max_a)
        self.hblayout_model_a_opr.addWidget(self.button_restore_a)
        self.hblayout_model_a_opr.setContentsMargins(0, 0, 0, 0)

        self.tabLayout_models.addLayout(self.hblayout_model_a_opr)


        self.line_a = QFrame()
        self.line_a.setFrameShape(QFrame.Shape.HLine)  # 设置为水平线
        self.line_a.setFrameShadow(QFrame.Shadow.Plain)  # 添加凹陷阴影效果
        self.line_a.setLineWidth(1)  # 线宽
        # self.line_a.setStyleSheet("background-color: rgba(255,255,255,0);border:1px solid #a9d7ff;")
        self.line_a.setStyleSheet("background-color: rgba(255,255,255,0);border-top:2px solid #4ca3e0;border-bottom:0px solid #a9d7ff;border-left:0px solid #a9d7ff;border-right:0px solid #a9d7ff;")
        self.tabLayout_models.addWidget(self.line_a)

        # self.msgbox_model_b = QtWidgets.QTextEdit(self.tab_models)
        # self.msgbox_model_b.setReadOnly(True)
        # self.msgbox_model_b.setFixedHeight(100)
        # agent_cfg_b = query_AgentCfg(user_id="002")
        agent_cfg_b = self.agent_cfg
        self.agent_b = Agent(agent_cfg_b)
        self.msgbox_model_b = QWebEngineView(self.tab_models)
        # self.msgbox_model_b.setFixedHeight(140)
        self.msgbox_model_b.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding
        )
        self.msgbox_model_b.setZoomFactor(0.75)

        global channel_b
        global message_handler_b
        channel_b = QWebChannel()
        message_handler_b = MessageHandler()
        self.message_handler_b = message_handler_b
        self.channel_b = channel_b
        channel_b.registerObject("message_handler", message_handler_b)
        self.msgbox_model_b.page().setWebChannel(channel_b)
        message_handler_b.on_message_runJavaScript.connect(self.runJavaScript_b)

        self.speaker_b = Speaker(message_handler_b, self.msgbox_model_b)
        # self.speaker_b = Speaker_Log()

        self.tabLayout_models.addWidget(self.msgbox_model_b, stretch=1)

        self.hblayout_model_b_opr = QtWidgets.QHBoxLayout(self.tab_models)
        self.model_combobox_b = QtWidgets.QComboBox(self.tab_models)
        self.prompt_combobox_b = QtWidgets.QComboBox(self.tab_models)
        self.model_combobox_b.setMinimumWidth(198)
        self.prompt_combobox_b.setMinimumWidth(120)


        self.button_accept_b = QtWidgets.QPushButton(self.tab_models)
        self.button_accept_b.setText(lt("Take it", "采纳"))
        # self.button_accept_b.clicked.connect(self.accept_model_reply_b)
        self.button_accept_b.mousePressEvent = self.accept_model_reply_b
        self.button_stop_b = QtWidgets.QPushButton(self.tab_models)
        self.button_stop_b.setText(lt("Stop", "停止"))
        self.button_stop_b.clicked.connect(self.stopMessage_b)
        self.button_stop_b.setVisible(False)
        self.button_max_b = QtWidgets.QPushButton(self.tab_models)
        self.button_max_b.setText(lt("Maximum", "放大"))
        self.button_max_b.clicked.connect(lambda: self.multi_model_max("b"))
        self.button_max_b.setShortcut(QtGui.QKeySequence(Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier | Qt.Key.Key_2))
        self.button_restore_b = QtWidgets.QPushButton(self.tab_models)
        self.button_restore_b.setText(lt("Restore", "恢复"))
        self.button_restore_b.clicked.connect(self.multi_model_restore)
        self.button_restore_b.setVisible(False)

        self.button_accept_b.setMaximumWidth(50)
        self.button_stop_b.setMaximumWidth(50)
        self.button_max_b.setMaximumWidth(70)
        self.button_restore_b.setMaximumWidth(70)

        self.hblayout_model_b_opr.addWidget(self.model_combobox_b)
        self.hblayout_model_b_opr.addWidget(self.prompt_combobox_b)
        self.hblayout_model_b_opr.addWidget(self.button_accept_b)
        self.hblayout_model_b_opr.addWidget(self.button_stop_b)
        self.hblayout_model_b_opr.addWidget(self.button_max_b)
        self.hblayout_model_b_opr.addWidget(self.button_restore_b)
        self.hblayout_model_b_opr.setContentsMargins(0, 0, 0, 0)

        self.tabLayout_models.addLayout(self.hblayout_model_b_opr)

        # 创建水平分割线
        self.line_b = QFrame()
        self.line_b.setFrameShape(QFrame.Shape.HLine)  # 设置为水平线
        self.line_b.setFrameShadow(QFrame.Shadow.Plain)  # 添加凹陷阴影效果
        # self.line_b.setLineWidth(1)  # 线宽
        self.line_b.setStyleSheet("background-color: rgba(255,255,255,0);border-top:2px solid #4ca3e0;border-bottom:0px solid #a9d7ff;border-left:0px solid #a9d7ff;border-right:0px solid #a9d7ff;")
        self.tabLayout_models.addWidget(self.line_b)


        # self.msgbox_model_c = QtWidgets.QTextEdit(self.tab_models)
        # # self.msgbox_model_c.setFixedHeight(100)
        # self.msgbox_model_c.setReadOnly(True)
        # agent_cfg_c = query_AgentCfg(user_id="003")
        agent_cfg_c = self.agent_cfg
        self.agent_c = Agent(agent_cfg_c)
        self.msgbox_model_c = QWebEngineView(self.tab_models)
        # self.msgbox_model_c.setFixedHeight(140)
        self.msgbox_model_c.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding
        )
        self.msgbox_model_c.setZoomFactor(0.75)

        global channel_c
        global message_handler_c
        channel_c = QWebChannel()
        message_handler_c = MessageHandler()
        self.message_handler_c = message_handler_c
        self.channel_c = channel_c
        channel_c.registerObject("message_handler", message_handler_c)
        self.msgbox_model_c.page().setWebChannel(channel_c)
        message_handler_c.on_message_runJavaScript.connect(self.runJavaScript_c)
        self.speaker_c = Speaker(message_handler_c, self.msgbox_model_c)
        # self.speaker_c = Speaker_Log()
        self.tabLayout_models.addWidget(self.msgbox_model_c, stretch=1)

        self.hblayout_model_c_opr = QtWidgets.QHBoxLayout(self.tab_models)
        self.model_combobox_c = QtWidgets.QComboBox(self.tab_models)
        self.prompt_combobox_c = QtWidgets.QComboBox(self.tab_models)
        self.model_combobox_c.setMinimumWidth(198)
        self.prompt_combobox_c.setMinimumWidth(120)


        self.button_accept_c = QtWidgets.QPushButton(self.tab_models)
        self.button_accept_c.setText(lt("Take it", "采纳"))
        # self.button_accept_c.clicked.connect(self.accept_model_reply_c)
        self.button_accept_c.mousePressEvent = self.accept_model_reply_c
        self.button_stop_c = QtWidgets.QPushButton(self.tab_models)
        self.button_stop_c.setText(lt("Stop", "停止"))
        self.button_stop_c.clicked.connect(self.stopMessage_c)
        self.button_stop_c.setVisible(False)
        self.button_max_c = QtWidgets.QPushButton(self.tab_models)
        self.button_max_c.setText(lt("Maximum", "放大"))
        self.button_max_c.clicked.connect(lambda: self.multi_model_max("c"))
        self.button_max_c.setShortcut(QtGui.QKeySequence(Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier | Qt.Key.Key_3))
        self.button_restore_c = QtWidgets.QPushButton(self.tab_models)
        self.button_restore_c.setText(lt("Restore", "恢复"))
        self.button_restore_c.clicked.connect(self.multi_model_restore)
        self.button_restore_c.setVisible(False)
        self.button_accept_c.setMaximumWidth(50)
        self.button_stop_c.setMaximumWidth(50)
        self.button_max_c.setMaximumWidth(70)
        self.button_restore_c.setMaximumWidth(70)

        self.hblayout_model_c_opr.addWidget(self.model_combobox_c)
        self.hblayout_model_c_opr.addWidget(self.prompt_combobox_c)
        self.hblayout_model_c_opr.addWidget(self.button_accept_c)
        self.hblayout_model_c_opr.addWidget(self.button_stop_c)
        self.hblayout_model_c_opr.addWidget(self.button_max_c)
        self.hblayout_model_c_opr.addWidget(self.button_restore_c)
        self.hblayout_model_c_opr.setContentsMargins(0, 0, 0, 0)

        self.tabLayout_models.addLayout(self.hblayout_model_c_opr)

        qurl_remote_url = QUrl(
            "http://localhost:8900/scripts/taskpagemsgbox.html")

        self.msgbox_model_a.page().load(qurl_remote_url)
        self.msgbox_model_b.page().load(qurl_remote_url)
        self.msgbox_model_c.page().load(qurl_remote_url)


        self.model_combobox_a.currentTextChanged.connect(
            lambda: self.set_role_combo_choice_multi_model(self.model_combobox_a, self.prompt_combobox_a)
        )
        self.model_combobox_b.currentTextChanged.connect(
            lambda: self.set_role_combo_choice_multi_model(self.model_combobox_b, self.prompt_combobox_b)
        )
        self.model_combobox_c.currentTextChanged.connect(
            lambda: self.set_role_combo_choice_multi_model(self.model_combobox_c, self.prompt_combobox_c)
        )

        self.model_combobox_a.clear()
        self.model_combobox_b.clear()
        self.model_combobox_c.clear()

        # 将每个 LLM 模型添加到组合框中
        self.model_combobox_a.addItem(lt("Select a model", "请选择模型"), "N/A")
        self.model_combobox_b.addItem(lt("Select a model", "请选择模型"), "N/A")
        self.model_combobox_c.addItem(lt("Select a model", "请选择模型"), "N/A")
        self.reload_agent_cfg()
        if (self.agent_cfg.multimodelfrequent):

            llm_model_list = query_llm_frequents(belong_to_agent_id=self.agent_cfg.user_id)
            for llm_model in llm_model_list:
                self.model_combobox_a.addItem(llm_model.alias_name, llm_model.name + ":" + llm_model.model_type)
                self.model_combobox_b.addItem(llm_model.alias_name, llm_model.name + ":" + llm_model.model_type)
                self.model_combobox_c.addItem(llm_model.alias_name, llm_model.name + ":" + llm_model.model_type)

        else:
            llm_model_list = llmmgr.get_all_llm_model_list()
            for llm_model in llm_model_list:
                self.model_combobox_a.addItem(llm_model, llm_model)
                self.model_combobox_b.addItem(llm_model, llm_model)
                self.model_combobox_c.addItem(llm_model, llm_model)



        multimodellastmodel = self.agent_cfg.multimodellastmodel
        multimodellastrole = self.agent_cfg.multimodellastrole

        if (multimodellastmodel):
            index = self.model_combobox_a.findData(multimodellastmodel.split(",")[0])
            if index != -1:
                self.model_combobox_a.setCurrentIndex(index)

            index = self.model_combobox_b.findData(multimodellastmodel.split(",")[1])
            if index != -1:
                self.model_combobox_b.setCurrentIndex(index)

            index = self.model_combobox_c.findData(multimodellastmodel.split(",")[2])
            if index != -1:
                self.model_combobox_c.setCurrentIndex(index)


        if(multimodellastrole):
            index = self.prompt_combobox_a.findData(int(multimodellastrole.split(",")[0]))
            if index != -1:
                self.prompt_combobox_a.setCurrentIndex(index)

            index = self.prompt_combobox_b.findData(int(multimodellastrole.split(",")[1]))
            if index != -1:
                self.prompt_combobox_b.setCurrentIndex(index)

            index = self.prompt_combobox_c.findData(int(multimodellastrole.split(",")[2]))
            if index != -1:
                self.prompt_combobox_c.setCurrentIndex(index)


        message_handler_a.on_edit_content_message.connect(self.edit_selected_content)
        message_handler_b.on_edit_content_message.connect(self.edit_selected_content)
        message_handler_c.on_edit_content_message.connect(self.edit_selected_content)


        tab_index=self.tabWidget.addTab(self.tab_models, lt("Compare", "多模型"))

        # 自动切换到新添加的标签页
        self.tabWidget.setCurrentIndex(tab_index)

        if not self.output_checkbox.isChecked():
            self.toggle_sidepane_mode()

    def set_role_combo_choice_multi_model(self,model_combo,role_combo):
        """
        设置角色组合框的选择项，根据选中的模型连接器名称获取相应的角色记录，并将其添加到角色组合框中。

        :return: None
        """
        # 获取当前选择的模型连接器名称，并从中提取实际的名称
        model_connector_name = model_combo.currentData().split(":")[0]

        # 获取与模型连接器名称相关的角色记录
        role_records = get_all_prompt_by_modelname(f"{model_connector_name}")

        # 清空角色组合框以避免重复添加
        role_combo.clear()

        # 检查是否找到了角色记录
        if role_records:
            # 遍历角色记录并将其添加到角色组合框
            for role_record in role_records:
                # 假设 role_record 有一个 `name` 属性或字段用于显示
                role_combo.addItem(role_record.title,role_record.id,)  # 使用 role_record 的名称添加项
        else:
            print(f"No role records found for model: {model_connector_name}")  # 记录未找到的情况

    def accept_model_reply_a(self, event):
        content = self.model_reply_a
        task_id = self.task_id
        model_name = self.llm_full_name_a
        parts = model_name.split(':')
        model_name = f"{parts[0]}({parts[1]})"
        records = query_AgentTask(task_id=task_id)
        record = records[-1]
        first_record_id = record.id
        # 检查鼠标点击的按钮
        if event.button() == Qt.MouseButton.RightButton:
                record = records[0]
                record_id = record.id
                update_AgentTask(record_id, answer=content, model_name=model_name)

        elif event.button() == Qt.MouseButton.LeftButton:
                question=""
                answer = content
                attachment_content_list=""
                add_AgentTask(task_id, question, question, answer, model_name, self.agent_cfg.user_id, False, attachment_content_list)


        application = self.application
        agent_cfg = self.agent_cfg
        taskList = application.tasklist_list[agent_cfg.user_id]
        item = self.find_item_by_id(taskList,first_record_id)
        taskList.on_itemDoubleClicked(item,0)



    def accept_model_reply_b(self, event):
        content = self.model_reply_b
        task_id = self.task_id
        model_name = self.llm_full_name_b
        parts = model_name.split(':')
        model_name = f"{parts[0]}({parts[1]})"
        records = query_AgentTask(task_id=task_id)
        record = records[-1]
        first_record_id = record.id
        # 检查鼠标点击的按钮
        if event.button() == Qt.MouseButton.RightButton:
            record = records[0]
            record_id = record.id
            update_AgentTask(record_id, answer=content, model_name=model_name)

        elif event.button() == Qt.MouseButton.LeftButton:
            question = ""
            answer = content
            attachment_content_list = ""
            add_AgentTask(task_id, question, question, answer, model_name, self.agent_cfg.user_id, False, attachment_content_list)

        application = self.application
        agent_cfg = self.agent_cfg
        taskList = application.tasklist_list[agent_cfg.user_id]
        item = self.find_item_by_id(taskList, first_record_id)
        taskList.on_itemDoubleClicked(item, 0)

    def accept_model_reply_c(self, event):
        content = self.model_reply_c
        task_id = self.task_id
        model_name = self.llm_full_name_c
        parts = model_name.split(':')
        model_name = f"{parts[0]}({parts[1]})"
        records = query_AgentTask(task_id=task_id)
        record = records[-1]
        first_record_id = record.id
        # 检查鼠标点击的按钮
        if event.button() == Qt.MouseButton.RightButton:
            record = records[0]
            record_id = record.id
            update_AgentTask(record_id, answer=content, model_name=model_name)

        elif event.button() == Qt.MouseButton.LeftButton:
            question = ""
            answer = content
            attachment_content_list = ""
            add_AgentTask(task_id, question, question, answer, model_name, self.agent_cfg.user_id, False, attachment_content_list)

        application = self.application
        agent_cfg = self.agent_cfg
        taskList = application.tasklist_list[agent_cfg.user_id]
        item = self.find_item_by_id(taskList, first_record_id)
        taskList.on_itemDoubleClicked(item, 0)


    def multi_model_max(self,flag):
        self.line_a.setVisible(False)
        self.line_b.setVisible(False)
        self.splitter.setSizes([0, 1])
        if flag == "a":
            self.msgbox_model_b.setVisible(False)
            self.msgbox_model_c.setVisible(False)

            self.set_all_widgets_visible_on_layout(self.hblayout_model_b_opr,False)
            self.set_all_widgets_visible_on_layout(self.hblayout_model_c_opr, False)
            self.model_hidden_flag_b = True
            self.model_hidden_flag_c = True

            self.button_restore_a.setVisible(True)
            self.button_max_a.setVisible(False)
            # self.msgbox_model_a.setFixedHeight(500)
        elif flag == "b":
            self.msgbox_model_a.setVisible(False)
            self.msgbox_model_c.setVisible(False)
            self.set_all_widgets_visible_on_layout(self.hblayout_model_a_opr,False)
            self.set_all_widgets_visible_on_layout(self.hblayout_model_c_opr, False)
            self.model_hidden_flag_a = True
            self.model_hidden_flag_c = True

            self.button_restore_b.setVisible(True)
            self.button_max_b.setVisible(False)
            # self.msgbox_model_b.setFixedHeight(500)
        elif flag == "c":
            self.msgbox_model_b.setVisible(False)
            self.msgbox_model_a.setVisible(False)
            self.set_all_widgets_visible_on_layout(self.hblayout_model_a_opr,False)
            self.set_all_widgets_visible_on_layout(self.hblayout_model_b_opr, False)
            self.model_hidden_flag_a = True
            self.model_hidden_flag_b = True

            self.button_restore_c.setVisible(True)
            self.button_max_c.setVisible(False)
            # self.msgbox_model_c.setFixedHeight(500)



    def multi_model_restore(self):
            self.msgbox_model_a.setVisible(True)
            self.msgbox_model_b.setVisible(True)
            self.msgbox_model_c.setVisible(True)
            self.set_all_widgets_visible_on_layout(self.hblayout_model_a_opr, True)
            self.set_all_widgets_visible_on_layout(self.hblayout_model_b_opr, True)
            self.set_all_widgets_visible_on_layout(self.hblayout_model_c_opr, True)
            self.model_hidden_flag_a = False
            self.model_hidden_flag_b = False
            self.model_hidden_flag_c = False

            if self.model_replying_flag_a:
                self.button_accept_a.setVisible(False)
            else:
                self.button_stop_a.setVisible(False)

            if self.model_replying_flag_b:
                self.button_accept_b.setVisible(False)
            else:
                self.button_stop_b.setVisible(False)

            if self.model_replying_flag_c:
                self.button_accept_c.setVisible(False)
            else:
                self.button_stop_c.setVisible(False)

            self.line_a.setVisible(True)
            self.line_b.setVisible(True)

            self.button_restore_a.setVisible(False)
            self.button_max_a.setVisible(True)
            # self.msgbox_model_a.setFixedHeight(140)


            self.button_restore_b.setVisible(False)
            self.button_max_b.setVisible(True)
            # self.msgbox_model_b.setFixedHeight(140)


            self.button_restore_c.setVisible(False)
            self.button_max_c.setVisible(True)
            # self.msgbox_model_c.setFixedHeight(140)

            self.splitter.setSizes([500, 300])


    def set_all_widgets_visible_on_layout(self,opr_layout,is_visible=True):
        """遍历布局中的所有控件，并将它们设置为不可见"""
        for i in range(opr_layout.count()):  # 遍历布局中的控件
            widget = opr_layout.itemAt(i).widget()  # 获取控件
            if widget:  # 确保控件存在
                widget.setVisible(is_visible)  # 设置控件为可见


    def find_item_by_id(self,taskList,record_id):

        """通过 id_value 查找并选中项"""
        id_value_to_find = record_id  # 要查找的 id_value
        found_item = self.find_item(taskList.invisibleRootItem(), id_value_to_find)

        if found_item:
            return found_item
        else:
            return None

    def find_item(self, parent_item, id_value):
        """递归查找树形项"""
        for i in range(parent_item.childCount()):
            item = parent_item.child(i)
            # 检查数据是否匹配
            if item.data(0, Qt.ItemDataRole.UserRole) == id_value:
                return item
            # 递归查找子项
            found_item = self.find_item(item, id_value)
            if found_item:
                return found_item
        return None  # 如果未找到，返回 None


    def close_multi_model_tab(self):
        self.multi_model_comparison = False
        tab = self.tabWidget
        tab_name = lt("Compare", "多模型")
        if tab:
            tab_count = tab.count()  # 获取当前标签页的数量
            for index in range(tab_count):
                if tab.tabText(index) == tab_name:  # 比较标签名称
                    tab.removeTab(index)  # 删除标签页





    def on_message_from_message_handler(self, word):
        """
            处理传入的单词并更新显示内容。

            :param word: 字符串，表示需要处理的单词。
            """
        question = ""
        plugin_tool_record_selected_list = self.plugin_tool_record_selected_list
        for record in plugin_tool_record_selected_list:
            if "replying_a" in record.plugin_event:
                index_event = record.plugin_event.split(",").index("replying_a")
                instruction_list = []
                instruction = record.instruction
                instructed_flag = False
                run_plugin_flag = False
                if instruction:
                    instruction_list = instruction.split(",")

                for inst in instruction_list:
                    if inst in question:
                        instructed_flag = True

                if instructed_flag:
                    run_plugin_flag = True

                run_plugin_flag = True

                if run_plugin_flag:
                    plugin = self.plugin_tool_loaded_list[record.name]
                    result = plugin.handle_replying_a(self, word)
                    how_to_handle_executed_result = record.plugin_executed.split(",")[index_event]
                    if how_to_handle_executed_result == "get_output_as_final_result":
                        answer = result
                        return answer
                    else:
                        # question = result
                        # self.messageEdit.setPlainText(result)
                        pass

        words = self.words
        k = self.words_count

        # 检查单词是否为结束标志
        if word != "__end_speak__":
            # 将单词添加到已有的单词集合中
            words += word

            # 增加计数器
            k += 1

            # 每当计数器为1或是6的倍数时，渲染下一个单词
            if k == 1 or k % 20 == 0:
                self.handle_next_word(words)

        else:
            # 如果单词为结束标志，则渲染剩余的单词
            self.handle_next_word(words)
            self.words = ""
            self.words_count = 0

    def handle_next_word(self, words):
        print("handlingword:", words)

    def ask_agent_and_get_instruction(self, question, system_role_prompt):

        vector_path = ""
        embedding_model_name = ''

        # question = self.current_received_msg

        agent = self.agent
        # agent.give_it_plugin(pluginname)#使用配置里面的第一个
        agent.give_it_km(vector_path, embedding_model_name)
        agent.give_it_role(-1,system_role_prompt)
        self.messages_command = []
        self.messages_command.append({"role": "user", "content": question})

        messages = self.messages_command

        speaker = Speaker_Log()
        agent.give_it_speaker(speaker)

        self.thread_background = WorkerThreadBackGround(agent, question, messages, self.messageBrowser, "NOID00000", None)
        self.thread_background.finished.connect(self.on_agent_return_instruction)
        self.thread_background.start()

    def on_agent_return_instruction(self, question, content):
        if self.current_ask_agent_to_instruct_flag == "waiting_for_feedback_to_auto_operation":
            self.feedback_value_for_auto_operate_bar(content)
        elif self.current_ask_agent_to_instruct_flag == "ask_agent_to_select_tool":
            print(content)
            self.handle_agent_pick_a_tool_result(question,content)


        self.current_ask_agent_to_instruct_flag = ""


    def request_value_for_auto_operate_bar(self, question, img_path):
        print("agent get question:", question)
        print("agent get imgsrc", img_path)
        question = f"我正在指导你填表，如果我说：{question}。你将填入什么内容，请直接提供问题的最终答案，要求：1.不要做任何解释和说明。2.不要重复我的问题。记住这些规则，然后直接给出填入的内容"


        self.current_ask_agent_to_instruct_flag = "waiting_for_feedback_to_auto_operation"
        self.ask_agent_and_get_instruction(question,"你是位经验非常丰富的人。")




    def feedback_value_for_auto_operate_bar(self, value):
        self.auto_operate_bar.feed_bak_from_ai(value)



    def set_km_selected(self, km_list):
        self.kmselectedList = km_list
        if len(km_list) == 0:
            # 设置按钮的样式表，修改边框颜色
            self.kmButton.setStyleSheet("""
                                QPushButton {
                            border: 0px;                /* 默认无边框 */
                            border-radius: 2px;         /* 边框圆角 */
                            padding: 2px;               /* 按钮内边距 */
                            height: 28px;               /* 按钮高度 */
                            width: 28px;                /* 按钮宽度 */
                            margin:0px;
                        }

                            """)
        else:
            self.kmButton.setStyleSheet("""
                                QPushButton {
                             border: 0px;                /* 默认无边框 */
                            border-radius: 2px;         /* 边框圆角 */
                            padding: 2px;               /* 按钮内边距 */
                            height: 28px;               /* 按钮高度 */
                            width: 28px;                /* 按钮宽度 */
                            margin:0px;
                            background:#a9d7ff;
                        }
                            """)

    def set_plugin_tool_selected(self, plugin_tool_list):
        self.pluginselectedList_tool = plugin_tool_list
        if len(plugin_tool_list) == 0:
            # 设置按钮的样式表，修改边框颜色
            self.plugin_button.setStyleSheet("""
                                   QPushButton {
                               border: 0px;                /* 默认无边框 */
                               border-radius: 2px;         /* 边框圆角 */
                               padding: 2px;               /* 按钮内边距 */
                               height: 28px;               /* 按钮高度 */
                               width: 28px;                /* 按钮宽度 */
                               margin:0px 2px 0px 0px;      
                           }

                                    """)
        else:
            self.plugin_button.setStyleSheet("""
                                        QPushButton {
                               border: 0px;                /* 默认无边框 */
                               border-radius: 2px;         /* 边框圆角 */
                               padding: 2px;               /* 按钮内边距 */
                               height: 28px;               /* 按钮高度 */
                               width: 28px;                /* 按钮宽度 */
                               margin:0px 2px 0px 0px;                         
                               background:#a9d7ff;
                                }
                                    """)

        self.plugin_tool_record_selected_list.clear()
        if self.pluginselectedList_tool:
            for plugin_id in self.pluginselectedList_tool:
                if plugin_id == '23':
                    print("数字人，go...")
                    # 创建线程
                    thread = threading.Thread(target=self.run_digital_human)

                    # 启动线程
                    thread.start()

                    # 可选：等待线程完成，会阻塞线程
                    thread.join()#todo会阻塞线程

                record = query_PluginMng(plugin_id=plugin_id)
                self.plugin_tool_record_selected_list.append(record)
                if record.run_mode == "show_when_activate":
                    self.load_plugin_to_tab(record)

    def setup_logging(self):
        """配置日志记录"""
        # 创建日志记录器
        task_id = self.task_id
        if task_id == "":
            task_id = generate_random_id()
            self.task_id = task_id
            self.is_first = True

        self.logger = logging.getLogger("AI-SNS")
        self.logger.setLevel(logging.DEBUG)  # 设置日志级别

        # 创建文件处理器，将日志保存到文件
        log_file_path = os.path.join(os.getcwd(), 'resource', 'attachment', 'chat', task_id)
        os.makedirs(log_file_path, exist_ok=True)

        file_handler = logging.FileHandler(os.path.join(log_file_path, "app.log"))
        file_handler.setLevel(logging.DEBUG)

        # 创建控制台处理器，将日志输出到控制台
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # 创建日志格式
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 将处理器添加到日志记录器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        # 自定义日志处理器，将日志输出到 QTextEdit
        self.text_edit_handler = TextEditHandler(self.textEdit_log)
        self.text_edit_handler.setLevel(logging.DEBUG)
        self.text_edit_handler.setFormatter(formatter)
        self.logger.addHandler(self.text_edit_handler)


        self.agent.give_it_logger(self.logger)

        # """记录日志消息"""
        # self.logger.debug("This is a debug message.")
        # self.logger.info("This is an info message.")
        # self.logger.warning("This is a warning message.")
        # self.logger.error("This is an error message.")
        # self.logger.critical("This is a critical message.")

