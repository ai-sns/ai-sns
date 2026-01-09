import os
import time
import urllib
from datetime import datetime

import openai
import pyautogui
from PyQt6.QtWidgets import QWidget, QFileDialog, QMessageBox, QDialog
from PyQt6.QtCore import QSettings, Qt, QUrl, QFile, QFileInfo, pyqtSignal
from PyQt6.QtGui import QIcon, QStandardItemModel, QStandardItem

from langchainhandler import getvectorkm_String
from ui.ui_TaskPageWidgetGroup import Ui_TaskPageWidget
import hashlib
import webbrowser
import http.client
import json
from pluginsmanager import PluginEngine

import argparse

from pluginsmanager import FileSystem

import urllib.request
import re

import sys
from PyQt6 import QtWidgets, QtGui, QtCore

sys.path.append("..")
sys.path.append("../..")
from kmselect import FreezeTableDialog as KmFreezeTableDialog
from pluginselect_llm import FreezeTableDialog as PluginFreezeTableDialog, ComboBoxDelegate, ButtonDelegate
from pluginselect_llm import FreezeTableDialog as PluginFreezeTableDialog
from pluginselect_llm import FreezeTableDialog as PluginFreezeTableDialog, ComboBoxDelegate, ButtonDelegate, ButtonDelegateFrequent
from pluginselect_tool import FreezeTableDialog as PluginFreezeTableDialogTool, ComboBoxDelegate as ComboBoxDelegateTool, ButtonDelegate as ButtonDelegateTool

from db.DBFactory import add_KMCfg, query_KMCfg_All, update_KMCfg, delete_KMCfg, query_KMCfg
from db.DBFactory import add_PluginMng, query_PluginMng_All, update_PluginMng, delete_PluginMng, query_PluginMng
from db.DBFactory import add_AgentTaskMulti,query_PluginMng_All_Tool
from db.DBFactory import update_MutiAgentCfg
from db.DBFactory import update_AgentCfg,query_AgentCfg
from db.DBFactory import add_AgentTask
from globals import global_plugin_list, global_agent_list
from PyQt6.QtWidgets import QWidget, QFileDialog, QMessageBox, QDialog, QTreeWidgetItemIterator, QPlainTextEdit
from PyQt6.QtCore import QThread, pyqtSignal
from Agent import Agent
# from agentgroup import AgentGroup
from Agent import AgentGroup
from util import generate_random_id, add_msg_to_message_window, get_user_ask_msg_title_formatted, get_user_ask_msg_content_formatted, get_agent_reply_msg_title_formatted, get_agent_reply_msg_content_formatted, toggle_msg_loading_status, add_agent_reply_msg_to_message_window
from pluginsmanager.plugins_gui.tab_plugin import load_plugin
import threading
import logging
from i18n import lt
import re


pyautogui.PAUSE = 0.5
from pathlib import Path
from util import generate_random_id, add_msg_to_message_window, add_msg_to_message_windowv3, get_user_ask_msg_title_formatted, get_user_ask_msg_content_formatted, get_agent_reply_msg_title_formatted, get_agent_reply_msg_content_formatted, toggle_msg_loading_status, add_agent_reply_msg_to_message_window, add_msg_to_message_window_with_markdown_and_highlight, add_attachment_to_message_window, image_to_base64, generate_img_tag
from skilllearning.learn_operation import LearnOperationBar
from skilllearning.auto_operate import AutoOperateBar
import llm_manager as llmmgr
from llm_message_manager import LLMMessageManager



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
    finished = pyqtSignal(str)

    def __init__(self, agent_group, messages, agent_list_to_run_task, pluginname, vector_path, embedding_model_name, agentcfg, task_id, is_first, owner, browser_page, speaker, parent=None):
        super(WorkerThread, self).__init__(parent)
        self.agent_group = agent_group
        self.agent_list_to_run_task = agent_list_to_run_task
        self.pluginname = pluginname
        self.vector_path = vector_path
        self.embedding_model_name = embedding_model_name
        self.agentcfg = agentcfg
        self.task_id = task_id
        self.is_first = is_first
        self.messages = messages
        self.owner = owner
        self.browser_page = browser_page
        self.speaker =speaker

    def run(self):
        agent_group = self.agent_group
        agent_list_to_run_task = self.agent_list_to_run_task
        agent_group.give_it_speaker(self.speaker)
        content = agent_group.start_chat(self.messages, agent_list_to_run_task, self.browser_page,self.task_id)
        topic = ""
        # add_AgentTaskMulti(self.task_id, topic, content, self.owner, self.agentcfg.group_id, self.is_first)
        self.finished.emit(content)


class TaskPageGroup(QWidget, Ui_TaskPageWidget):
    # signal_report_to_commander = pyqtSignal(str, str, str)

    def __init__(self, application, agent_group_cfg):
        super(TaskPageGroup, self).__init__()
        self.agent_group_cfg = agent_group_cfg
        self.name = agent_group_cfg.name
        self.application = application
        self.task_id = ""
        self.is_first = True
        self.task_type = 'group'

        self.page_index = 0
        self.messages = [{"role": "system", "content": "You are a helpful assistant who provides concise and accurate information."}]
        self.task_command = ""

        self.messages_attachment_list = {}
        self.messages_km_list = {}
        self.messages_attachment_content = {}
        self.messages_km_content = {}

        self.words = ""
        self.words_count = 0

        self.pluginselectedList_tool = []
        self.plugin_tool_record_selected_list = []
        self.plugin_tool_loaded_list = {}

        # 指定历史(指定上下文相关)
        self.selected_history_messages = []
        self.selected_history_index = []

        # 附件信息相关
        self.current_attachment_list = []
        # self.current_attachment_content="___________以下是相关附件信息,供你参考___________"
        # self.current_attachment_content = ""  # 合并后的附件内容
        self.attachment_content_list = []  # 附件内容列表
        self.attachment_labels = []  # 存储所有附件标签

        self.conten_menu_closing = False  # 是否正在关闭内容菜单，用于给全选按钮做判断条件

        self.setupUi(self)

        self.messageEdit.setFocus()
        self.messageEdit.installEventFilter(self)
        # Example list of people
        self.personList = [query_AgentCfg(user_id=agent).name for agent in agent_group_cfg.agents.split(",")]


        self.completer = QtWidgets.QCompleter(self.personList, self)
        self.completer.setWidget(self.messageEdit)
        self.completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        self.completer.activated.connect(self.insertCompletion)

        self.sendButton.clicked.connect(self.sendMessage)
        self.stopButton.clicked.connect(self.stopMessage)
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


        self.kmselectedList = []
        if agent_group_cfg.kms != "":
            self.kmselectedList = agent_group_cfg.kms.split(",")
        print(self.kmselectedList)
        self.pluginselectedList = []
        if agent_group_cfg.plugins != "":
            self.pluginselectedList = agent_group_cfg.plugins.split(",")
        print(self.pluginselectedList)
        self.agent_commander_id = agent_group_cfg.agentcommander
        agent_commander = global_agent_list[self.agent_commander_id]  # Altman
        self.agent_commander = agent_commander

        # agent_musk = global_agent_list["002"]  # Musk
        # self.Agent_Musk = agent_musk

        self.agent_group = AgentGroup(agent_group_cfg)

        # self.signal_report_to_commander.connect(self.report_to_commander)

        self.is_browser_page_loaded = False
        self.messageBrowser.page().loadFinished.connect(self.onLoadFinished)  # 第一次可能page没来得及load，所以需要在onload中处理

        # self.messageBrowser.anchorClicked.connect(self.openLink)

    # def eventFilter(self, obj, event):
    #     if obj == self.messageEdit and event.type() == QtCore.QEvent.KeyPress:
    #         if event.text() == "@":
    #             cursor = self.messageEdit.textCursor()
    #             rect = self.messageEdit.cursorRect(cursor)
    #             rect.setWidth(self.completer.popup().sizeHintForColumn(0) + self.completer.popup().verticalScrollBar().sizeHint().width())
    #             self.completer.complete(rect)  # Show completer popup
    #     return super().eventFilter(obj, event)
    #
    # def insertCompletion(self, completion):
    #     cursor = self.messageEdit.textCursor()
    #     cursor.movePosition(QtGui.QTextCursor.Left, QtGui.QTextCursor.KeepAnchor, 1)  # Select the '@'
    #     cursor.insertText("@" + completion + " ")  # Insert '@' and the completion text
    #     self.messageEdit.setTextCursor(cursor)

    def eventFilter(self, obj, event):
        """过滤事件以检测 '@' 键的按下，并显示选择对话框"""
        if obj == self.messageEdit and event.type() == QtCore.QEvent.KeyPress:
            # if event.text() == "@":  # 检测 '@' 键
            if event.text() == "@" or (event.key() == QtCore.Qt.Key.Key_Slash and event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier):
                self.showCompletionDialog()  # 显示选择对话框
                return True  # 事件被处理，返回True
        return super().eventFilter(obj, event)  # 其他事件交给基类处理

    def showCompletionDialog(self):
        """显示对话框，供用户选择内容"""
        choices = self.personList  # 选择项列表

        # 创建QDialog作为对话框
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("选择成员")  # 对话框标题

        layout = QtWidgets.QVBoxLayout(dialog)  # 创建布局
        list_widget = QtWidgets.QListWidget(dialog)  # 创建QListWidget显示选择项
        list_widget.addItems(choices)  # 添加选择项到QListWidget
        layout.addWidget(list_widget)  # 将QListWidget添加到布局

        # 连接选择项点击事件
        list_widget.itemClicked.connect(lambda item: self.insertCompletion(item.text(), dialog))
        # 连接键盘事件，以处理回车键
        list_widget.keyPressEvent = lambda event: self.handleKeyPress(event, list_widget, dialog)
        # 获取光标位置并设置对话框位置
        cursor = self.messageEdit.textCursor()  # 获取当前光标
        cursorRect = self.messageEdit.cursorRect(cursor)  # 获取光标的矩形区域
        # 计算对话框位置为光标的右上方

        # 将光标位置转换为全局坐标
        global_position = self.messageEdit.mapToGlobal(QtCore.QPoint(cursorRect.right(), cursorRect.top() - dialog.sizeHint().height()))
        dialog.move(global_position.x(), global_position.y())  # 设置对话框位置

        dialog.exec()  # 显示对话框并等待用户操作

    def handleKeyPress(self, event, list_widget, dialog):
        """处理键盘事件，特别是回车键"""
        if event.key() == QtCore.Qt.Key.Key_Return or event.key() == QtCore.Qt.Key.Key_Enter:
            # 获取当前选中的项
            current_item = list_widget.currentItem()
            if current_item:
                # 如果有选中的项，则插入内容并关闭对话框
                self.insertCompletion(current_item.text(), dialog)
        else:
            # 调用基类的keyPressEvent以处理其他按键
            super(QtWidgets.QListWidget, list_widget).keyPressEvent(event)

    def insertCompletion(self, completion, dialog):
        """插入用户选择的内容并关闭对话框"""
        cursor = self.messageEdit.textCursor()  # 获取当前光标
        # cursor.movePosition(QtGui.QTextCursor.Left, QtGui.QTextCursor.KeepAnchor, 1)  # 选择 '@'
        cursor.insertText("@" + completion + " ")  # 插入 '@' 和选择的文本
        self.messageEdit.setTextCursor(cursor)  # 更新光标位置
        dialog.accept()  # 关闭对话框

    def onLoadFinished(self):
        self.is_browser_page_loaded = True

    def keyPressEvent(self, event):
        # if event.key() == Qt.Key.Key_F and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
        if event.key() == Qt.Key.Key_F1 and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            print("Ctrl+F detected")
            self.toggle_search_box()

    def increment_page_index(self):
        self.page_index += 1
        return self.page_index

    def set_selected_history_index(self, i, status):
        print("set_selected_history_index i:", i)
        print("set_selected_history_index status", status)
        if status == "checked":
            self.add_selected_history_index(i)
        else:
            self.remove_selected_history_index(i)
        self.get_selected_history_messages()

    def add_selected_history_index(self, i):
        # Check if 'i' is already in 'self.selected_history_index'
        if i not in self.selected_history_index:
            # Insert 'i' into 'self.selected_history_index' in sorted order
            self.selected_history_index.append(i)
            self.selected_history_index.sort()


    def toggle_content_menu(self,status="checked"):
        if status == "checked":
            self.content_menu_group_box.setVisible(True)

            for i in range(self.hboxlayout.count()):
                item = self.hboxlayout.itemAt(i)
                if item.widget():
                    item.widget().setVisible(False)  # 隐藏每个控件

            for i in range(self.hboxlayout1.count()):
                item = self.hboxlayout1.itemAt(i)
                if item.widget():
                    item.widget().setVisible(False)  # 隐藏每个控件

        else:#由关闭按钮触发
            self.conten_menu_closing = True
            self.content_menu_group_box.setVisible(False)

            for i in range(self.hboxlayout.count()):
                item = self.hboxlayout.itemAt(i)
                if item.widget():
                    item.widget().setVisible(True)  # 隐藏每个控件

            for i in range(self.hboxlayout1.count()):
                item = self.hboxlayout1.itemAt(i)
                if item.widget():
                    item.widget().setVisible(True)  # 隐藏每个控件
            self.stopButton.setVisible(False)

            if self.history_mode_checkbox.isChecked()==False:

                self.task_mode_checkboxa.setChecked(False)
                # self.toggle_page_all_checkboxes_status(0)
                self.messageBrowser.page().runJavaScript("hideCheckboxes()")



    def edit_selected_content(self, code_type, text):
        tabs = self.tabWidget
        if code_type.lower() == "markdown" and "```mermaid" in text:
            text=text.replace("```mermaid","")
            print("mermaid")
            editor = tabs.findChild(QPlainTextEdit, "mermaid_editor")
            if editor is None:
                load_plugin(tabs, "Mermaid", "mermaid_editor", "MermaidEditor", content=text)
            else:
                editor.setPlainText(text)

        elif code_type.lower() == "markdown" and (("思维导图" in text and "##" in text) or ("mindmap" in text and "##" in text)) :

            print("mindmap")
            editor = tabs.findChild(QPlainTextEdit, "mindmap_editor")
            if editor is None:
                load_plugin(tabs, "MindMap", "mindmap_editor", "MindMapEditor", content=text)
            else:
                editor.setPlainText(text)
        else:

            editor=tabs.findChild(QPlainTextEdit,"code_editor")
            if editor is None:
                load_plugin(tabs,"编辑器","code_editor","CodeEditor",content=text)
            else:
                editor.setPlainText(text)

        if not self.output_checkbox.isChecked():
            self.output_checkbox.setChecked(True)
            self.toggle_output_checkbox(self.output_checkbox.checkState())


    def get_selected_history_messages(self):
        # Clear the selected_history_messages list first
        self.selected_history_messages.clear()
        self.selected_history_messages = [{"role": "system", "content": f"{self.system_role_prompt}"}]
        # Get the messages corresponding to the indices in selected_history_index
        for index in self.selected_history_index:
            if 0 <= index < len(self.messages):
                self.selected_history_messages.append(self.messages[index])

    def remove_selected_history_index(self, i):
        # Remove the first occurrence of 'i' from 'self.selected_history_index', if it exists
        if i in self.selected_history_index:
            self.selected_history_index.remove(i)

    def new_task(self):
        self.task_id = ""
        self.is_first = True
        self.messages = [{"role": "system", "content": "You are a helpful assistant who provides concise and accurate information."}]
        self.messageBrowser.page().runJavaScript('re_init()')

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

    def sendMessage(self):
        if self.messageEdit.toPlainText():
            task_id = self.task_id
            topic = self.messageEdit.toPlainText()
            content = self.messageEdit.toPlainText()
            owner = lt("User","用户")
            agent_group_cfg = self.agent_group_cfg
            group_id = agent_group_cfg.group_id
            application = self.application
            taskList = application.tasklist_group_list[agent_group_cfg.group_id]

            if task_id == "":
                task_id = generate_random_id()
                self.task_id = task_id

            record_id = add_AgentTaskMulti(task_id, topic, content, owner, group_id, self.is_first)

            if self.is_first:
                taskList.addItem(topic.replace("\n", "")[:50], record_id, True)

            self.is_first = False


            if self.speaker.status == "wait_for_feedback":
                 self.speaker.human_feedback=self.messageEdit.toPlainText()
                 question=self.speaker.human_feedback
                 human_feedback = question
                 page_index = self.increment_page_index()
                 message = get_user_ask_msg_title_formatted(page_index)
                 add_msg_to_message_window(self.messageBrowser.page(), message, 1)
                 message = get_user_ask_msg_content_formatted(question)
                 add_msg_to_message_windowv3(self.messageBrowser.page(), message, 2)

                 self.messageBrowser.page().runJavaScript("window.scrollTo(0, document.body.scrollHeight);")

                 next_agent_process_flag = False
                 need_toggle_flag = True
                 if human_feedback == "ok":
                     need_toggle_flag = True
                     next_agent_process_flag = True
                 if human_feedback == "👨‍💻✔️":
                     need_toggle_flag = False
                     next_agent_process_flag = True
                 if human_feedback == "🆗":
                     need_toggle_flag = False
                     next_agent_process_flag = True
                 if human_feedback == "➡️✔️":
                     need_toggle_flag = False
                     next_agent_process_flag = True
                 if human_feedback == "🏁✔️":
                     need_toggle_flag = False
                     next_agent_process_flag = False

                 if need_toggle_flag:
                   browser_page = self.messageBrowser.page()
                   browser_page.runJavaScript('toggleOperatorDisplay()')



                 if next_agent_process_flag:

                     page_index = self.increment_page_index()

                     memo = self.speaker.memo
                     # 定义前缀
                     prefix = "Agent Manager select the next agent:"

                     agent_userid=memo[len(prefix):].strip()  # strip() 去掉前后空格

                     selected_agent_cfg = query_AgentCfg(user_id=agent_userid)
                     if selected_agent_cfg:
                        modelname = selected_agent_cfg.name+" Powered by ("+selected_agent_cfg.defaultmodel + ")"
                     else:
                        modelname = agent_userid
                     message = get_agent_reply_msg_title_formatted(modelname, page_index)
                     add_msg_to_message_window(self.messageBrowser.page(), message, 1)

            else:

                task_content = self.messageEdit.toPlainText()
                if task_content:
                    page_index = self.increment_page_index()

                    message = get_user_ask_msg_title_formatted(page_index)
                    add_msg_to_message_window(self.messageBrowser.page(), message, 1)
                    message = get_user_ask_msg_content_formatted(task_content)
                    add_msg_to_message_windowv3(self.messageBrowser.page(), message, 2)

                    if len(self.pluginselectedList) > 0:
                        llm_full_name = self.pluginselectedList[0]
                        # modelname = self.pluginselectedList[0]

                    else:
                        llm_full_name = "Baichuan_local:gpt-4o-mini"
                        # modelname = "ChatGLM"

                    if len(self.kmselectedList) > 0:
                        vector_path = self.kmselectedList[0]
                        vector_path = "vector_store"  # 先写死
                        embedding_model_name = 'shibing624/text2vec-bge-large-chinese'
                    else:
                        vector_path = ""
                        embedding_model_name = ""

                    agent_commander = self.agent_commander
                    agent_commander_name = agent_commander.name

                    llm_full_name = agent_commander.agent_cfg.defaultmodel

                    page_index = self.increment_page_index()
                    owner = f"({lt('Group Head', '群主')}){self.tr(agent_commander_name)} Powered by ({llm_full_name})"

                    message = get_agent_reply_msg_title_formatted(owner, page_index)
                    add_msg_to_message_window(self.messageBrowser.page(), message, 1)

                    agent_group = self.agent_group

                    self.messages.append({"role": "user", "content": task_content})
                    messages = self.messages  # 分开两行否则加不进去
                    speaker = self.speaker
                    agent_list_to_run_task = self.agent_group_cfg.agents.split(',')  # 全部是agent的userid

                    self.thread = WorkerThread(agent_group, messages, agent_list_to_run_task, llm_full_name, vector_path, embedding_model_name, self.agent_group_cfg, self.task_id, self.is_first, owner, self.messageBrowser.page(), speaker)
                    self.thread.finished.connect(self.onGroupChatStarted)
                    self.thread.start()


                print("group cjr 001")

            self.messageEdit.clear()


    def show_group_select_agent_title(self,output):

        agent_commander = self.agent_commander
        agent_commander_name = agent_commander.name

        llm_full_name = agent_commander.agent_cfg.defaultmodel

        page_index = self.increment_page_index()
        owner = f"({lt('Group Head', '群主')}){self.tr(agent_commander_name)} Powered by ({llm_full_name})"

        message = get_agent_reply_msg_title_formatted(owner, page_index)
        add_msg_to_message_window(self.messageBrowser.page(), message, 1)

    def stopMessage(self):
        self.thread.stop()

        del self.thread
        print("after deling2")
        self.speaker.stop_speaker = True
        self.stopButton.setVisible(False)
        self.sendButton.setVisible(True)


    def onGroupChatStarted(self, content):

        toggle_msg_loading_status(self.messageBrowser.page())
        # self.signal_report_to_commander.emit("", "", "")

    def showTaskResult(self, agent_name, task_result):
        toggle_msg_loading_status(self.messageBrowser.page())

        # stoploadingstript = "var images = document.getElementsByClassName('imgcls');for (var i = 0; i < images.length; i++) { images[i].style.display = 'none';}"
        # self.messageBrowser.page().runJavaScript(stoploadingstript)

    #     message = task_result
    #
    #     text = message
    #
    #     # 使用正则表达式提取Python代码块
    #     python_code_pattern = re.compile(r'```python(.*?)```', re.DOTALL)
    #     python_code_matches = python_code_pattern.findall(text)
    #
    #     # 打印提取的Python代码块
    #     python_code_list = []
    #
    #     for code_block in python_code_matches:
    #         python_code_list.append(code_block.strip())
    #
    #     # 打印结果
    #     print("Python代码列表:")
    #     i = 0
    #     s = text
    #
    #     answer_list = []
    #     type_list = []
    #     for code in python_code_list:
    #         print("python_code_list length", len(python_code_list))
    #         print("i:", i)
    #         print(code)
    #
    #         substring = code
    #         left_part = s[:s.find(substring)]
    #         right_part = s[s.find(substring) + len(substring):]
    #         print("左边所有字符:", left_part)
    #         print("右边所有字符:", right_part)
    #
    #         left_part = left_part[:left_part.find("```python")]
    #         right_part = right_part[right_part.find("```") + len("```"):]
    #         s = right_part
    #         answer_list.append(left_part.strip())
    #         type_list.append(0)
    #         answer_list.append(code)
    #         type_list.append(1)
    #
    #         i += 1
    #         if len(python_code_list) == i:
    #             answer_list.append(right_part.strip())
    #             type_list.append(0)
    #
    #     print("show all list *************************")
    #     j = 0
    #     scriptStr = ""
    #     if len(answer_list) > 0:
    #         for answer in answer_list:
    #             print("*******", j, "***********")
    #             print("type_list:", type_list[j])
    #
    #             if type_list[j] == 1:
    #
    #                 copyhtml = """<div style="margin-top:15px;border:solid 0px red;width:100%;overflow: hidden; ">
    #                         <span href="#" class="codetype" id="codetype" style="float: left;text-decoration:none">代码类型:Python</span>
    #                         <span style="float: right;"><span id="yifuzhi{}" style="font-size:10pt;color:red;display:none">已经复制到剪切板了&nbsp;&nbsp;&nbsp;&nbsp;</span><a href="#" class="copy-link" id="copyCodeLink{}">复制代码</a></span>
    #                     </div>""".format(j, j)
    #             else:
    #                 copyhtml = """<div style="border:solid 0px red;width:100%;overflow: hidden;display:none ">
    #                         <span href="#" class="codetype" id="codetype" style="float: left;text-decoration:none">Python</span>
    #                         <span style="float: right;"><span id="yifuzhi{}" style="font-size:10pt;color:red;display:none">已经复制到剪切板了&nbsp;&nbsp;&nbsp;&nbsp;</span><a href="#" class="copy-link" id="copyCodeLink{}">复制代码</a></span>
    #                     </div>""".format(j, j)
    #
    #             print("copyhtml:", copyhtml)
    #             self.messageBrowser.page().runJavaScript('document.body.innerHTML += `' + copyhtml + '<br><br>`')
    #
    #             print(answer)
    #             message = answer
    #
    #             if type_list[j] == 1:
    #                 self.messageBrowser.page().runJavaScript("document.body.innerHTML += " + "\"<pre style='margin-top:-50px'><code id='codeToCopy" + str(j) + "' style='border:solid 1px #c0c0c0' class='language-python'></code></pre>\"")
    #             else:
    #                 self.messageBrowser.page().runJavaScript("document.body.innerHTML += " + "\"<pre id='codeToCopy" + str(j) + "' style='margin-top:-50px;border:solid 0px #c0c0c0;width: 99%; paddingbak: 10px; white-space: pre-wrap; word-wrap: break-word;  overflow-wrap: break-word;' class='language-python'></pre>\"")
    #
    #             message = message.replace('`', '\\`')
    #             message = f"""`{message}`"""
    #             self.messageBrowser.page().runJavaScript("$('#codeToCopy" + str(j) + "').html(" + message + ");")
    #             self.messageBrowser.page().runJavaScript("hljs.highlightBlock(document.getElementById('codeToCopy" + str(j) + "'));")
    #
    #             # self.messageBrowser.page().runJavaScript("document.body.innerHTML += " + "\"<pre style='margin-top:-50px'><code id='codeToCopy' style='border:solid 1px #c0c0c0' class='language-python'></code></pre>\"")
    #             # self.messageBrowser.page().runJavaScript("$('#codeToCopy').html(" + message + ");")
    #             # #self.messageBrowser.page().runJavaScript("hljs.highlightAll();")
    #             # self.messageBrowser.page().runJavaScript("hljs.highlightBlock(document.getElementById('codeToCopy'));")#$('#codeToCopy')
    #
    #             scriptStr = scriptStr + """
    # document.getElementById('copyCodeLink{}').addEventListener('click', function (e) {{
    #     e.preventDefault();
    #     copyCode{}();
    # }});
    #
    # function copyCode{}() {{
    #     var code = document.getElementById('codeToCopy{}');
    #     var range = document.createRange();
    #     range.selectNode(code);
    #     window.getSelection().removeAllRanges();
    #     window.getSelection().addRange(range);
    #     document.execCommand('copy');
    #     window.getSelection().removeAllRanges();
    #     $("#yifuzhi{}").show();
    #     setTimeout(function () {{
    #     $("#yifuzhi{}").hide();
    # }}, 1500);
    # }}""".format(j, j, j, j, j, j)
    #             print("scripts:", scriptStr)
    #             # self.messageBrowser.page().runJavaScript('document.body.innerHTML += `' + message + '<br><br>`')
    #
    #             j += 1
    #     else:
    #         self.messageBrowser.page().runJavaScript('document.body.innerHTML += `<pre style="width: 99%; paddingbak: 10px; white-space: pre-wrap; word-wrap: break-word;  overflow-wrap: break-word; ">' + message + '</pre><br>`')
    #     if scriptStr != "":
    #         self.messageBrowser.page().runJavaScript(scriptStr)



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
        application=self.application
        application.open_multi_agent_task_chat(self.agent_group_cfg)

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
                             "Markdown Files (*.md)")
        if not native:
            options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self,
                                                "QFileDialog.getOpenFileNames()", openFilesPath,
                                                filter_extensions, options=options)

        self.add_attachment_area(files)


    def opendialogplugin(self):
        pluginselectedList = self.pluginselectedList
        selected_items = []
        unselected_items = []

        agents = query_PluginMng_All(is_delete=0)
        model = QStandardItemModel()
        header = ["", "plugin_id", "名称", "简称", "型号", "版本", "功能描述", "操作"]
        model.setHorizontalHeaderLabels(header)

        def create_item(text, editable=False):
            item = QStandardItem(text)
            if not editable:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            return item

        agent_dict = {f"{agent.name}: {agent.version}": agent for agent in agents}

        # Process selected items first according to the order in pluginselectedList
        for selected in pluginselectedList:
            if selected in agent_dict:
                agent = agent_dict.pop(selected)
                row_data = [
                    create_item(agent.plugin_id),
                    create_item(agent.name),
                    create_item(agent.alias_name),
                    create_item(json.dumps(agent.detail, ensure_ascii=False)),  # Convert JSON to string
                    create_item(agent.version),
                    create_item(agent.description),
                    create_item("操作")
                ]
                checkbox_item = QStandardItem()
                checkbox_item.setCheckable(True)
                checkbox_item.setCheckState(Qt.CheckState.Checked)
                row_data.insert(0, checkbox_item)

                selected_items.append((agent, row_data))

        # Process the rest of the items
        for agent in agent_dict.values():
            row_data = [
                create_item(agent.plugin_id),
                create_item(agent.name),
                create_item(agent.alias_name),
                create_item(json.dumps(agent.detail, ensure_ascii=False)),  # Convert JSON to string
                create_item(agent.version),
                create_item(agent.description),
                create_item("操作")
            ]
            checkbox_item = QStandardItem()
            checkbox_item.setCheckable(True)
            row_data.insert(0, checkbox_item)
            unselected_items.append((agent, row_data))

        # Combine selected and unselected items
        all_items = selected_items + unselected_items

        # Add items to the model
        for row, (agent, item_row) in enumerate(all_items):
            for col, item in enumerate(item_row):
                model.setItem(row, col, item)

            # Create a combo box for '型号'
            combo_item = QStandardItem("gpt-3.5-turbo")
            model.setItem(row, 4, combo_item)

            # Placeholder for button, actual button will be inserted by delegate
            model.setItem(row, 7, QStandardItem())

        # Generate items_per_row based on the order of all_items
        items_per_row = {}
        for i, (agent, _) in enumerate(all_items):
            detail_json = json.loads(agent.detail)
            items_per_row[i] = detail_json.get("model_type", [])

        dialog = PluginFreezeTableDialog(model, items_per_row)

        combo_delegate = ComboBoxDelegate(items_per_row, dialog.tableView)
        dialog.tableView.setItemDelegateForColumn(4, combo_delegate)
        button_delegate = ButtonDelegate(dialog.tableView, dialog)
        dialog.tableView.setItemDelegateForColumn(7, button_delegate)

        if dialog.exec() == QDialog.Accepted:
            self.pluginselectedList = dialog.getResult()
            print("self.pluginselectedList:", self.pluginselectedList)
            print("self.pluginselectedListjoin:", ",".join(self.pluginselectedList))
            # update_AgentCfg(self.agent_cfg.id, plugins=",".join(self.pluginselectedList))
            # self.agent.reset_cfg_plugin_llm()
            # tech_list = self.application.techlist_list[self.agent_cfg.user_id]
            # tech_list.reload()
            # self.set_messagebox_placeholder()

    def opendialog_plugin_tool(self):
        pluginselectedList_tool = self.pluginselectedList_tool
        selected_items = []
        unselected_items = []

        agents = query_PluginMng_All_Tool(is_delete=0)

        model = QStandardItemModel()
        header = ["", "plugin_id", "名称", "运行模式", "版本", "功能描述", "插件调用指令", "操作"]
        model.setHorizontalHeaderLabels(header)

        def create_item(text, editable=False):
            item = QStandardItem(text)
            if not editable:
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            return item

        agent_dict = {f"{agent.plugin_id}": agent for agent in agents}

        # Process selected items first according to the order in pluginselectedList
        for selected in pluginselectedList_tool:
            if selected in agent_dict:
                agent = agent_dict.pop(selected)
                row_data = [
                    create_item(agent.plugin_id),
                    create_item(agent.name),
                    create_item({"back_end": "后台运行", "show_by_ai_call": "AI调用时显示插件", "show_when_activate": "启用时显示插件"}.get(agent.run_mode, "后台运行")),
                    create_item(agent.version),
                    create_item(agent.description),
                    create_item(agent.instruction),
                    create_item("操作")
                ]
                checkbox_item = QStandardItem()
                checkbox_item.setCheckable(True)
                checkbox_item.setCheckState(Qt.Checked)
                row_data.insert(0, checkbox_item)

                selected_items.append((agent, row_data))

        # Process the rest of the items
        for agent in agent_dict.values():
            row_data = [
                create_item(agent.plugin_id),
                create_item(agent.name),
                create_item({"back_end": "后台运行", "show_by_ai_call": "AI调用时显示插件", "show_when_activate": "启用时显示插件"}.get(agent.run_mode, "后台运行")),
                create_item(agent.version),
                create_item(agent.description),
                create_item(agent.instruction),
                create_item("操作")
            ]
            checkbox_item = QStandardItem()
            checkbox_item.setCheckable(True)
            row_data.insert(0, checkbox_item)
            unselected_items.append((agent, row_data))

        # Combine selected and unselected items
        all_items = selected_items + unselected_items

        # Add items to the model
        for row, (agent, item_row) in enumerate(all_items):
            for col, item in enumerate(item_row):
                model.setItem(row, col, item)

            # Placeholder for button, actual button will be inserted by delegate
            model.setItem(row, 7, QStandardItem())

        # Generate items_per_row based on the order of all_items
        items_per_row = {}
        for i, (agent, _) in enumerate(all_items):
            detail_json = json.loads(agent.detail)
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

        agents = query_PluginMng_All(is_delete=0, plugin_type="LLM_Connector")
        model = QStandardItemModel()
        header = ["", "plugin_id", lt("Name","名称"), lt("Abbrev","简称"), lt("Model Type","型号"), lt("Version","版本"), lt("Description","功能描述"), lt("Operation","操作"), lt("Favorate","加入常用")]
        model.setHorizontalHeaderLabels(header)

        def create_item(text, editable=False):
            item = QStandardItem(text)
            if not editable:
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            return item

        agent_dict = {f"{agent.name}: {agent.version}": agent for agent in agents}

        # Process selected items first according to the order in pluginselectedList
        for selected in pluginselectedList:
            if selected in agent_dict:
                agent = agent_dict.pop(selected)
                row_data = [
                    create_item(agent.plugin_id),
                    create_item(agent.name),
                    create_item(agent.alias_name),
                    create_item(json.dumps(agent.detail, ensure_ascii=False)),  # Convert JSON to string
                    create_item(agent.version),
                    create_item(agent.description),
                    create_item("操作"),
                    create_item("加入常用")
                ]
                checkbox_item = QStandardItem()
                checkbox_item.setCheckable(True)
                checkbox_item.setCheckState(Qt.Checked)
                row_data.insert(0, checkbox_item)

                selected_items.append((agent, row_data))

        # Process the rest of the items
        for agent in agent_dict.values():
            row_data = [
                create_item(agent.plugin_id),
                create_item(agent.name),
                create_item(agent.alias_name),
                create_item(json.dumps(agent.detail, ensure_ascii=False)),  # Convert JSON to string
                create_item(agent.version),
                create_item(agent.description),
                create_item("操作"),
                create_item("加入常用")
            ]
            checkbox_item = QStandardItem()
            checkbox_item.setCheckable(True)
            row_data.insert(0, checkbox_item)
            unselected_items.append((agent, row_data))

        # Combine selected and unselected items
        all_items = selected_items + unselected_items

        # Add items to the model
        for row, (agent, item_row) in enumerate(all_items):
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
        for i, (agent, _) in enumerate(all_items):
            detail_json = json.loads(agent.detail)
            # items_per_row[i] = detail_json.get("model_type", [])
            items_per_row[i] = llmmgr.get_model_type_list_by_connector_name(agent.name)

        dialog = PluginFreezeTableDialog(model, items_per_row, self)

        combo_delegate = ComboBoxDelegate(items_per_row, dialog.tableView)
        dialog.tableView.setItemDelegateForColumn(4, combo_delegate)
        button_delegate = ButtonDelegate(dialog.tableView, dialog)
        dialog.tableView.setItemDelegateForColumn(7, button_delegate)
        button_delegate_frequent = ButtonDelegateFrequent(dialog.tableView, dialog)
        dialog.tableView.setItemDelegateForColumn(8, button_delegate_frequent)

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



    def opendialogkm(self):
        kmselectedList = self.kmselectedList
        print(kmselectedList)
        selected_items = []
        unselected_items = []

        agents = query_KMCfg_All(is_delete=0)
        model = QStandardItemModel()
        header = ["", "km_id", "名称", "简介", "标签", "路径"]
        model.setHorizontalHeaderLabels(header)

        def create_item(text, editable=False):
            item = QStandardItem(text)
            if not editable:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
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
                checkbox_item.setCheckState(Qt.CheckState.Checked)
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
        if dialog.exec() == QDialog.Accepted:
            self.kmselectedList = dialog.getResult()
            print("self.kmselectedList", self.kmselectedList)
            print("self.kmselectedList:", ",".join(self.kmselectedList))
            # update_AgentCfg(self.agent_cfg.id, kms=",".join(self.kmselectedList))
            # self.agent.reload_agent_cfg()
            # tech_list = self.application.techlist_list[self.agent_cfg.user_id]
            # tech_list.reload()

    def openLink(self, url):
        webbrowser.open(url.toString())

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
        if len(self.pluginselectedList) > 0:
            pluginname = self.pluginselectedList[0]
            llm = global_plugin_list[pluginname]
            config = llm.get_config()
            modelname = config.get("model", "")
            modelname = pluginname + f"({modelname})"
            self.messageEdit.setPlaceholderText("Powered by " + modelname)

    def save_task_output(self, output):
        print("cjrok the task output:", output)
        topic = self.task_command
        content = output


        agent_commander = self.agent_commander
        agent_commander_name = agent_commander.name

        llm_full_name = agent_commander.agent_cfg.defaultmodel

        owner = f"({lt('Group Head', '群主')}){self.tr(agent_commander_name)} Powered by ({llm_full_name})"





        add_AgentTaskMulti(self.task_id, topic, content, owner, self.agent_group_cfg.group_id, self.is_first)

        browser_page = self.messageBrowser.page()
        browser_page.runJavaScript('toggleOperatorDisplay()')


        # self.modelname="gpt4-ooo"
        # record_id = add_AgentTask(self.task_id, question, question, answer, self.modelname, self.agent_cfg.user_id, self.is_first, attachment_content_list)
        # self.onTaskFinished(question, answer, record_id)


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
            if k == 1 or k % 6 == 0:
                self.handle_next_word(words)

        else:
            # 如果单词为结束标志，则渲染剩余的单词
            self.handle_next_word(words)
            self.words = ""
            self.words_count = 0

    def handle_next_word(self, words):
        print("handlingword:", words)

    def request_value_for_auto_operate_bar(self, question, img_path):
        print("agent get question:", question)
        print("agent get imgsrc", img_path)
        self.pre_system_role_prompt = self.system_role_prompt
        # self.system_role_prompt = "请直接提供问题的最终答案，要求：1.不要做任何解释和说明。2.不要重复我的问题。记住这些规则，然后回答我的问题"
        # question = "请直接提供问题的最终答案，要求：1.不要做任何解释和说明。2.不要重复我的问题。记住这些规则，然后回答我的问题，我的问题是：" + question
        question = f"我正在指导你填表，如果我说：{question}。你将填入什么内容，请直接提供问题的最终答案，要求：1.不要做任何解释和说明。2.不要重复我的问题。记住这些规则，然后直接给出填入的内容"

        self.is_waiting_for_feedback_to_auto_operation = True
        self.messageEdit.setPlainText(question)
        self.sendMessage()

    def feedback_value_for_auto_operate_bar(self, value):
        self.auto_operate_bar.feed_bak_from_ai(value)
        self.is_waiting_for_feedback_to_auto_operation = False
        self.system_role_prompt = self.pre_system_role_prompt

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
                               margin:0px;
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

                    # 可选：等待线程完成
                    thread.join()

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

    def set_message_checked(self, i, id, status):
        print("set_selected_history_index i:", i)
        print("set_selected_history_index id", id)
        print("set_selected_history_index status", status)
        if status == "checked":
            self.messages_mng.append_specified_message_id(id)
        else:
            self.messages_mng.remove_specified_message_id(id)

