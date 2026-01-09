import copy
import re
import zipfile
import shutil
import sys
import time
from PyQt6 import QtCore, QtGui, QtWidgets

import math

from PyQt6.QtCore import (pyqtSignal, QLineF, QPointF, QRect, QRectF, QSize,
                          QSizeF, Qt)
from PyQt6.QtGui import (QAction, QBrush, QColor, QFont, QIcon, QIntValidator, QPainter,
                         QPainterPath, QPen, QPixmap, QPolygonF, QCursor)
from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest
from PyQt6.QtWidgets import (QApplication, QButtonGroup, QComboBox,
                             QFontComboBox, QGraphicsItem, QGraphicsLineItem, QGraphicsPolygonItem,
                             QGraphicsScene, QGraphicsTextItem, QGraphicsView, QGridLayout,
                             QHBoxLayout, QLabel, QMainWindow, QMenu, QMessageBox, QSizePolicy,
                             QToolBox, QToolButton, QWidget, QToolBar, QDialog, QTabWidget, QLineEdit, QVBoxLayout, QFormLayout)

from PyQt6.QtCore import QDir, Qt
from PyQt6.QtGui import QFont, QPalette
from PyQt6.QtWidgets import (QApplication, QCheckBox, QColorDialog, QDialog,
                             QErrorMessage, QFileDialog, QFontDialog, QFrame, QGridLayout,
                             QInputDialog, QLabel, QLineEdit, QMessageBox, QPushButton, QStatusBar)

from PyQt6.QtCore import QFile, QFileInfo, Qt
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QApplication, QDialog, QHeaderView, QTableView, QVBoxLayout

# from TaskListGroupLabel import TaskListGroupLabel
from NoteListLabel import NoteListLabel
from TaskListGroupLabel import TaskListGroupLabel
from model_metric import ModelEvaluationDialog
import numpy as np

sys.path.append("..")
sys.path.append("../..")
import MainWindow_rc

from TaskPage import TaskPage
from TaskPageGroup import TaskPageGroup
from configdialog import ConfigDialog
from wizardconfigdialog import ConfigDialog as WizardConfigDialog
from userconfigdialog import ConfigDialog as UserConfigDialog
from agentconfigdialog import ConfigDialog as AgentConfigDialog
from agentmuticonfigdialog import ConfigDialog as AgentMutiConfigDialog
from aichatconfigdialog import ConfigDialog as AiChatConfigDialog
from aimapconfigdialog import ConfigDialog as AiMapConfigDialog
from aimaptaskdialog import ConfigDialog as AiMapTaskDialog
from humanchatconfigdialog import ConfigDialog as HumanChatConfigDialog
from kmconfigdialog import ConfigDialog as KmConfigDialog
from agentmng import FreezeTableDialog as AgentFreezeTableDialog
from agentmultimng import FreezeTableDialog as AgentMultiFreezeTableDialog
from aiaccountmng import FreezeTableDialog as AiFreezeTableDialog
from humanaccountmng import FreezeTableDialog as HumanFreezeTableDialog
from kmmng import FreezeTableDialog as KmFreezeTableDialog
from llm_arrange import FreezeTableDialog as LLMArrangeFreezeTableDialog
from logsmng import FreezeTableDialog as LogsFreezeTableDialog
from PyQt6.QtWebEngineWidgets import QWebEngineView
from db.DBFactory import add_AgentCfg, query_AgentCfg_All, update_AgentCfg, delete_AgentCfg, query_AgentCfg, query_web_mng_all
from db.DBFactory import add_KMData, query_KMData_All, update_KMData, delete_KMData, query_KMData, query_AiChatCfg_map, query_AiChatCfg_common
from db.DBFactory import add_KMCfg, query_KMCfg_All, update_KMCfg, delete_KMCfg, query_KMCfg
from db.DBFactory import add_HumanChatCfg, query_HumanChatCfg_All, update_HumanChatCfg, delete_HumanChatCfg, \
    query_HumanChatCfg
from db.DBFactory import add_AiChatCfg, query_AiChatCfg_All, update_AiChatCfg, delete_AiChatCfg, query_AiChatCfg
from db.DBFactory import add_MutiAgentCfg, query_MutiAgentCfg_All, update_MutiAgentCfg, delete_MutiAgentCfg, \
    query_MutiAgentCfg
from db.DBFactory import add_PluginMng, query_PluginMng_All, query_PluginMng, update_PluginMng, delete_PluginMng, \
    query_PluginMng_All_Tool
from db.DBFactory import add_LogsMng, query_LogsMng_All, update_LogsMng, delete_LogsMng, query_LogsMng, add_web_mng
import db.DBFactory as dbfactory

from pluginsmanager import PluginEngine
from pluginsmanager.plugins_headless.plugin_mng import load_plugin as load_plugin_tool
from workflow_manager import WorkFlowManager
from task_schedule import TaskSchedule
from prompts import PromptDialog, PromptManager, MainWindow as Prompt_Manager
import argparse

from shutil import copy2

from pluginsmanager import FileSystem

from langchainhandler import *
import os
from pathlib import Path
from globals import global_plugin_list

from BuddyList import BuddyList
from BuddyListMap import BuddyList as BuddyListMap
from BuddyListHuman import BuddyListHuman
from InfoList import InfoList
from TaskList import TaskList
from MapTaskList import MapTaskList
from MapTradeList import MapTradeList
from MapToolList import MapToolList
from MapVisitList import MapVisitList

from TechList import TechList
from TaskListLabel import TaskListLabel
from TaskListGroup import TaskListGroup
from MemberList import MemberList
from KMList import KMList
from NoteList import NoteList
import http.client
import json
import requests
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QSize, QUrl, QThread
from PyQt6.QtWidgets import QTreeWidgetItem
from globals import global_agent_list
from Agent import Agent, AgentMode
from AddBuddyDialog import AddBuddyDialog
# from AddGroupDialog import AddGroupDialog
from noteeditor.msword import Main as NoteEditor
from function_manager import FunctionManager
from mcp_manager import McpManager
from skill_manager import SkillManager
from util import open_file
import util
from keyvalue_mng import KeyValueManager
from MessageBoxEarth import MessageBox as MapMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import platform
from PyQt6.QtWidgets import QToolButton, QApplication
from PyQt6.QtGui import QIcon, QCursor
from PyQt6.QtCore import QSize, Qt
import sys
import platform  # 用于检测操作系统
from .ui_ChartCanvas import RadarChartCanvas,BarChartCanvas
import webbrowser
from i18n import lt

# 根据操作系统选择合适的字体
if platform.system() == 'Darwin':  # macOS
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # macOS 上的中文字体
else:
    plt.rcParams['font.sans-serif'] = ['SimHei']  # Windows 上的黑体

plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题



class WorkerThread(QThread):
    finished = pyqtSignal()

    def __init__(self, filepath, persist_directory, embedding_model_name, emb_type, chunk_size, chunk_overlap,vector_type,config):
        super(WorkerThread, self).__init__()
        self.filepath = filepath
        self.persist_directory = persist_directory
        self.embedding_model_name = embedding_model_name
        self.emb_type = emb_type
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.vector_type=vector_type
        self.config = config

    def run(self):
        filepath = self.filepath
        persist_directory = self.persist_directory
        embedding_model_name = self.embedding_model_name
        emb_type = self.emb_type
        chunk_size = self.chunk_size
        chunk_overlap = self.chunk_overlap
        print("开始向量化....")
        if self.vector_type == "Pinecone":
            savevector_pinecone(filepath, persist_directory, self.config, chunk_size, chunk_overlap)
        else:
            savevector(filepath, persist_directory, embedding_model_name, emb_type, chunk_size, chunk_overlap)
        self.finished.emit()  # 发射信号，通知主线程


class Ui_MainWindow(object):
    CurTabTextChatTech = ""  # agent 对话列表
    CurTabTextChatMem = ""  # agent  成员列表
    CurTabTextAI = ""  # AI社交
    CurTabTextNote = ""  # 我的笔记
    CurTabTextKmlist = ""  # 知识列表

    def setupUi(self, MainWindow):
        MainWindow.setWindowTitle("AI-SNS")
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(QtCore.QSize(QtCore.QRect(0, 0, 316, 407).size()).expandedTo(MainWindow.minimumSizeHint()))
        MainWindow.setWindowIcon(QtGui.QIcon("images/aisns.png"))
        # MainWindow.setUnifiedTitleAndToolBarOnMac(False)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.mainwindow_vlayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.main_hlayout = QtWidgets.QHBoxLayout()
        self.mainwindow_vlayout.addLayout(self.main_hlayout)
        self.main_statusbar = QStatusBar()
        self.main_statusbar.setVisible(False)
        self.mainwindow_vlayout.addWidget(self.main_statusbar)

        self.stack_main_widget = QtWidgets.QStackedWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                                           QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stack_main_widget.sizePolicy().hasHeightForWidth())
        self.stack_main_widget.setSizePolicy(sizePolicy)
        self.stack_main_widget.setAutoFillBackground(False)
        self.stack_main_widget.setObjectName("stack_main_widget")

        self.create_toolbar_actions()
        self.createToolbars()

        self.createToolBox_AgentChat()
        self.createToolBox_AiChat()
        self.createToolBox_KM()
        # self.createToolBox_WorkFlow()
        self.createToolBox_Plugin()

        self.createToolBox_Web()
        self.createToolBox_Home()

        self.stack_toolbox = QtWidgets.QStackedWidget()
        # self.stack_toolbox.setFixedWidth(300)
        # self.stack_toolbox.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Expanding)
        self.stack_toolbox.addWidget(self.toolBox_AiChat)  # 前面create出来的
        self.stack_toolbox.addWidget(self.toolBox_AgentChat)  # 前面create出来的
        self.stack_toolbox.addWidget(self.toolBox_KM)  # 前面create出来的
        # self.stack_toolbox.addWidget(self.toolBox_Workflow)  # 前面create出来的
        self.stack_toolbox.addWidget(self.toolBox_Plugin)  # 前面create出来的
        self.stack_toolbox.addWidget(self.toolBox_Web)  # 前面create出来的
        self.stack_toolbox.addWidget(self.toolBox_Home)  # 前面create出来的

        self.stack_toolbox.setCurrentIndex(0)

        self.main_hlayout.addWidget(self.stack_toolbox)

        self.toggle_button = QtWidgets.QPushButton("◀",self)
        self.toggle_button.setFixedWidth(20)
        self.toggle_button.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Expanding)
        self.toggle_button.clicked.connect(self.toggle_stack_toolbox)
        self.toggle_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_button.setStyleSheet("""
                    QPushButton {
                        color: #146ebe;
                        font-size:16pt;
                        border: 1px solid #c0c0c0;
                        border-top: 0px solid #c0c0c0;
                        border-left: 0px solid #c0c0c0;
                        border-right: 0px solid #c0c0c0;
                        border-bottom: 0px solid #c0c0c0;
                    }
                """)



        self.vlayout_toggle_button = QtWidgets.QVBoxLayout()
        self.vlayout_toggle_button.setContentsMargins(0, 0, 0, 0)
        self.vlayout_toggle_button.setSpacing(0)
        self.vlayout_toggle_button.addWidget(self.toggle_button)

        self.toggle_button_shortcut = QtGui.QShortcut(
            QtGui.QKeySequence(QtCore.Qt.KeyboardModifier.ControlModifier | QtCore.Qt.Key.Key_M),
            self
        )
        self.toggle_button_shortcut.activated.connect(self.toggle_stack_toolbox)
        # 设置快捷键上下文，确保在任何情况下都能响应。使用QShortcut而不是按钮的setShortcut，这样快捷键与按钮的可见性、可用性无关，而是与窗口关联。设置上下文为 ApplicationShortcut 确保全局可用
        self.toggle_button_shortcut.setContext(QtCore.Qt.ShortcutContext.ApplicationShortcut)

        # self.toggle_button.setShortcut(QtGui.QKeySequence(Qt.KeyboardModifier.ControlModifier | Qt.Key.Key_M))

        self.main_hlayout.setContentsMargins(0, 0, 0, 0)
        self.main_hlayout.setSpacing(0)
        self.main_hlayout.addLayout(self.vlayout_toggle_button)

        self.stack_toolbox_visible = True

        self.app_home = QWebEngineView()
        self.html_with_style = '''

        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AI-SNS</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f0f0f0;
                }
                h1, h2 {
                    color: #146EBE;
                }
                div {
                    margin-bottom: 20px;
                }
                img {
                    max-width: 100%;
                    height: auto;
                }
            </style>
        </head>
        <body>

            <!-- Logo section -->
            <div>
                <img alt="The AI-SNS Logo" src="http://localhost:8900/aisnshome.svg" />
            </div>


            <!-- Description section -->
            <div>
                <h2>We Are: AI Agent Social Network, Empowering the Future Metaverse! 🎉</h2>
                <p>
                    AI-SNS is built on a distributed and decentralized network architecture, and here are some key features of AI-SNS:
                </p>
                <ul>
                    <li>This is a social network for AI Agents, enabling communication and collaboration between AI and AI, as well as between AI and humans.</li>
                    <li>It can freely and openly access various large models such as ChatGPT, ChatGLM, Baichuan, etc., to drive and empower AI Agents.</li>
                    <li>This network is built on a decentralized instant messaging network architecture, already possessing a mature ecosystem and great openness.</li>
                    <li>It can use blockchain to confirm the digital identity of AI Agents, empowering the future metaverse.</li>
                </ul>
                <img alt="A screenshot" src="http://localhost:8900/agents.png" />
            </div>

            <!-- Contact section -->
            <div>
                <h2>Contact Us</h2>
                <p>Welcome to visit our website for more information:</p>
                <a href="https://www.ai-sns.org" target="_blank">www.ai-sns.org</a>
            </div>

        </body>
        </html>

                    '''
        self.app_home.setZoomFactor(0.75)
        self.app_home.setHtml(self.html_with_style)
        self.app_home_frame = QtWidgets.QFrame(self)
        self.app_home_frame.setContentsMargins(0, 0, 0, 0)
        self.app_home_frame.setStyleSheet(
            "QFrame { border: 1px solid #c0c0c0;margin:0,0,0,0;padding:0,0,0,0;border-radius: 8px;}")
        app_home_frame_layout = QtWidgets.QVBoxLayout(self.app_home_frame)
        app_home_frame_layout.addWidget(self.app_home)

        self.stack_main_widget.addWidget(self.app_home_frame)


        # self.stack_main_widget.setCurrentWidget(self.app_home_frame)
        self.stack_main_widget.setCurrentWidget(self.map_window_widget)
        self.main_hlayout.addWidget(self.stack_main_widget)  # hlayout在ui_mainwindow.py中定义了
        self.cjr = "cjrok"



        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def toggle_stack_toolbox(self):

        if self.stack_toolbox_visible:
            self.stack_toolbox.hide()
            self.toggle_button.setText("▶")
        else:
            self.stack_toolbox.show()
            self.toggle_button.setText("◀")
        self.stack_toolbox_visible = not self.stack_toolbox_visible

    def buttonGroupClicked_plugin_function(self, clicked_button):
        buttons = self.buttonGroup_Plugin_function.buttons()
        for button in buttons:
            if button != clicked_button:
                button.setChecked(False)

    def buttonGroupClicked_plugin_mcp(self, clicked_button):
        buttons = self.buttonGroup_Plugin_mcp.buttons()
        for button in buttons:
            if button != clicked_button:
                button.setChecked(False)

    def buttonGroupClicked_plugin_skill(self, clicked_button):
        buttons = self.buttonGroup_Plugin_skill.buttons()
        for button in buttons:
            if button != clicked_button:
                button.setChecked(False)

    def buttonGroupClicked_plugin_cfg(self, id):
        buttons = self.buttonGroup_Plugin.buttons()
        for button in buttons:
            if self.buttonGroup_Plugin.button(id) != button:
                button.setChecked(False)

    def buttonGroupClicked_workflow(self, clicked_button):
        buttons = self.buttonGroup_WorkFlow.buttons()
        for button in buttons:
            if button != clicked_button:
                button.setChecked(False)

    def buttonGroupClicked_plugin_install(self, clicked_button):
        buttons = self.buttonGroup_Plugin_install.buttons()
        for button in buttons:
            if button != clicked_button:
                button.setChecked(False)

    def download_file(self, url, file_path):
        # 发送 GET 请求并获取响应对象
        response = requests.get(url)

        # 检查响应状态码是否为成功
        if response.status_code == 200:
            # 打开文件并写入响应内容
            with open(file_path, 'wb') as file:
                file.write(response.content)
            print(f"文件 '{file_path}' 下载成功！")
        else:
            print(f"下载失败，状态码：{response.status_code}")

    def unzip_file(self, zip_file_path, extract_to_path):
        # 创建一个ZipFile对象，并打开要解压的zip文件
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            # 解压缩到指定位置
            zip_ref.extractall(extract_to_path)

        print("解压缩完成！")

    # Agent tool box

    def createToolBoxUnit_AgentChat(self, agent, pos=-1):
        agent_cfg = agent.agent_cfg
        if agent_cfg.is_show == False:
            return
        # Create layout and buttons
        layout = QGridLayout()
        layout.addWidget(self.create_new_task_button(lt("New Chat", "新建对话"), agent, 0), 0, 0)
        layout.addWidget(self.create_agent_cfg_button(lt("Setting", "更多设置"), agent, 0), 0, 1)

        # Create search input
        textEdit = QLineEdit()
        textEdit.setPlaceholderText(lt("🔍Keyword+Enter,Blank+Enter to reset", "🔍关键词+回车搜索，空+回车复原"))
        palette = textEdit.palette()
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("gray"))  # 可以改为其他颜色
        textEdit.setPalette(palette)
        textEdit.setToolTip("关键字以+++开头表示在搜索结果中继续搜索")
        layout.addWidget(textEdit, 1, 0, 1, 2)

        # Create task and tech lists and add them to tab widget
        tabWidget = QTabWidget()
        layout.addWidget(tabWidget, 2, 0, 3, 2)
        taskList = TaskList(self, agent)
        # techList = TechList(self, agent)
        labelList = TaskListLabel(self, agent)
        # self.taskList_Task = taskList
        # self.techList_Tech = techList
        # self.labelList_label = labelList

        self.tasklist_list[agent_cfg.user_id] = taskList
        # self.techlist_list[agent_cfg.user_id] = techList
        self.labellist_list[agent_cfg.user_id] = labelList
        tabWidget.addTab(taskList, lt("Chat List", "对话列表"))
        # tabWidget.addTab(techList, "技能列表")
        tabWidget.addTab(labelList, lt("Tag List", "标签列表"))  # -->
        self.CurTabTextChatTech = lt("Chat List", "对话列表")
        # 直接在 connect 方法中使用 lambda 函数处理标签页切换
        tabWidget.currentChanged.connect(
            lambda index: setattr(self, 'CurTabTextChatTech', tabWidget.tabText(index))
        )
        # Stretch settings
        # layout.setRowStretch(3, 10)
        # layout.setColumnStretch(2, 10)
        # 设置行的拉伸系数
        layout.setRowStretch(3, 10)  # 第3行的拉伸系数
        layout.setColumnStretch(0, 1)  # 设置第0列的拉伸系数以均衡布局
        layout.setColumnStretch(1, 1)  # 设置第1列的拉伸系数以均衡布局

        # Create and set widget
        itemWidget = QWidget()
        itemWidget.setObjectName(agent_cfg.user_id)
        itemWidget.item_id = agent_cfg.user_id
        itemWidget.item_type = "agent"
        itemWidget.setLayout(layout)
        self.toolBox_AgentChat.setMinimumWidth(itemWidget.sizeHint().width())
        if pos == -1:
            self.toolBox_AgentChat.addItem(itemWidget, QIcon('images/agentsingle.png'),
                                           f"{agent_cfg.name} ({agent_cfg.memo})" if agent_cfg.memo else agent_cfg.name)
        else:
            self.toolBox_AgentChat.insertItem(pos - 1, itemWidget, QIcon('images/agentsingle.png'),
                                              f"{agent_cfg.name} ({agent_cfg.memo})" if agent_cfg.memo else agent_cfg.name)

        # Connect returnPressed signal to search function
        # textEdit.returnPressed.connect(lambda: self.taskList_Task.search(textEdit.text()))
        textEdit.returnPressed.connect(lambda: taskList_on_return_pressed(textEdit.text()))

        # -->内部函数
        def taskList_on_return_pressed(key_word):
            if self.CurTabTextChatTech == lt("Chat List", "对话列表"):  # 这里是你的判断条件
                print("对话列表")
                taskList.search(key_word)
            elif self.CurTabTextChatTech == lt("Tag List", "标签列表"):
                print("标签列表")
                labelList.search(key_word)
            elif self.CurTabTextChatTech == lt("Tech List", "技能列表"):
                # todo
                print("技能列表")
                # techList.search(key_word)
            else:
                print("其他")

    def createToolBoxUnit_MutiAgentChat(self, agent_cfg_multi, pos=-1):
        if agent_cfg_multi.is_show == False:
            return
        # two button 两个按钮
        layout = QGridLayout()

        layout.addWidget(self.create_new_group_task_button(lt("New Chat", "新建对话"), agent_cfg_multi, 0),
                         0, 0)
        layout.addWidget(self.create_muti_agent_cfg_button(lt("Setting", "更多设置"), agent_cfg_multi, 0), 0,
                         1)

        # search input 搜索框
        textEdit = QLineEdit()
        textEdit.setPlaceholderText(lt("🔍Keyword+Enter,Blank+Enter to reset", "🔍关键词+回车搜索，空+回车复原"))
        palette = textEdit.palette()
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("gray"))  # 可以改为其他颜色
        textEdit.setPalette(palette)
        textEdit.setToolTip("关键字以+++开头表示在搜索结果中继续搜索")
        layout.addWidget(textEdit, 1, 0, 1, 2)

        # task tab 任务页签
        tabWidget = QTabWidget()
        layout.addWidget(tabWidget, 2, 0, 3, 2)  # rowspan为3，此时tab在垂直方向上铺满
        task_list_group = TaskListGroup(self, agent_cfg_multi)
        member_list = MemberList(self, agent_cfg_multi)
        task_list_group_label = TaskListGroupLabel(self, agent_cfg_multi)
        self.tasklist_group_list[agent_cfg_multi.group_id] = task_list_group
        self.memberlist_group_list[agent_cfg_multi.group_id] = member_list

        self.task_list_group = task_list_group
        self.member_list = member_list

        tabWidget.addTab(task_list_group, lt("Chat List", "对话列表"))
        tabWidget.addTab(member_list, lt("Member List", "成员列表"))
        tabWidget.addTab(task_list_group_label, lt("Tag List", "标签列表"))
        self.CurTabTextChatMem = lt("Chat List", "对话列表")
        # 直接在 connect 方法中使用 lambda 函数处理标签页切换
        tabWidget.currentChanged.connect(
            lambda index: setattr(self, 'CurTabTextChatMem', tabWidget.tabText(index))
        )
        layout.setRowStretch(3, 10)
        layout.setColumnStretch(0, 1)  # 设置第0列的拉伸系数以均衡布局
        layout.setColumnStretch(1, 1)  # 设置第1列的拉伸系数以均衡布局
        itemWidget = QWidget()
        itemWidget.setLayout(layout)
        itemWidget.setObjectName(agent_cfg_multi.group_id)
        itemWidget.item_id = agent_cfg_multi.group_id
        itemWidget.item_type = "agent_group"
        self.toolBox_AgentChat.setMinimumWidth(itemWidget.sizeHint().width())

        if pos == -1:
            self.toolBox_AgentChat.addItem(itemWidget, QIcon('images/agentmulti.png'),
                                           f"{agent_cfg_multi.name} ({agent_cfg_multi.memo})" if agent_cfg_multi.memo else agent_cfg_multi.name)
        else:
            self.toolBox_AgentChat.insertItem(pos - 1, itemWidget, QIcon('images/agentmulti.png'),
                                              f"{agent_cfg_multi.name} ({agent_cfg_multi.memo})" if agent_cfg_multi.memo else agent_cfg_multi.name)
        # textEdit.returnPressed.connect(lambda: task_list_group.search(textEdit.text()))
        textEdit.returnPressed.connect(lambda: task_list_group_on_return_pressed(textEdit.text()))

        # --> 内部调用
        def task_list_group_on_return_pressed(key_word):
            if self.CurTabTextChatMem == lt("Chat List", "对话列表"):  # 这里是你的判断条件
                task_list_group.search(key_word)
            elif self.CurTabTextChatMem == lt("Tag List", "标签列表"):
                task_list_group_label.search(key_word)
            elif self.CurTabTextChatMem == lt("Member List", "成员列表"):
                print("成员列表---未实现")
                member_list.search(key_word)
            else:
                print("其他列表")

    def createToolBox_AgentChat(self):
        self.toolBox_AgentChat = QToolBox()
        self.toolBox_AgentChat.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Ignored))

        # self.buttonGroup = QButtonGroup()
        # self.buttonGroup.setExclusive(False)
        # self.buttonGroup.buttonClicked[int].connect(self.buttonGroupClicked)

        agents = global_agent_list.values()  # 前面已经从数据库中初始化了agent列表，直接使用前面已经初始化的列表获取其agent_cfg即可
        for agent in agents:
            self.createToolBoxUnit_AgentChat(agent)

        # agent_cfgs_multi = query_MutiAgentCfg_All()
        # for agent_cfg_multi in agent_cfgs_multi:
        #     self.createToolBoxUnit_MutiAgentChat(agent_cfg_multi)

        settingLayout = QGridLayout()
        settingLayout.addWidget(self.createCellWidgetAgentNew("新增Agent",
                                                              'images/userplus.png'), 0, 0)
        settingLayout.addWidget(self.createCellWidgetAgentMng("管理Agent",
                                                              'images/usermng.png'), 0, 1)

        settingLayout.addWidget(self.createCellWidgetAgentMultiPrompt("提示词管理",
                                                                      'images/fileline.png'), 1, 0)

        # settingLayout.addWidget(self.createCellWidgetAgentMultiNew("新增Agent群",
        #                                                            'images/agentmultiadd.png'), 1, 0)
        # settingLayout.addWidget(self.createCellWidgetAgentMultiMng("管理Agent群",
        #                                                            'images/agentmultimng.png'), 1, 1)
        #
        # settingLayout.addWidget(self.createCellWidgetAgentMultiEval("模型评测",
        #                                                             'images/billboard.png'), 2, 0)

        # settingLayout.addWidget(self.createCellWidgetAgentMultiPrompt("提示词管理",
        #                                                               'images/fileline.png'), 2, 1)

        settingLayout.setRowStretch(3, 10)
        settingLayout.setColumnStretch(0, 1)  # 设置第0列的拉伸系数以均衡布局
        settingLayout.setColumnStretch(1, 1)  # 设置第1列的拉伸系数以均衡布局

        settingWidget = QWidget()
        settingWidget.setObjectName("agent_setting")
        settingWidget.item_id = "agent_setting_01"
        settingWidget.item_type = "agent_setting"
        settingWidget.setLayout(settingLayout)

        self.toolBox_AgentChat.addItem(settingWidget, lt("Agent Management", "AI智能体管理"))
        # 动态修改其值
        self.toolBox_AgentChat.setItemText(self.toolBox_AgentChat.indexOf(settingWidget), lt("Agent Management", "AI智能体管理"))
        self.toolBox_AgentChat.setItemIcon(self.toolBox_AgentChat.indexOf(settingWidget), QIcon('images/setting.png'))

        self.toolBox_AgentChat.currentChanged.connect(self.on_agentchat_toolbox_item_changed)

        self.toolBox_AgentChat.setStyleSheet("""
        QToolBox {
            background: #f0f0f0;  /* 整体背景颜色 */
            border-radius: 8px;
            padding: 5px;
        }
        QToolBox::tab {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #ffffff, stop:1 #e0e0e0);  /* 渐变背景 */
            
            border-radius: 6px;
            color: #333;  /* 文本颜色 */
            /*padding: 10px 15px;*/
            padding-bottom:0px;
            margin: 0px;
            font-size: 14px;
            transition: background 0.3s;  /* 背景过渡效果 */
            height: 100px;  /* 确保标签有足够的高度 */
        }
        QToolBox::tab:selected {
        
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #e0e0e0, stop:1 #f0f0f0); 
            /*background: qlineargradient(x1:0, y1:0, x2:1, y2:0,stop:0 #4facfe, stop:1 #00f2fe); */ /* 选中的标签渐变色 */
            /*color: #ffffff;*/  /* 选中状态下的文本颜色 */
            font-weight: bold;
            box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.2);
        }
        QToolBox::tab:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                    stop:0 #e0e0e0, stop:1 #f0f0f0); 
        }
        QToolBox::tab QLabel {
            color: #333; /* 确保标签内的文本颜色 */
        }

        QToolBox > QWidget {  /* 仅设置QToolBox子项的背景 */
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #e0e0e0, stop:1 #e0e0e0);
            border-radius: 6px;
            padding: 10px;
        }

            """)

    def get_toolbox_agentchat_current_item(self):
        current_index = self.toolBox_AgentChat.currentIndex()  # 获取当前选中项的索引
        item_widget = self.toolBox_AgentChat.widget(current_index)  # 获取对应的 QWidget
        return item_widget

    def get_toolbox_agentchat_current_item_id(self):
        item_widget = self.get_toolbox_agentchat_current_item()
        item_id = item_widget.item_id
        return item_id

    def get_toolbox_agentchat_current_item_type(self):
        item_widget = self.get_toolbox_agentchat_current_item()
        item_type = item_widget.item_type
        return item_type

    def on_agentchat_toolbox_item_changed(self, index):
        self.show_agent_current_main_widget()

    def createToolBoxUnit_AiChat(self, agent, pos=-1):
        # two button 两个按钮
        print("createToolBoxUnit_AiChat-->")
        layout = QGridLayout()

        layout = QGridLayout()
        layout.addWidget(self.create_new_contact_group_button(lt("Contact/Group", "添加联系人/组"), agent, 0),
                         0, 0)
        layout.addWidget(self.create_ai_cfg_button(lt("Login setting", "登录设置"), agent, 0), 0,
                         1)

        # search input 搜索框
        textEdit = QLineEdit()
        textEdit.setPlaceholderText(lt("Search...", "搜索..."))
        palette = textEdit.palette()
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("gray"))  # 可以改为其他颜色
        textEdit.setPalette(palette)
        # textEdit.setToolTip("关键字以+++开头表示在搜索结果中继续搜索")
        layout.addWidget(textEdit, 1, 0, 1, 2)

        # task tab 任务页签
        tabWidget = QTabWidget()
        layout.addWidget(tabWidget, 2, 0, 3, 2)  # rowspan为3，此时tab在垂直方向上铺满
        buddyList = BuddyList(self, agent)
        infoList = InfoList(self, agent)
        self.buddylist_list[agent.user_id] = buddyList
        self.current_buddylist = buddyList
        self.contactlist_list[agent.user_id] = infoList

        tabWidget.addTab(buddyList, lt("Chat", "聊天"))
        tabWidget.addTab(infoList, lt("Info", "通知"))
        self.CurTabTextAI = lt("Chat", "聊天")

        # 直接在 connect 方法中使用 lambda 函数处理标签页切换
        tabWidget.currentChanged.connect(
            lambda index: setattr(self, 'CurTabTextAI', tabWidget.tabText(index))
        )

        layout.setRowStretch(3, 10)
        layout.setColumnStretch(0, 1)  # 设置第0列的拉伸系数以均衡布局
        layout.setColumnStretch(1, 1)  # 设置第1列的拉伸系数以均衡布局
        itemWidget = QWidget()
        itemWidget.setLayout(layout)
        itemWidget.setObjectName(agent.user_id)
        itemWidget.item_id = agent.user_id
        itemWidget.item_type = "ai_chat"
        self.toolBox_AiChat.setMinimumWidth(itemWidget.sizeHint().width())

        if pos == -1:
            self.toolBox_AiChat.addItem(itemWidget, QIcon('images/messageoffline.png'), agent.nickname)
        else:
            self.toolBox_AiChat.insertItem(self.toolBox_AiChat.count() - 1, itemWidget,
                                           QIcon('images/messageoffline.png'), agent.nickname)
        # textEdit.returnPressed.connect(lambda: buddyList.search(textEdit.text()))
        textEdit.returnPressed.connect(lambda: self.filterItemsBuddyList(textEdit.text()))

    def createToolBoxUnit_AiChat_earth(self, aichat_cfg, pos=-1):
        # two button 两个按钮
        print("createToolBoxUnit_AiChat-->")
        # 定义示例数据和类别
        radar_data = [1, 1, 1, 1, 1]

        radar_categories = [f'{lt("IQ", "智力")}:100', f'{lt("Energy", "体力")}:100', f'{lt("Life", "生命")}:100', f'{lt("Move", "行动")}:100', f'{lt("Exp", "经验")}:100']


        # 定义柱状图数据
        bar_indicators = [f'{lt("Money", "资金")}:1,000', f'{lt("Credit", "信用")}:100', f'{lt("Level", "等级")}1']  # 使用中文标签
        bar_values = [1, 1, 1]
        bar_colors = ['#ffb676', '#c3f1d7', '#99d4ff']  # 使用协调的颜色

        # 创建雷达图和柱状图的画布
        self.radar_chart = RadarChartCanvas(radar_data, radar_categories)
        self.bar_chart = BarChartCanvas(bar_indicators, bar_values, bar_colors)

        layout = QGridLayout()
        layout.addWidget(self.bar_chart,
                         0, 0)
        layout.addWidget(self.radar_chart, 0,
                         1)

        config_button = self.create_ai_cfg_button_earth(lt("Setting", "设置"), aichat_cfg, 0)

        mission_button = self.create_ai_task_button_earth(lt("New Task", "指派任务"), aichat_cfg, 0)

        # layout.addWidget(mission_button,
        #                  1, 0)
        # layout.addWidget(config_button, 1,
        #                  1)



        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Policy.Expanding,
                                                      QtWidgets.QSizePolicy.Policy.Minimum)
        layout.addItem(spacerItem)  # 通过留空来居中


        # search input 搜索框
        textEdit = QLineEdit()
        textEdit.setPlaceholderText(lt("Search...", "搜索..."))
        palette = textEdit.palette()
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("gray"))  # 可以改为其他颜色
        textEdit.setPalette(palette)
        textEdit.setVisible(False)
        # textEdit.setToolTip("关键字以+++开头表示在搜索结果中继续搜索")
        # layout.addWidget(textEdit, 2, 0, 1, 2)

        # 页签
        tabWidget = QTabWidget()
        layout.addWidget(tabWidget, 3, 0, 3, 2)  # rowspan为3，此时tab在垂直方向上铺满
        buddyList = BuddyListMap(self, aichat_cfg, "1")
        self.map_buddy_list = buddyList
        # maptasklist = MapTaskList(self, aichat_cfg)
        # visitList = MapVisitList(self, aichat_cfg)
        # toolList = MapToolList(self, aichat_cfg)
        tradeList = MapTradeList(self, aichat_cfg)
        infoList = InfoList(self, aichat_cfg)
        self.buddylist_list[aichat_cfg.user_id] = buddyList
        self.contactlist_list[aichat_cfg.user_id] = infoList
        # self.maptasklist = maptasklist
        infoList.setVisible(False)

        tabWidget.addTab(buddyList, lt("Chat", "聊天"))
        # tabWidget.addTab(maptasklist, lt("Task", "任务"))
        # tabWidget.addTab(visitList, lt("Visit", "打卡"))
        # tabWidget.addTab(toolList, lt("Tech", "技能"))
        tabWidget.addTab(tradeList, lt("Trade", "交易"))
        # tabWidget.addTab(infoList, lt("Info", "通知"))

        tabWidget.setCurrentIndex(0)
        self.CurTabTextAI = lt("Chat", "聊天")

        # 直接在 connect 方法中使用 lambda 函数处理标签页切换
        tabWidget.currentChanged.connect(
            lambda index: setattr(self, 'CurTabTextAI', tabWidget.tabText(index))
        )

        layout.setRowStretch(4, 10)
        layout.setColumnStretch(0, 1)  # 设置第0列的拉伸系数以均衡布局
        layout.setColumnStretch(1, 1)  # 设置第1列的拉伸系数以均衡布局
        itemWidget = QWidget()
        itemWidget.setLayout(layout)
        itemWidget.setObjectName(aichat_cfg.user_id)
        itemWidget.item_id = aichat_cfg.user_id
        itemWidget.item_type = "ai_map"
        self.toolBox_AiChat.setMinimumWidth(itemWidget.sizeHint().width())

        if pos == -1:
            self.toolBox_AiChat.addItem(itemWidget, QIcon('images/earth.png'), lt("Explore the Earth", "漫游地球", "漫游地球") + "-" + aichat_cfg.nickname)
        else:
            self.toolBox_AiChat.insertItem(self.toolBox_AiChat.count() - 1, itemWidget,
                                           QIcon('images/earth.png'), lt("Explore the Earth", "漫游地球", "漫游地球") + "-" + aichat_cfg.nickname)
        # textEdit.returnPressed.connect(lambda: buddyList.search(textEdit.text()))
        textEdit.returnPressed.connect(lambda: self.filterItemsBuddyList(textEdit.text()))
        self.map_window_widget = QWidget()
        # aicfg_record = query_AiChatCfg(is_delete=0)
        # self.map_message_box = MessageBox(self, None, aicfg_record)
        self.map_message_box = MapMessageBox(self, None, aichat_cfg)
        vlayout = QVBoxLayout(self.map_window_widget)
        vlayout.addWidget(self.map_message_box)
        self.stack_main_widget.addWidget(self.map_window_widget)
        # 自动登录
        self.on_configured_ai_map(aichat_cfg.user_id, aichat_cfg.account, aichat_cfg.password, "1")

    def filterItemsBuddyList(self, text):
        """根据用户输入的关键词过滤树节点"""
        # 过滤树形控件中的项目 topLevelItemCount
        if hasattr(self, 'BuddyList') or hasattr(self, 'InfoList'):
            if self.CurTabTextAI == "聊天":
                search_list = self.BuddyList
            else:
                search_list = self.InfoList
            print("tree--:", search_list.tree)
            for i in range(search_list.topLevelItemCount()):
                top_item = search_list.topLevelItem(i)
                self.filter_children(top_item, text)
                # print("tree--:",self.BuddyList.tree)
                # for i in range(self.BuddyList.topLevelItemCount()):
                #     top_item = self.BuddyList.topLevelItem(i)
                #     self.filter_children(top_item, text)

    def filter_children(self, parent, text):
        for i in range(parent.childCount()):
            child = parent.child(i)
            if text.lower() in child.text(0).lower():
                child.setHidden(False)
            else:
                child.setHidden(True)
            if child.childCount() > 0:
                self.filter_children(child, text)

    def createToolBox_AiChat(self):
        self.toolBox_AiChat = QToolBox()
        self.toolBox_AiChat.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Ignored))

        self.buttonGroup_AiChat = QButtonGroup()
        self.buttonGroup_AiChat.setExclusive(False)
        # self.buttonGroup_AiChat.buttonClicked[int].connect(self.buttonGroupClicked)

        map_record = query_AiChatCfg_map()

        self.createToolBoxUnit_AiChat_earth(map_record)

        common_record = query_AiChatCfg_common()

        self.createToolBoxUnit_AiChat(common_record)

        # settingLayout = QGridLayout()
        # settingLayout.addWidget(self.createCellWidgetAiChatNew("添加社交帐号",
        #                                                        'images/userplus.png'), 0, 0)
        # settingLayout.addWidget(self.createCellWidgetAiChatMng("管理社交帐号",
        #                                                        'images/usermng.png'), 0, 1)
        #
        # settingLayout.setRowStretch(2, 10)
        # settingLayout.setColumnStretch(0, 1)  # 设置第0列的拉伸系数以均衡布局
        # settingLayout.setColumnStretch(1, 1)  # 设置第1列的拉伸系数以均衡布局
        #
        # itemWidget = QWidget()
        # itemWidget.item_id = "ai_chat_setting_001"
        # itemWidget.item_type = "ai_chat_setting"
        # itemWidget.setLayout(settingLayout)
        #
        # self.toolBox_AiChat.addItem(itemWidget, QIcon('images/setting.png'), lt("Account setting", "帐号管理"))

        self.toolBox_AiChat.currentChanged.connect(self.on_aichat_toolbox_item_changed)
        self.toolBox_AiChat.setStyleSheet("""
        QToolBox {
            background: #f0f0f0;  /* 整体背景颜色 */
            border-radius: 8px;
            padding: 5px;
        }
        QToolBox::tab {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #ffffff, stop:1 #e0e0e0);  /* 渐变背景 */

            border-radius: 6px;
            color: #333;  /* 文本颜色 */
            /*padding: 10px 15px;*/
            padding-bottom:0px;
            margin: 0px;
            font-size: 14px;
            transition: background 0.3s;  /* 背景过渡效果 */
            height: 100px;  /* 确保标签有足够的高度 */
        }
        QToolBox::tab:selected {

            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #e0e0e0, stop:1 #f0f0f0); 
            /*background: qlineargradient(x1:0, y1:0, x2:1, y2:0,stop:0 #4facfe, stop:1 #00f2fe); */ /* 选中的标签渐变色 */
            /*color: #ffffff;*/  /* 选中状态下的文本颜色 */
            font-weight: bold;
            box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.2);
        }
        QToolBox::tab:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                    stop:0 #e0e0e0, stop:1 #f0f0f0); 
        }
        QToolBox::tab QLabel {
            color: #333; /* 确保标签内的文本颜色 */
        }

        QToolBox > QWidget {  /* 仅设置QToolBox子项的背景 */
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #e0e0e0, stop:1 #e0e0e0);
            border-radius: 6px;
            padding: 10px;
        }

            """)

    def get_toolbox_aichat_current_item(self):
        current_index = self.toolBox_AiChat.currentIndex()  # 获取当前选中项的索引
        item_widget = self.toolBox_AiChat.widget(current_index)  # 获取对应的 QWidget
        return item_widget

    def get_toolbox_aichat_current_item_id(self):
        item_widget = self.get_toolbox_aichat_current_item()
        item_id = item_widget.item_id
        return item_id

    def get_toolbox_aichat_current_item_type(self):
        item_widget = self.get_toolbox_aichat_current_item()
        item_type = item_widget.item_type
        return item_type

    def on_aichat_toolbox_item_changed(self, index):
        self.show_ai_current_main_widget()

    def km_item_click(self, item, col, kmrecord):
        print("in clickitem")
        print(item.type())
        print(QTreeWidgetItem.ItemType.UserType + 1)
        # if item and item.type() == QTreeWidgetItem.ItemType.UserType + 1:
        id_value = item.data(col, Qt.ItemDataRole.UserRole)
        if id_value == None:
            return (False)
        name = item.text(col)
        km_path = kmrecord.kmpath
        file_path = os.path.join(os.getcwd(), "km", km_path, "doc", name)
        open_file(file_path)

        # item.on_click()

    def createToolBoxUnit_KM_Notes(self, kmrecord, pos=-1):
        # Create layout and buttons
        layout = QGridLayout()
        layout.addWidget(self.create_new_note_button(lt("New Note", "新建笔记"), kmrecord, "images/fileplus.png"),
                         0, 0)
        layout.addWidget(self.create_note_cfg_button(lt("Setting", "更多设置"), 0), 0,
                         1)
        # Create search input
        textEdit = QLineEdit()
        textEdit.setPlaceholderText(lt("🔍Keyword+Enter,Blank+Enter to reset", "🔍关键词+回车搜索，空+回车复原"))
        palette = textEdit.palette()
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("gray"))  # 可以改为其他颜色
        textEdit.setPalette(palette)
        textEdit.setToolTip("关键字以+++开头表示在搜索结果中继续搜索")
        layout.addWidget(textEdit, 1, 0, 1, 2)

        # Create task and tech lists and add them to tab widget
        tabWidget = QTabWidget()
        layout.addWidget(tabWidget, 2, 0, 3, 2)
        # notelist_recent = NoteList(self, kmrecord, "recent")
        # notelist_recent.setObjectName("recentnotelist")
        notelist_all = NoteList(self, kmrecord, "all")
        notelist_all.setObjectName("allnotelist")
        notelist_all_label = NoteListLabel(self, kmrecord, "label")
        notelist_all_label.setObjectName("labelallnotelist")
        # self.notelist_recent = notelist_recent
        self.notelist_all = notelist_all
        self.notelist_all_label = notelist_all_label


        self.notelist_all_list[kmrecord.km_id] = notelist_all
        self.notelist_all_list_label[kmrecord.km_id] = notelist_all_label

        # tabWidget.addTab(notelist_recent, "最新")
        tabWidget.addTab(notelist_all, lt("All", "全部"))
        tabWidget.addTab(notelist_all_label, lt("Tag", "标签"))
        # self.CurTabTextNote = "最新"
        self.CurTabTextNote = lt("All", "全部")
        # 直接在 connect 方法中使用 lambda 函数处理标签页切换
        tabWidget.currentChanged.connect(
            lambda index: setattr(self, 'CurTabTextNote', tabWidget.tabText(index))
        )

        # Stretch settings
        layout.setRowStretch(3, 10)
        layout.setColumnStretch(0, 1)  # 设置第0列的拉伸系数以均衡布局
        layout.setColumnStretch(1, 1)  # 设置第1列的拉伸系数以均衡布局
        # layout.setColumnStretch(2, 10)

        # Create and set widget
        itemWidget = QWidget()
        itemWidget.setObjectName(kmrecord.km_id)
        itemWidget.item_id = kmrecord.km_id
        itemWidget.item_type = "note"
        itemWidget.setLayout(layout)
        self.toolBox_KM.setMinimumWidth(itemWidget.sizeHint().width())

        # self.toolBox_KM.addItem(itemWidget, "我的笔记")

        if pos == -1:
            self.toolBox_KM.addItem(itemWidget, QIcon('images/note.png'), kmrecord.name)
        else:
            self.toolBox_KM.insertItem(self.toolBox_KM.count() - 1, itemWidget, QIcon('images/note.png'), kmrecord.name)

        # Connect returnPressed signal to search function
        # textEdit.returnPressed.connect(lambda: notelist_all.search(textEdit.text()))
        textEdit.returnPressed.connect(lambda: self.notelist_on_return_pressed(textEdit.text()))

    def notelist_on_return_pressed(self, key_word):
        if self.CurTabTextNote == lt("All", "全部"):  # 这里是你的判断条件
            self.notelist_all.search(key_word)
        elif self.CurTabTextNote == lt("Tag", "标签"):  # -->  增加 标签 页签
            self.notelist_all_label.search(key_word)
        elif self.CurTabTextNote == "最新":  # 这里是你的判断条件
            self.notelist_recent.search(key_word)
        else:
            print("其他")

    def createToolBoxUnit_KM(self, kmrecord, pos=-1):
        # two button 两个按钮
        layout = QGridLayout()
        layout.addWidget(self.create_new_km_button(lt("Add", "新建知识"), kmrecord, "images/fileplus.png"),
                         0, 0)
        layout.addWidget(self.create_km_cfg_button(lt("Setting", "更多设置"), kmrecord, 0), 0,
                         1)
        # search input 搜索框
        textEdit = QLineEdit()
        textEdit.setPlaceholderText(lt("🔍Keyword+Enter,Blank+Enter to reset", "🔍关键词+回车搜索，空+回车复原"))
        palette = textEdit.palette()
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("gray"))  # 可以改为其他颜色
        textEdit.setPalette(palette)
        textEdit.setToolTip("关键字以+++开头表示在搜索结果中继续搜索")
        textEdit.setPlaceholderText(lt("Search...", "搜索..."))
        palette = textEdit.palette()
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("gray"))  # 可以改为其他颜色
        textEdit.setPalette(palette)
        layout.addWidget(textEdit, 1, 0, 1, 2)
        # task tab 任务页签

        tabWidget = QTabWidget()
        layout.addWidget(tabWidget, 2, 0, 3, 2)  # rowspan为3，此时tab在垂直方向上铺满
        kmlist_list = KMList(self, kmrecord, False)
        kmlist_list_deleted = KMList(self, kmrecord, True)

        kmlist_list.itemDoubleClicked.connect(lambda item, column: self.km_item_click(item, column, kmrecord))
        self.kmlist_all = kmlist_list
        self.kmlist_deleted = kmlist_list_deleted

        self.kmlist_list[kmrecord.km_id] = kmlist_list
        self.kmlist_list_deleted[kmrecord.km_id] = kmlist_list_deleted

        tabWidget.addTab(kmlist_list, lt("File List", "知识列表"))
        tabWidget.addTab(kmlist_list_deleted, lt("Trash", "回收站"))
        self.CurTabTextKmlist = lt("File List", "知识列表")
        # 直接在 connect 方法中使用 lambda 函数处理标签页切换
        tabWidget.currentChanged.connect(
            lambda index: setattr(self, 'CurTabTextKmlist', tabWidget.tabText(index))
        )

        layout.setRowStretch(3, 10)
        layout.setColumnStretch(0, 1)  # 设置第0列的拉伸系数以均衡布局
        layout.setColumnStretch(1, 1)  # 设置第1列的拉伸系数以均衡布局
        # layout.setColumnStretch(2, 10)
        itemWidget = QWidget()
        itemWidget.setObjectName(kmrecord.km_id)
        itemWidget.item_id = kmrecord.km_id
        itemWidget.item_type = "kb"
        itemWidget.setLayout(layout)
        self.toolBox_KM.setMinimumWidth(itemWidget.sizeHint().width())
        if pos == -1:
            self.toolBox_KM.addItem(itemWidget, QIcon('images/filelist.png'), kmrecord.name)
        else:
            self.toolBox_KM.insertItem(self.toolBox_KM.count() - 1, itemWidget, QIcon('images/filelist.png'),
                                       kmrecord.name)
        # Connect returnPressed signal to search function
        textEdit.returnPressed.connect(lambda: kmlist_list.search(textEdit.text()))
        # textEdit.returnPressed.connect(lambda: self.kmlist_on_return_pressed(textEdit.text()))

    def kmlist_on_return_pressed(self, key_word):
        if self.CurTabTextKmlist == lt("KM List", "知识列表"):  # 这里是你的判断条件
            self.kmlist_all.search(key_word)
        else:
            self.kmlist_deleted.search(key_word)

    def createToolBox_KM(self):
        self.toolBox_KM = QToolBox()
        self.toolBox_KM.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Ignored))

        self.buttonGroup_KM = QButtonGroup()
        self.buttonGroup_KM.setExclusive(False)
        # self.buttonGroup_KM.buttonClicked[int].connect(self.buttonGroupClicked)

        records = query_KMCfg_All()
        for record in records:
            # print(f"ID: {record.id}, Name: {record.name}, Memo: {record.memo}")
            if record.kmtype == "1":
                self.createToolBoxUnit_KM_Notes(record)
            else:
                self.createToolBoxUnit_KM(record)

        self.backgroundButtonGroup_KM = QButtonGroup()
        # self.backgroundButtonGroup_KM.buttonClicked.connect(self.backgroundButtonGroupClicked)

        settingLayout = QGridLayout()
        settingLayout.addWidget(self.createCellWidgetKMNew(lt("New KB", "新增知识库"),
                                                           'images/bookplus.png'), 0, 0)
        settingLayout.addWidget(self.createCellWidgetKMMng(lt("KB Management", "管理知识库"),
                                                           'images/filecabinet.png'), 0, 1)

        settingLayout.addWidget(self.createCellWidgetKVMng(lt("Key-Value", "管理键值对"),
                                                           'images/database.png'), 1, 0)

        settingLayout.setRowStretch(2, 10)
        settingLayout.setColumnStretch(0, 1)  # 设置第0列的拉伸系数以均衡布局
        settingLayout.setColumnStretch(1, 1)  # 设置第1列的拉伸系数以均衡布局

        # backgroundLayout.setColumnStretch(2, 10)

        itemWidget = QWidget()
        itemWidget.item_id = "km_setting_001"
        itemWidget.item_type = "km_setting"
        itemWidget.setLayout(settingLayout)

        self.toolBox_KM.addItem(itemWidget, QIcon('images/setting.png'), lt("KM Setting", "知识库设置"))
        self.toolBox_KM.currentChanged.connect(self.on_km_toolbox_item_changed)
        self.toolBox_KM.setStyleSheet("""
        QToolBox {
            background: #f0f0f0;  /* 整体背景颜色 */
            border-radius: 8px;
            padding: 5px;
        }
        QToolBox::tab {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #ffffff, stop:1 #e0e0e0);  /* 渐变背景 */

            border-radius: 6px;
            color: #333;  /* 文本颜色 */
            /*padding: 10px 15px;*/
            padding-bottom:0px;
            margin: 0px;
            font-size: 14px;
            transition: background 0.3s;  /* 背景过渡效果 */
            height: 100px;  /* 确保标签有足够的高度 */
        }
        QToolBox::tab:selected {

            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #e0e0e0, stop:1 #f0f0f0); 
            /*background: qlineargradient(x1:0, y1:0, x2:1, y2:0,stop:0 #4facfe, stop:1 #00f2fe); */ /* 选中的标签渐变色 */
            /*color: #ffffff;*/  /* 选中状态下的文本颜色 */
            font-weight: bold;
            box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.2);
        }
        QToolBox::tab:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                    stop:0 #e0e0e0, stop:1 #f0f0f0); 
        }
        QToolBox::tab QLabel {
            color: #333; /* 确保标签内的文本颜色 */
        }

        QToolBox > QWidget {  /* 仅设置QToolBox子项的背景 */
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #e0e0e0, stop:1 #e0e0e0);
            border-radius: 6px;
            padding: 10px;
        }

            """)

        # Plugin Tool Box

    def get_toolbox_km_current_item(self):
        current_index = self.toolBox_KM.currentIndex()  # 获取当前选中项的索引
        item_widget = self.toolBox_KM.widget(current_index)  # 获取对应的 QWidget
        return item_widget

    def get_toolbox_km_current_item_id(self):
        item_widget = self.get_toolbox_km_current_item()
        item_id = item_widget.item_id
        return item_id

    def get_toolbox_km_current_item_type(self):
        item_widget = self.get_toolbox_km_current_item()
        item_type = item_widget.item_type
        return item_type

    def on_km_toolbox_item_changed(self, index):
        self.show_km_current_main_widget()

    # Plugin tool box

    def load_tool_plugin_records(self):
        """加载当前记录并更新工具箱内容"""
        # 清空布局中的当前插件按钮
        for i in reversed(range(self.layout_tool.count())):
            if i > 2:
                widget = self.layout_tool.itemAt(i).widget()
                if widget is not None:
                    widget.deleteLater()  # 删除现有的按钮以准备重新加载

        # 获取当前插件记录
        row = 2
        col = 0
        records = query_PluginMng_All_Tool()
        for record in records:
            print(f"ID: {record.id}, Name: {record.name}, Memo: {record.description}")
            # self.createToolBoxUnit_AgentChat(record)
            print("row:", row)
            print("col:", col)
            print("col % 2：", col % 2)
            self.layout_tool.addWidget(self.create_plugin_tool_cfg_button(record, 0),
                                       row, col % 2)

            if (col % 2) == 1:
                row = row + 1
            col = col + 1

        # self.layout_tool.setRowStretch(row + 1, 10)
        # self.layout_tool.setColumnStretch(0, 1)  # 设置第0列的拉伸系数以均衡布局
        # self.layout_tool.setColumnStretch(1, 1)  # 设置第1列的拉伸系数以均衡布局

        return row

    def load_llm_plugin_records(self):
        """加载当前记录并更新工具箱内容"""
        # 清空布局中的当前插件按钮
        for i in reversed(range(self.layout.count())):
            if i > 2:
                widget = self.layout.itemAt(i).widget()
                if widget is not None:
                    widget.deleteLater()  # 删除现有的按钮以准备重新加载

        # 获取当前插件记录
        records = query_PluginMng_All(plugin_type="LLM_Connector")
        row = 2  # 重置行计数
        col = 0  # 重置列计数

        # 遍历记录并添加到布局
        for record in records:
            print(f"ID: {record.id}, Name: {record.name}, Memo: {record.description}")
            self.layout.addWidget(self.create_plugin_cfg_button(record, 0), row, col % 2)

            if (col % 2) == 1:
                row += 1  # 每两列换行
            col += 1

        return row

    def load_llm_web_records(self, type_str="LLM"):
        """加载当前记录并更新工具箱内容"""
        # 清空布局中的当前插件按钮
        if type_str == "LLM":
            layout = self.layout_web
        else:
            layout = self.layout_web_tool

        for i in reversed(range(layout.count())):
            if i > 2:
                widget = layout.itemAt(i).widget()
                if widget is not None:
                    widget.deleteLater()  # 删除现有的按钮以准备重新加载

        # 获取当前插件记录
        records = query_web_mng_all(type=type_str)
        row = 2  # 重置行计数
        col = 0  # 重置列计数

        # 遍历记录并添加到布局
        for record in records:
            print(f"ID: {record.id}, Name: {record.name}, Memo: {record.description}")
            layout.addWidget(self.create_open_web_button(record, 0, type_str), row, col % 2)

            if (col % 2) == 1:
                row += 1  # 每两列换行
            col += 1

        return row

    def refresh_toolbox_llm_web(self, type_str="LLM"):
        """刷新工具箱以显示最新的插件记录"""
        self.load_llm_web_records(type_str)  # 重新加载插件记录

    def refresh_toolbox_llm_plugin(self):
        """刷新工具箱以显示最新的插件记录"""
        self.load_llm_plugin_records()  # 重新加载插件记录

    def refresh_toolbox_tool_plugin(self):
        """刷新工具箱以显示最新的插件记录"""
        self.load_tool_plugin_records()  # 重新加载插件记录

    def createToolBox_Plugin(self):
        self.toolBox_Plugin = QToolBox()
        self.toolBox_Plugin.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Ignored))

        # 已装模型插件
        self.buttonGroup_Plugin = QButtonGroup()
        self.buttonGroup_Plugin.setExclusive(False)
        # self.buttonGroup_Plugin.buttonClicked[int].connect(self.buttonGroupClicked_plugin_cfg)

        self.layout = QGridLayout()

        self.textEdit = QLineEdit()
        self.textEdit.setPlaceholderText(lt("Search...", "搜索..."))
        palette = self.textEdit.palette()
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("gray"))  # 可以改为其他颜色
        self.textEdit.setPalette(palette)
        self.textEdit.textChanged.connect(self.filterTextEdit)
        self.layout.addWidget(self.textEdit, 0, 0, 1, 2)
        self.layout.addWidget(self.create_install_llm_plugin_local_button(lt("Import/Copy", "导入/拷贝插件"),
                                                                          'images/add.png'), 1, 0)
        self.layout.addWidget(self.create_remove_llm_plugin_local_button(lt("Delete", "删除模型插件"), 'images/delete.png')
                              , 1, 1)
        # 连接删除按钮的点击事件到刷新功能

        # 初始化加载插件记录
        row = self.load_llm_plugin_records()

        self.layout.setRowStretch(row + 1, 10)
        self.layout.setColumnStretch(0, 1)  # 设置第0列的拉伸系数以均衡布局
        self.layout.setColumnStretch(1, 1)  # 设置第1列的拉伸系数以均衡布局
        # self.layout.setColumnStretch(2, 10)

        itemWidget = QWidget()
        itemWidget.item_id = "llm_setting_001"
        itemWidget.item_type = "llm_setting"
        itemWidget.setLayout(self.layout)

        self.toolBox_Plugin.setMinimumWidth(itemWidget.sizeHint().width())
        self.toolBox_Plugin.addItem(itemWidget, QIcon('images/llm.png'), lt("LLM Plugin", "模型插件"))

        # 已装工具插件
        self.buttonGroup_Plugin_tool = QButtonGroup()
        self.buttonGroup_Plugin_tool.setExclusive(False)
        # self.buttonGroup_Plugin_tool.buttonClicked[int].connect(self.buttonGroupClicked_plugin_cfg)

        self.layout_tool = QGridLayout()

        self.textEdit_tool = QLineEdit()
        self.textEdit_tool.setPlaceholderText(lt("Search...", "搜索..."))
        palette = self.textEdit_tool.palette()
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("gray"))  # 可以改为其他颜色
        self.textEdit_tool.setPalette(palette)
        self.textEdit_tool.textChanged.connect(self.filterTextEditTool)
        self.layout_tool.addWidget(self.textEdit_tool, 0, 0, 1, 2)
        self.layout_tool.addWidget(self.create_install_plugin_local_button(lt("Import/Copy", "导入/拷贝插件"),
                                                                           'images/add.png'), 1, 0)
        self.layout_tool.addWidget(self.create_remove_plugin_local_button(lt("Delete", "删除插件"),
                                                                          'images/delete.png'), 1, 1)

        row = 2
        col = 0
        records = query_PluginMng_All_Tool()
        for record in records:
            print(f"ID: {record.id}, Name: {record.name}, Memo: {record.description}")
            # self.createToolBoxUnit_AgentChat(record)
            print("row:", row)
            print("col:", col)
            print("col % 2：", col % 2)
            self.layout_tool.addWidget(self.create_plugin_tool_cfg_button(record, 0),
                                       row, col % 2)

            if (col % 2) == 1:
                row = row + 1
            col = col + 1

        # row = self.load_tool_plugin_records()
        self.layout_tool.setRowStretch(row + 1, 10)
        self.layout_tool.setColumnStretch(0, 1)  # 设置第0列的拉伸系数以均衡布局
        self.layout_tool.setColumnStretch(1, 1)  # 设置第1列的拉伸系数以均衡布局

        # self.layout_tool.setColumnStretch(2, 10)

        itemWidget = QWidget()
        itemWidget.item_id = "tools_setting_001"
        itemWidget.item_type = "tools_setting"
        itemWidget.setLayout(self.layout_tool)

        self.toolBox_Plugin.setMinimumWidth(itemWidget.sizeHint().width())
        self.toolBox_Plugin.addItem(itemWidget, QIcon('images/plugin_tool.png'), lt("Tools Plugin ", "工具插件"))

        # 已装MCP插件
        self.buttonGroup_Plugin_mcp = QButtonGroup()
        self.buttonGroup_Plugin_mcp.setExclusive(False)
        self.buttonGroup_Plugin_mcp.buttonClicked.connect(self.buttonGroupClicked_plugin_mcp)

        layout_mcp = QGridLayout()

        i = 0
        row = 1
        col = 0
        layout_mcp.addWidget(self.create_plugin_mcp_button("1", 0),
                                  0, 0)

        layout_mcp.addWidget(self.create_plugin_mcp_button("0", 1),
                                  0, 1)

        layout_mcp.setRowStretch(row + 1, 10)
        layout_mcp.setColumnStretch(0, 1)  # 设置第0列的拉伸系数以均衡布局
        layout_mcp.setColumnStretch(1, 1)  # 设置第1列的拉伸系数以均衡布局

        # layout_mcp.setColumnStretch(2, 10)

        itemWidget = QWidget()
        itemWidget.item_id = "mcp_setting_001"
        itemWidget.item_type = "mcp_setting"
        itemWidget.setLayout(layout_mcp)

        self.toolBox_Plugin.setMinimumWidth(itemWidget.sizeHint().width())
        self.toolBox_Plugin.addItem(itemWidget, QIcon('images/mcplogo.png'), lt("MCP", "MCP"))



        # 已装函数插件
        self.buttonGroup_Plugin_function = QButtonGroup()
        self.buttonGroup_Plugin_function.setExclusive(False)
        self.buttonGroup_Plugin_function.buttonClicked.connect(self.buttonGroupClicked_plugin_function)

        layout_function = QGridLayout()

        i = 0
        row = 1
        col = 0
        layout_function.addWidget(self.create_plugin_function_button("1", 0),
                                  0, 0)

        layout_function.addWidget(self.create_plugin_function_button("0", 1),
                                  0, 1)

        layout_function.setRowStretch(row + 1, 10)
        layout_function.setColumnStretch(0, 1)  # 设置第0列的拉伸系数以均衡布局
        layout_function.setColumnStretch(1, 1)  # 设置第1列的拉伸系数以均衡布局

        # layout_function.setColumnStretch(2, 10)

        itemWidget = QWidget()
        itemWidget.item_id = "function_setting_001"
        itemWidget.item_type = "function_setting"
        itemWidget.setLayout(layout_function)

        self.toolBox_Plugin.setMinimumWidth(itemWidget.sizeHint().width())
        self.toolBox_Plugin.addItem(itemWidget, QIcon('images/function.png'), lt("Function", "自定义函数"))

        # 已学技能
        self.buttonGroup_Plugin_skill = QButtonGroup()
        self.buttonGroup_Plugin_skill.setExclusive(False)
        self.buttonGroup_Plugin_skill.buttonClicked.connect(self.buttonGroupClicked_plugin_skill)

        layout_skill = QGridLayout()

        i = 0
        row = 1
        col = 0
        layout_skill.addWidget(self.create_plugin_skill_button("1", 0),
                               0, 0)

        layout_skill.addWidget(self.create_plugin_skill_button("0", 0),
                               0, 1)

        layout_skill.setRowStretch(row + 1, 10)
        layout_skill.setColumnStretch(0, 1)  # 设置第0列的拉伸系数以均衡布局
        layout_skill.setColumnStretch(1, 1)  # 设置第1列的拉伸系数以均衡布局

        # layout_skill.setColumnStretch(2, 10)

        itemWidget = QWidget()
        itemWidget.item_id = "skill_setting_001"
        itemWidget.item_type = "skill_setting"
        itemWidget.setLayout(layout_skill)

        self.toolBox_Plugin.setMinimumWidth(itemWidget.sizeHint().width())
        self.toolBox_Plugin.addItem(itemWidget, QIcon('images/skill.png'), lt("Computer Use", "Computer Use"))

        # 插件市场
        # self.buttonGroup_Plugin_install = QButtonGroup()
        # self.buttonGroup_Plugin_install.setExclusive(False)
        # self.buttonGroup_Plugin_install.buttonClicked.connect(self.buttonGroupClicked_plugin_install)
        #
        # self.settingLayout = QGridLayout()
        # self.settingLayout.addWidget(self.download_plugin_button(lt("Download", "下载插件")), 0, 0)
        # self.settingLayout.addWidget(self.publish_plugin_button(lt("Publish", "发布插件")), 0, 1)
        #
        # self.settingLayout.setRowStretch(row + 1, 10)
        # self.settingLayout.setColumnStretch(0, 1)  # 设置第0列的拉伸系数以均衡布局
        # self.settingLayout.setColumnStretch(1, 1)  # 设置第1列的拉伸系数以均衡布局
        #
        # itemWidget = QWidget()
        # itemWidget.item_id = "market_setting_001"
        # itemWidget.item_type = "market_setting"
        # itemWidget.setLayout(self.settingLayout)
        #
        # self.toolBox_Plugin.addItem(itemWidget, QIcon('images/market.png'), lt("Plugin Market", "插件市场"))
        self.toolBox_Plugin.currentChanged.connect(self.on_plugin_toolbox_item_changed)
        self.toolBox_Plugin.setStyleSheet("""
        QToolBox {
            background: #f0f0f0;  /* 整体背景颜色 */
            border-radius: 8px;
            padding: 5px;
        }
        QToolBox::tab {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #ffffff, stop:1 #e0e0e0);  /* 渐变背景 */

            border-radius: 6px;
            color: #333;  /* 文本颜色 */
            /*padding: 10px 15px;*/
            padding-bottom:0px;
            margin: 0px;
            font-size: 14px;
            transition: background 0.3s;  /* 背景过渡效果 */
            height: 100px;  /* 确保标签有足够的高度 */
        }
        QToolBox::tab:selected {

            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #e0e0e0, stop:1 #f0f0f0); 
            /*background: qlineargradient(x1:0, y1:0, x2:1, y2:0,stop:0 #4facfe, stop:1 #00f2fe); */ /* 选中的标签渐变色 */
            /*color: #ffffff;*/  /* 选中状态下的文本颜色 */
            font-weight: bold;
            box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.2);
        }
        QToolBox::tab:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                    stop:0 #e0e0e0, stop:1 #f0f0f0); 
        }
        QToolBox::tab QLabel {
            color: #333; /* 确保标签内的文本颜色 */
        }

        QToolBox > QWidget {  /* 仅设置QToolBox子项的背景 */
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #e0e0e0, stop:1 #e0e0e0);
            border-radius: 6px;
            padding: 10px;
        }

            """)

    def get_toolbox_plugin_current_item(self):
        current_index = self.toolBox_Plugin.currentIndex()  # 获取当前选中项的索引
        item_widget = self.toolBox_Plugin.widget(current_index)  # 获取对应的 QWidget
        return item_widget

    def get_toolbox_plugin_current_item_id(self):
        item_widget = self.get_toolbox_plugin_current_item()
        item_id = item_widget.item_id
        return item_id

    def get_toolbox_plugin_current_item_type(self):
        item_widget = self.get_toolbox_plugin_current_item()
        item_type = item_widget.item_type
        return item_type

    def on_plugin_toolbox_item_changed(self, index):
        self.show_plugin_current_main_widget()

    def filterTextEdit(self, text):
        # 根据输入框的内容过滤表格项的标题列

        # layout = QGridLayout()
        i = 0
        row = 1
        col = 0

        for i in range(self.layout.count()):
            item = self.layout.itemAt(i)

            # self.layout.itemAt(0).widget().deleteLater()  # 删除控件
            # self.layout.removeAt(0)  # 从布局中移除控件
            # item = self.layout.takeAt(0)
            # 如果项目是一个控件，则删除它
            if item.widget() and item.widget() is not None:
                # 检查是否是 QLineEdit 输入框
                if isinstance(item.widget(), QLineEdit):
                    print("Found a QLineEdit")
                # 检查是否是 QPushButton 按钮
                elif isinstance(item.widget(), QToolButton):
                    print("Found a QPushButton")
                    item.widget().deleteLater()
                else:
                    plugin_widget = item.widget()
                    print(type(plugin_widget).__name__)
                    if hasattr(plugin_widget, 'name'):
                        widget_name = plugin_widget.name
                        if text == "" or text in widget_name:
                            plugin_widget.setHidden(False)
                            # self.layout.removeWidget(plugin_widget)
                            # plugin_widget.setParent(None)
                            # self.layout.addWidget(plugin_widget, row, col % 2)
                            # if (col % 2) == 1:
                            #     row = row + 1
                            # col = col + 1
                            print("The widget has a 'name' attribute.", item.widget().name)
                        else:
                            plugin_widget.setHidden(True)

                    else:
                        print("The widget does not have a 'name' attribute.")

            # 如果项目是一个子布局，则递归清空子布

        # i = 0
        # row = 1
        # col = 0
        # records = query_PluginMng_All(plugin_type="LLM_Connector")
        # print("records-->:", records)
        # for record in records:
        #
        #     # self.createToolBoxUnit_AgentChat(record)
        #     if text not in record.name:
        #         continue
        #     print(f"ID: {record.id}, Name: {record.name}, Memo: {record.description}")
        #     self.layout.addWidget(self.create_plugin_cfg_button(record, 0),
        #                           row, col % 2)
        #
        #     if (col % 2) == 1:
        #         row = row + 1
        #     col = col + 1
        #
        # self.layout.setRowStretch(row + 1, 10)
        # self.layout.setColumnStretch(2, 10)

    def filterTextEditTool(self, text):
        # 根据输入框的内容过滤表格项的标题列
        # layout = QGridLayout()
        i = 0
        row = 1
        col = 0
        for i in range(self.layout_tool.count()):
            item = self.layout_tool.itemAt(i)
            if item.widget() and item.widget() is not None:
                # 检查是否是 QLineEdit 输入框
                if isinstance(item.widget(), QLineEdit):
                    print("Found a QLineEdit")
                else:
                    plugin_widget = item.widget()
                    print(type(plugin_widget).__name__)
                    if hasattr(plugin_widget, 'name'):
                        widget_name = plugin_widget.name
                        if text == "" or text in widget_name:
                            plugin_widget.setHidden(False)
                            # self.layout.removeWidget(plugin_widget)
                            # plugin_widget.setParent(None)
                            # self.layout.addWidget(plugin_widget, row, col % 2)
                            # if (col % 2) == 1:
                            #     row = row + 1
                            # col = col + 1
                            print("The widget has a 'name' attribute.", item.widget().name)
                        else:
                            plugin_widget.setHidden(True)

                    else:
                        print("The widget does not have a 'name' attribute.")

            # 如果项目是一个子布局，则递归清空子布

    def filterTextEdit2(self, text):
        # 根据输入框的内容过滤表格项的标题列
        for i in range(self.backgroundLayout.count()):
            item = self.backgroundLayout.itemAt(i)
            # 如果项目是一个控件，则删除它
            if item.widget() and item.widget() is not None:
                # 检查是否是 QLineEdit 输入框
                if isinstance(item.widget(), QLineEdit):
                    print("Found a QLineEdit")
                else:
                    plugin_widget = item.widget()
                    print(type(plugin_widget).__name__)
                    if hasattr(plugin_widget, 'name'):
                        widget_name = plugin_widget.name
                        if text == "" or text in widget_name:
                            plugin_widget.setHidden(False)
                            print("The widget has a 'name' attribute.", item.widget().name)
                        else:
                            plugin_widget.setHidden(True)
                    else:
                        print("The widget does not have a 'name' attribute.")

            # 如果项目是一个子布局，则递归清空子布

    def createToolBox_Web(self):
        self.toolBox_Web = QToolBox()
        self.toolBox_Web.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Ignored))

        # 已装模型插件
        self.buttonGroup_Web = QButtonGroup()
        self.buttonGroup_Web.setExclusive(False)
        # self.buttonGroup_Web.buttonClicked[int].connect(self.buttonGroupClicked_plugin_cfg)

        self.layout_web = QGridLayout()

        self.textEdit = QLineEdit()
        self.textEdit.setPlaceholderText(lt("Search...", "搜索..."))
        palette = self.textEdit.palette()
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("gray"))  # 可以改为其他颜色
        self.textEdit.setPalette(palette)
        self.textEdit.textChanged.connect(self.filterTextEdit)
        self.layout_web.addWidget(self.textEdit, 0, 0, 1, 2)
        self.layout_web.addWidget(self.create_add_web_resource_button(lt("Add", "添加"),
                                                                      'images/add.png'), 1, 0)
        self.layout_web.addWidget(self.arrange_llm_button(lt("Manage", "管理")), 1, 1)
        # 连接删除按钮的点击事件到刷新功能

        # 初始化加载插件记录
        row = self.load_llm_web_records()

        self.layout_web.setRowStretch(row + 1, 10)
        self.layout_web.setColumnStretch(0, 1)  # 设置第0列的拉伸系数以均衡布局
        self.layout_web.setColumnStretch(1, 1)  # 设置第1列的拉伸系数以均衡布局
        # self.layout.setColumnStretch(2, 10)

        itemWidget = QWidget()
        itemWidget.item_id = "web_llm_001"
        itemWidget.item_type = "web_llm"
        itemWidget.setLayout(self.layout_web)

        self.toolBox_Web.setMinimumWidth(itemWidget.sizeHint().width())
        self.toolBox_Web.addItem(itemWidget, QIcon('images/llm.png'), lt("LLM Online", "在线大模型"))

        # 已装工具插件
        self.buttonGroup_Web_tool = QButtonGroup()
        self.buttonGroup_Web_tool.setExclusive(False)
        # self.buttonGroup_Web_tool.buttonClicked[int].connect(self.buttonGroupClicked_plugin_cfg)

        self.layout_web_tool = QGridLayout()

        self.textEdit_tool = QLineEdit()
        self.textEdit_tool.setPlaceholderText(lt("Search...", "搜索..."))
        palette = self.textEdit_tool.palette()
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("gray"))  # 可以改为其他颜色
        self.textEdit_tool.setPalette(palette)
        self.textEdit_tool.textChanged.connect(self.filterTextEditTool)
        self.layout_web_tool.addWidget(self.textEdit_tool, 0, 0, 1, 2)
        self.layout_web_tool.addWidget(self.create_add_web_resource_button(lt("Add", "添加"),
                                                                           'images/add.png', "Tool"), 1, 0)

        self.layout_web_tool.addWidget(self.arrange_llm_button(lt("Manage", "管理"), "Tool"), 1, 1)
        i = 0
        row = 2
        col = 0
        # 初始化加载插件记录
        row = self.load_llm_web_records("Tool")

        self.layout_web_tool.setRowStretch(row + 1, 10)
        self.layout_web_tool.setColumnStretch(0, 1)  # 设置第0列的拉伸系数以均衡布局
        self.layout_web_tool.setColumnStretch(1, 1)  # 设置第1列的拉伸系数以均衡布局

        itemWidget = QWidget()
        itemWidget.item_id = "web_tools_001"
        itemWidget.item_type = "web_tools"
        itemWidget.setLayout(self.layout_web_tool)

        self.toolBox_Web.setMinimumWidth(itemWidget.sizeHint().width())
        self.toolBox_Web.addItem(itemWidget, QIcon('images/plugin_tool.png'), lt("AI Tools Online", "在线AI工具"))
        self.toolBox_Web.currentChanged.connect(self.on_web_toolbox_item_changed)

        self.toolBox_Web.setStyleSheet("""
        QToolBox {
            background: #f0f0f0;  /* 整体背景颜色 */
            border-radius: 8px;
            padding: 5px;
        }
        QToolBox::tab {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #ffffff, stop:1 #e0e0e0);  /* 渐变背景 */

            border-radius: 6px;
            color: #333;  /* 文本颜色 */
            /*padding: 10px 15px;*/
            padding-bottom:0px;
            margin: 0px;
            font-size: 14px;
            transition: background 0.3s;  /* 背景过渡效果 */
            height: 100px;  /* 确保标签有足够的高度 */
        }
        QToolBox::tab:selected {

            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #e0e0e0, stop:1 #f0f0f0); 
            /*background: qlineargradient(x1:0, y1:0, x2:1, y2:0,stop:0 #4facfe, stop:1 #00f2fe); */ /* 选中的标签渐变色 */
            /*color: #ffffff;*/  /* 选中状态下的文本颜色 */
            font-weight: bold;
            box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.2);
        }
        QToolBox::tab:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                    stop:0 #e0e0e0, stop:1 #f0f0f0); 
        }
        QToolBox::tab QLabel {
            color: #333; /* 确保标签内的文本颜色 */
        }

        QToolBox > QWidget {  /* 仅设置QToolBox子项的背景 */
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #e0e0e0, stop:1 #e0e0e0);
            border-radius: 6px;
            padding: 10px;
        }

            """)

    def get_toolbox_web_current_item(self):
        current_index = self.toolBox_Web.currentIndex()  # 获取当前选中项的索引
        item_widget = self.toolBox_Web.widget(current_index)  # 获取对应的 QWidget
        return item_widget

    def get_toolbox_web_current_item_id(self):
        item_widget = self.get_toolbox_web_current_item()
        item_id = item_widget.item_id
        return item_id

    def get_toolbox_web_current_item_type(self):
        item_widget = self.get_toolbox_web_current_item()
        item_type = item_widget.item_type
        return item_type

    def on_web_toolbox_item_changed(self, index):
        self.show_web_current_main_widget()

    # createToolBox_WorkFlow
    def createToolBoxUnit_WorkFlow(self, record):
        pass

    def createToolBox_WorkFlow(self):
        self.toolBox_Workflow = QToolBox()
        self.toolBox_Workflow.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Ignored))

        # 工作流
        self.buttonGroup_WorkFlow = QButtonGroup()
        self.buttonGroup_WorkFlow.setExclusive(False)
        # self.buttonGroup_WorkFlow.buttonClicked[int].connect(self.buttonGroupClicked_plugin_cfg)
        self.buttonGroup_WorkFlow.buttonClicked.connect(self.buttonGroupClicked_workflow)

        layout_workflow = QGridLayout()

        i = 0
        row = 1
        col = 0

        layout_workflow.addWidget(self.create_workflow_cfg_button(0),
                                  0, 0)

        layout_workflow.addWidget(self.create_task_schedule_button(1),
                                  0, 1)

        layout_workflow.setRowStretch(1, 10)  # 第2行的拉伸系数
        layout_workflow.setColumnStretch(0, 1)  # 设置第0列的拉伸系数以均衡布局
        layout_workflow.setColumnStretch(1, 1)  # 设置第1列的拉伸系数以均衡布局

        itemWidget = QWidget()
        itemWidget.setLayout(layout_workflow)

        self.toolBox_Workflow.setMinimumWidth(itemWidget.sizeHint().width())
        self.toolBox_Workflow.addItem(itemWidget, QIcon('images/workflow_toolbox.png'), lt("WorkFlow", "工作流"))

        self.toolBox_Workflow.setStyleSheet("""
        QToolBox {
            background: #f0f0f0;  /* 整体背景颜色 */
            border-radius: 8px;
            padding: 5px;
        }
        QToolBox::tab {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #ffffff, stop:1 #e0e0e0);  /* 渐变背景 */

            border-radius: 6px;
            color: #333;  /* 文本颜色 */
            /*padding: 10px 15px;*/
            padding-bottom:0px;
            margin: 0px;
            font-size: 14px;
            transition: background 0.3s;  /* 背景过渡效果 */
            height: 100px;  /* 确保标签有足够的高度 */
        }
        QToolBox::tab:selected {

            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #e0e0e0, stop:1 #f0f0f0); 
            /*background: qlineargradient(x1:0, y1:0, x2:1, y2:0,stop:0 #4facfe, stop:1 #00f2fe); */ /* 选中的标签渐变色 */
            /*color: #ffffff;*/  /* 选中状态下的文本颜色 */
            font-weight: bold;
            box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.2);
        }
        QToolBox::tab:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                    stop:0 #e0e0e0, stop:1 #f0f0f0); 
        }
        QToolBox::tab QLabel {
            color: #333; /* 确保标签内的文本颜色 */
        }

        QToolBox > QWidget {  /* 仅设置QToolBox子项的背景 */
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #e0e0e0, stop:1 #e0e0e0);
            border-radius: 6px;
            padding: 10px;
        }

            """)

    # Setting Tool Box

    def createToolBox_Home(self):
        self.buttonGroup_Setting = QButtonGroup()
        self.buttonGroup_Setting.setExclusive(False)
        # self.buttonGroup_Setting.buttonClicked[int].connect(self.buttonGroupClicked)

        layout = QGridLayout()
        layout.addWidget(self.createCellWidgetInitCfg(lt("Initialization", "初始化"), 0), 0, 0)
        # layout.addWidget(self.createCellWidgetGeneralCfg(lt("Configuration", "系统设置"), 0),
        #                  0, 1)
        layout.addWidget(self.createCellWidgetHelp(lt("Help", "帮助"), 0),
                         0, 1)



        layout.setRowStretch(3, 10)
        layout.setColumnStretch(0, 1)  # 设置第0列的拉伸系数以均衡布局
        layout.setColumnStretch(1, 1)  # 设置第1列的拉伸系数以均衡布局
        # layout.setColumnStretch(2, 10)

        itemWidget = QWidget()
        itemWidget.setLayout(layout)

        self.toolBox_Home = QToolBox()
        self.toolBox_Home.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Ignored))
        self.toolBox_Home.setMinimumWidth(itemWidget.sizeHint().width())
        self.toolBox_Home.addItem(itemWidget, QIcon('images/setting.png'), lt("Setting", "系统管理"))
        self.toolBox_Home.setStyleSheet("""
        QToolBox {
            background: #f0f0f0;  /* 整体背景颜色 */
            border-radius: 8px;
            padding: 5px;
        }
        QToolBox::tab {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #ffffff, stop:1 #e0e0e0);  /* 渐变背景 */

            border-radius: 6px;
            color: #333;  /* 文本颜色 */
            /*padding: 10px 15px;*/
            padding-bottom:0px;
            margin: 0px;
            font-size: 14px;
            transition: background 0.3s;  /* 背景过渡效果 */
            height: 100px;  /* 确保标签有足够的高度 */
        }
        QToolBox::tab:selected {

            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #e0e0e0, stop:1 #f0f0f0); 
            /*background: qlineargradient(x1:0, y1:0, x2:1, y2:0,stop:0 #4facfe, stop:1 #00f2fe); */ /* 选中的标签渐变色 */
            /*color: #ffffff;*/  /* 选中状态下的文本颜色 */
            font-weight: bold;
            box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.2);
        }
        QToolBox::tab:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                    stop:0 #e0e0e0, stop:1 #f0f0f0); 
        }
        QToolBox::tab QLabel {
            color: #333; /* 确保标签内的文本颜色 */
        }

        QToolBox > QWidget {  /* 仅设置QToolBox子项的背景 */
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #e0e0e0, stop:1 #e0e0e0);
            border-radius: 6px;
            padding: 10px;
        }

            """)

    def show_agent_toolbox_stack(self):
        orgfont = QFont()
        orgfont.setBold(False)
        orgfont.setUnderline(False)

        font = QFont()
        font.setBold(True)

        self.ai2meAction.setFont(orgfont)
        self.ai2aiAction.setFont(orgfont)
        self.kmAction.setFont(orgfont)
        # self.workflowAction.setFont(orgfont)
        self.pluginAction.setFont(orgfont)
        self.webAction.setFont(orgfont)
        self.homeAction.setFont(orgfont)

        self.ai2meAction.setFont(font)
        self.stack_toolbox.setCurrentWidget(self.toolBox_AgentChat)
        self.show_agent_current_main_widget()

    def show_ai_toolbox_stack(self):
        orgfont = QFont()
        orgfont.setBold(False)
        orgfont.setUnderline(False)

        font = QFont()
        font.setBold(True)

        self.ai2meAction.setFont(orgfont)
        self.ai2aiAction.setFont(orgfont)
        self.kmAction.setFont(orgfont)
        # self.workflowAction.setFont(orgfont)
        self.pluginAction.setFont(orgfont)
        self.webAction.setFont(orgfont)
        self.homeAction.setFont(orgfont)

        self.ai2aiAction.setFont(font)
        self.stack_toolbox.setCurrentWidget(self.toolBox_AiChat)
        self.show_ai_current_main_widget()

    def show_km_toolbox_stack(self):
        orgfont = QFont()
        orgfont.setBold(False)
        orgfont.setUnderline(False)

        font = QFont()
        font.setBold(True)

        self.ai2meAction.setFont(orgfont)
        self.ai2aiAction.setFont(orgfont)
        self.kmAction.setFont(orgfont)
        # self.workflowAction.setFont(orgfont)
        self.pluginAction.setFont(orgfont)
        self.webAction.setFont(orgfont)
        self.homeAction.setFont(orgfont)

        self.kmAction.setFont(font)
        self.stack_toolbox.setCurrentWidget(self.toolBox_KM)
        self.show_km_current_main_widget()

    def show_workflow_toolbox_stack(self):
        orgfont = QFont()
        orgfont.setBold(False)
        orgfont.setUnderline(False)

        font = QFont()
        font.setBold(True)
        self.ai2meAction.setFont(orgfont)
        self.ai2aiAction.setFont(orgfont)
        self.kmAction.setFont(orgfont)
        # self.workflowAction.setFont(orgfont)
        self.pluginAction.setFont(orgfont)
        self.webAction.setFont(orgfont)
        self.homeAction.setFont(orgfont)

        # self.workflowAction.setFont(font)
        # self.stack_toolbox.setCurrentWidget(self.toolBox_Workflow)
        # self.show_workflow_current_main_widget()

    def show_plugin_toolbox_stack(self):
        orgfont = QFont()
        orgfont.setBold(False)
        orgfont.setUnderline(False)

        font = QFont()
        font.setBold(True)
        self.ai2meAction.setFont(orgfont)
        self.ai2aiAction.setFont(orgfont)
        self.kmAction.setFont(orgfont)
        # self.workflowAction.setFont(orgfont)
        self.pluginAction.setFont(orgfont)
        self.webAction.setFont(orgfont)
        self.homeAction.setFont(orgfont)

        self.pluginAction.setFont(font)
        self.stack_toolbox.setCurrentWidget(self.toolBox_Plugin)
        self.show_plugin_current_main_widget()

    def show_web_toolbox_stack(self):
        orgfont = QFont()
        orgfont.setBold(False)
        orgfont.setUnderline(False)

        font = QFont()
        font.setBold(True)
        self.ai2meAction.setFont(orgfont)
        self.ai2aiAction.setFont(orgfont)
        self.kmAction.setFont(orgfont)
        # self.workflowAction.setFont(orgfont)
        self.pluginAction.setFont(orgfont)
        self.webAction.setFont(orgfont)
        self.homeAction.setFont(orgfont)

        self.webAction.setFont(font)
        self.stack_toolbox.setCurrentWidget(self.toolBox_Web)
        self.show_web_current_main_widget()

    def show_app_home_toolbox_stack(self):
        orgfont = QFont()
        orgfont.setBold(False)
        orgfont.setUnderline(False)

        font = QFont()
        font.setBold(True)
        self.ai2meAction.setFont(orgfont)
        self.ai2aiAction.setFont(orgfont)
        self.kmAction.setFont(orgfont)
        # self.workflowAction.setFont(orgfont)
        self.pluginAction.setFont(orgfont)
        self.webAction.setFont(orgfont)
        self.homeAction.setFont(orgfont)

        self.homeAction.setFont(font)
        self.stack_toolbox.setCurrentWidget(self.toolBox_Home)
        self.show_app_home_current_main_widget()

    def create_toolbar_actions(self):
        self.ai2aiAction = QAction(
            QIcon('images/aichat.png'), "Ai和Ai之间的社交，比如在线聊天",
            self, shortcut="Ctrl+1", statusTip="Ai和Ai之间的社交，比如在线聊天",
            triggered=self.show_ai_toolbox_stack, iconText=lt("SNS", "AI社交"))

        font = QFont()
        font.setBold(True)
        self.ai2aiAction.setFont(font)


        self.ai2meAction = QAction(QIcon('images/agent.png'),
                                   "为我处理工作的Ai智能体", self, shortcut="Ctrl+2",
                                   statusTip="为我处理工作的Ai智能体",
                                   triggered=self.show_agent_toolbox_stack, iconText="Agent")





        self.kmAction = QAction(
            QIcon('images/km.png'), lt("KM", "知识库"),
            self, shortcut="Ctrl+3", statusTip="知识库",
            triggered=self.show_km_toolbox_stack, iconText=lt("KM", "知识库"))

        # self.workflowAction = QAction(
        #     QIcon('images/workflow.png'), lt("WorkFlow", "工作流"),
        #     self, shortcut="Ctrl+4", statusTip="工作流",
        #     triggered=self.show_workflow_toolbox_stack, iconText=lt("WorkFlow", "工作流"))

        self.pluginAction = QAction(
            QIcon('images/tool.png'), lt("Tools", "工具"),
            self, shortcut="Ctrl+4", statusTip="Tools",
            triggered=self.show_plugin_toolbox_stack, iconText=lt("Tools", "工具"))

        self.webAction = QAction(
            QIcon('images/webresource.png'), lt("Web", "网络资源"),
            self, shortcut="Ctrl+5", statusTip=lt("Web", "网络资源"),
            triggered=self.show_web_toolbox_stack, iconText=lt("Web", "网络资源"))

        self.homeAction = QAction(
            QIcon('images/aisns150.png'), lt("Home", "首页"),
            self, shortcut="Ctrl+6", statusTip="系统管理",
            triggered=self.show_app_home_toolbox_stack, iconText=lt("Home", "首页"))

    def createToolbars(self):
        # Create Ai Toolbar
        top_toolbar = QToolBar("Top_Toolbar")
        top_toolbar.addAction(self.ai2aiAction)
        top_toolbar.addAction(self.ai2meAction)
        # ai_toolbar.addAction(self.chatAction)
        top_toolbar.addAction(self.kmAction)
        # top_toolbar.addAction(self.workflowAction)
        top_toolbar.addAction(self.pluginAction)
        top_toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        # ai_toolbar.setFixedHeight(350)
        top_toolbar.setFixedHeight(600)
        top_toolbar.setFixedWidth(70)
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, top_toolbar)

        bottom_toolbar = QToolBar("Bottom_Toolbar")
        bottom_toolbar.addAction(self.webAction)
        bottom_toolbar.addAction(self.homeAction)
        bottom_toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, bottom_toolbar)

        toolbar_container = QToolBar()
        toolbar_container.setOrientation(Qt.Orientation.Vertical)
        toolbar_container.addWidget(top_toolbar)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        toolbar_container.addWidget(spacer)

        toolbar_container.addWidget(bottom_toolbar)

        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, toolbar_container)

    def create_install_plugin_button(self, plugin_data, image):
        plugin_name = plugin_data["name"]
        button = QToolButton()
        button.setText(plugin_name)
        button.setIcon(QIcon(image))
        button.setIconSize(QSize(50, 50))
        button.setCheckable(False)
        button.clicked.connect(lambda: self.plugin_install_dialog(plugin_data))
        button.setStyleSheet("""QToolButton {                        
                       background:#a9d7ff
                    }""")
        self.buttonGroup_Plugin_install.addButton(button)

        layout = QGridLayout()
        layout.addWidget(button, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(plugin_name), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.name = plugin_name
        widget.setLayout(layout)

        return widget

    def agentopendialog(self):
        model = QStandardItemModel()
        agents = query_AgentCfg_All(is_delete=0)
        header = ["显示", "user_id", "名称", "简介", "专长", "社交帐号"]
        model.setHorizontalHeaderLabels(header)
        row = 0
        for agent in agents:
            checkbox_item = QStandardItem()
            checkbox_item.setCheckable(True)
            checkbox_item.setCheckState(Qt.CheckState.Checked if agent.is_show else Qt.CheckState.Unchecked)
            model.setItem(row, 0, checkbox_item)

            newItem = QStandardItem(agent.user_id)
            print("agent.id:", agent.user_id)
            newItem.setFlags(newItem.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make items non-editable
            model.setItem(row, 1, newItem)

            newItem = QStandardItem(agent.name)
            newItem.setFlags(newItem.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make items non-editable
            model.setItem(row, 2, newItem)

            newItem2 = QStandardItem(agent.memo)
            newItem2.setFlags(newItem2.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make items non-editable
            model.setItem(row, 3, newItem2)

            newItem3 = QStandardItem(agent.specialization)
            newItem3.setFlags(newItem3.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make items non-editable
            model.setItem(row, 4, newItem3)

            newItem4 = QStandardItem(agent.snsaccount)
            newItem4.setFlags(newItem4.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make items non-editable
            model.setItem(row, 5, newItem4)

            row += 1

        dialog = AgentFreezeTableDialog(model, self)
        dialog.exec()

    def agentmultiopendialog(self):
        model = QStandardItemModel()
        agents = query_MutiAgentCfg_All(is_delete=0)
        header = ["显示", "group_id", "名称", "简介", "成员", "群主"]
        model.setHorizontalHeaderLabels(header)
        row = 0
        for agent in agents:
            checkbox_item = QStandardItem()
            checkbox_item.setCheckable(True)
            checkbox_item.setCheckState(Qt.CheckState.Checked if agent.is_show else Qt.CheckState.Unchecked)
            model.setItem(row, 0, checkbox_item)

            newItem = QStandardItem(agent.group_id)
            newItem.setFlags(newItem.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make items non-editable
            model.setItem(row, 1, newItem)

            newItem = QStandardItem(agent.name)
            newItem.setFlags(newItem.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make items non-editable
            model.setItem(row, 2, newItem)

            newItem2 = QStandardItem(agent.memo)
            newItem2.setFlags(newItem2.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make items non-editable
            model.setItem(row, 3, newItem2)

            # newItem3 = QStandardItem(",".join([query_AgentCfg(user_id=user_id).name for user_id in agent.agents.split(",")]))
            newItem3 = QStandardItem(",".join(
                [query_AgentCfg(user_id=user_id).name for user_id in agent.agents.split(",")]) if agent.agents else "")
            newItem3.setFlags(newItem3.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make items non-editable
            model.setItem(row, 4, newItem3)

            newItem4 = QStandardItem(query_AgentCfg(user_id=agent.agentcommander).name)
            newItem4.setFlags(newItem4.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make items non-editable
            model.setItem(row, 5, newItem4)

            row += 1

        dialog = AgentMultiFreezeTableDialog(model, self)
        dialog.exec()

    def aiopendialog(self):
        model = QStandardItemModel()
        agents = query_AiChatCfg_All(is_delete=0)
        header = ["", "user_id", "帐号", "昵称", "签名", "状态"]
        model.setHorizontalHeaderLabels(header)
        row = 0
        for agent in agents:
            checkbox_item = QStandardItem()
            checkbox_item.setCheckable(False)
            model.setItem(row, 0, checkbox_item)

            newItem = QStandardItem(agent.user_id)
            newItem.setFlags(newItem.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make items non-editable
            model.setItem(row, 1, newItem)

            newItem = QStandardItem(agent.account)
            newItem.setFlags(newItem.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make items non-editable
            model.setItem(row, 2, newItem)

            newItem2 = QStandardItem(agent.nickname)
            newItem2.setFlags(newItem2.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make items non-editable
            model.setItem(row, 3, newItem2)

            newItem3 = QStandardItem(agent.sign)
            newItem3.setFlags(newItem3.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make items non-editable
            model.setItem(row, 4, newItem3)

            newItem4 = QStandardItem(agent.status)
            newItem4.setFlags(newItem4.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make items non-editable
            model.setItem(row, 5, newItem4)

            row += 1

        dialog = AiFreezeTableDialog(model, self)
        dialog.exec()

    def humanopendialog(self):
        model = QStandardItemModel()
        agents = query_HumanChatCfg_All(is_delete=0)
        header = ["", "user_id", "帐号", "昵称", "签名", "状态"]
        model.setHorizontalHeaderLabels(header)
        row = 0
        for agent in agents:
            checkbox_item = QStandardItem()
            checkbox_item.setCheckable(False)
            model.setItem(row, 0, checkbox_item)

            newItem = QStandardItem(agent.user_id)
            newItem.setFlags(newItem.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make items non-editable
            model.setItem(row, 1, newItem)

            newItem = QStandardItem(agent.account)
            newItem.setFlags(newItem.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make items non-editable
            model.setItem(row, 2, newItem)

            newItem2 = QStandardItem(agent.nickname)
            newItem2.setFlags(newItem2.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make items non-editable
            model.setItem(row, 3, newItem2)

            newItem3 = QStandardItem(agent.sign)
            newItem3.setFlags(newItem3.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make items non-editable
            model.setItem(row, 4, newItem3)

            newItem4 = QStandardItem(agent.status)
            newItem4.setFlags(newItem4.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make items non-editable
            model.setItem(row, 5, newItem4)

            row += 1

        dialog = HumanFreezeTableDialog(model)
        dialog.exec()

    def open_llm_arrange_dialog(self, type_str="LLM"):
        model = QStandardItemModel()
        agents = query_web_mng_all(type=type_str)
        header = ["", "web_id", "名称", "简介", "地址", "图标"]
        model.setHorizontalHeaderLabels(header)
        row = 0
        for agent in agents:
            checkbox_item = QStandardItem()
            checkbox_item.setCheckable(False)
            model.setItem(row, 0, checkbox_item)

            newItem = QStandardItem(agent.web_id)
            newItem.setFlags(newItem.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make items non-editable
            model.setItem(row, 1, newItem)

            newItem = QStandardItem(agent.name)
            newItem.setFlags(newItem.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make items non-editable
            model.setItem(row, 2, newItem)

            newItem = QStandardItem(agent.description)
            newItem.setFlags(newItem.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make items non-editable
            model.setItem(row, 3, newItem)

            newItem2 = QStandardItem(agent.url)
            newItem2.setFlags(newItem2.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make items non-editable
            model.setItem(row, 4, newItem2)

            newItem3 = QStandardItem(agent.filename)
            newItem3.setFlags(newItem3.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make items non-editable
            model.setItem(row, 5, newItem3)

            row += 1

        dialog = LLMArrangeFreezeTableDialog(model, self, type_str)
        dialog.exec()

    def open_tools_arrange_dialog(self):
        model = QStandardItemModel()
        agents = query_web_mng_all(type="LLM")
        header = ["", "web_id", "名称", "简介", "地址", "图标"]
        model.setHorizontalHeaderLabels(header)
        row = 0
        for agent in agents:
            checkbox_item = QStandardItem()
            checkbox_item.setCheckable(False)
            model.setItem(row, 0, checkbox_item)

            newItem = QStandardItem(agent.web_id)
            newItem.setFlags(newItem.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make items non-editable
            model.setItem(row, 1, newItem)

            newItem = QStandardItem(agent.name)
            newItem.setFlags(newItem.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make items non-editable
            model.setItem(row, 2, newItem)

            newItem = QStandardItem(agent.description)
            newItem.setFlags(newItem.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make items non-editable
            model.setItem(row, 3, newItem)

            newItem2 = QStandardItem(agent.url)
            newItem2.setFlags(newItem2.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make items non-editable
            model.setItem(row, 4, newItem2)

            newItem3 = QStandardItem(agent.filename)
            newItem3.setFlags(newItem3.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make items non-editable
            model.setItem(row, 5, newItem3)

            row += 1

        dialog = LLMArrangeFreezeTableDialog(model, self)
        dialog.exec()

    def kmopendialog(self):
        model = QStandardItemModel()
        agents = query_KMCfg_All(is_delete=0)
        header = ["", "km_id", "名称", "简介", "标签", "路径"]
        model.setHorizontalHeaderLabels(header)
        row = 0
        for agent in agents:
            checkbox_item = QStandardItem()
            checkbox_item.setCheckable(False)
            model.setItem(row, 0, checkbox_item)

            newItem = QStandardItem(agent.km_id)
            newItem.setFlags(newItem.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make items non-editable
            model.setItem(row, 1, newItem)

            newItem = QStandardItem(agent.name)
            newItem.setFlags(newItem.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make items non-editable
            model.setItem(row, 2, newItem)

            newItem = QStandardItem(agent.memo)
            newItem.setFlags(newItem.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make items non-editable
            model.setItem(row, 3, newItem)

            newItem2 = QStandardItem(agent.label)
            newItem2.setFlags(newItem2.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make items non-editable
            model.setItem(row, 4, newItem2)

            newItem3 = QStandardItem(agent.kmpath)
            newItem3.setFlags(newItem3.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make items non-editable
            model.setItem(row, 5, newItem3)

            row += 1

        dialog = KmFreezeTableDialog(model, self)
        dialog.exec()

    def kvopendialog(self):
        print("hello")
        self.keyvalue_manager = KeyValueManager(self)
        self.keyvalue_manager.exec()

    def logopendialog(self):
        model = QStandardItemModel()
        agents = query_LogsMng_All(is_delete=0)
        header = ["", "logs_id", "内容", "类型", "时间"]
        model.setHorizontalHeaderLabels(header)
        row = 0
        for agent in agents:
            checkbox_item = QStandardItem()
            checkbox_item.setCheckable(False)
            model.setItem(row, 0, checkbox_item)

            newItem = QStandardItem(agent.logs_id)
            newItem.setFlags(newItem.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make items non-editable
            model.setItem(row, 1, newItem)

            newItem = QStandardItem(agent.content)
            newItem.setFlags(newItem.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make items non-editable
            model.setItem(row, 2, newItem)

            newItem = QStandardItem(agent.type)
            newItem.setFlags(newItem.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make items non-editable
            model.setItem(row, 3, newItem)

            newItem2 = QStandardItem(str(agent.create_time))
            newItem2.setFlags(newItem2.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make items non-editable
            model.setItem(row, 4, newItem2)

            row += 1

        dialog = LogsFreezeTableDialog(model)
        dialog.exec()

    def createCellWidgetAiChatMng(self, text, image):
        # agetnconfigdlg = FreezeTableDialog(self)
        agentcfgbutton = QToolButton()
        agentcfgbutton.setIcon(QIcon(image))
        agentcfgbutton.setIconSize(QSize(50, 50))
        agentcfgbutton.setCheckable(False)
        agentcfgbutton.clicked.connect(self.aiopendialog)

        # self.backgroundButtonGroup.addButton(agentcfgbutton)

        layout = QGridLayout()
        layout.addWidget(agentcfgbutton, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def createCellWidgetHumanChatMng(self, text, image):
        # agetnconfigdlg = FreezeTableDialog(self)
        agentcfgbutton = QToolButton()
        agentcfgbutton.setIcon(QIcon(image))
        agentcfgbutton.setIconSize(QSize(50, 50))
        agentcfgbutton.setCheckable(False)
        agentcfgbutton.clicked.connect(self.humanopendialog)

        # self.backgroundButtonGroup.addButton(agentcfgbutton)

        layout = QGridLayout()
        layout.addWidget(agentcfgbutton, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def arrange_llm_button(self, text, type_str="LLM"):
        # agetnconfigdlg = FreezeTableDialog(self)
        agentcfgbutton = QToolButton()
        agentcfgbutton.setIcon(QIcon("images/setting.png"))
        agentcfgbutton.setIconSize(QSize(50, 50))
        agentcfgbutton.setCheckable(False)
        agentcfgbutton.clicked.connect(lambda: self.open_llm_arrange_dialog(type_str))

        # self.backgroundButtonGroup.addButton(agentcfgbutton)

        layout = QGridLayout()
        layout.addWidget(agentcfgbutton, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def createCellWidgetKMMng(self, text, image):
        # agetnconfigdlg = FreezeTableDialog(self)
        agentcfgbutton = QToolButton()
        agentcfgbutton.setIcon(QIcon(image))
        agentcfgbutton.setIconSize(QSize(50, 50))
        agentcfgbutton.setCheckable(False)
        agentcfgbutton.clicked.connect(self.kmopendialog)

        # self.backgroundButtonGroup.addButton(agentcfgbutton)

        layout = QGridLayout()
        layout.addWidget(agentcfgbutton, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def createCellWidgetKVMng(self, text, image):
        # agetnconfigdlg = FreezeTableDialog(self)
        agentcfgbutton = QToolButton()
        agentcfgbutton.setIcon(QIcon(image))
        agentcfgbutton.setIconSize(QSize(50, 50))
        agentcfgbutton.setCheckable(False)
        agentcfgbutton.clicked.connect(self.kvopendialog)

        # self.backgroundButtonGroup.addButton(agentcfgbutton)

        layout = QGridLayout()
        layout.addWidget(agentcfgbutton, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def plugin_install_local(self):
        zip_file_path = self.setOpenFileName()
        if zip_file_path != "":
            self.plugin_install(zip_file_path)

    def create_remove_llm_plugin_local_button(self, text, image):
        button = QToolButton()
        button.setIcon(QIcon(image))
        button.setIconSize(QSize(50, 50))
        button.setCheckable(False)
        button.clicked.connect(self.remove_llm_plugin)

        # self.buttonGroup_Plugin_install.addButton(button)

        layout = QGridLayout()
        layout.addWidget(button, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def create_install_tool_plugin_local_button(self, text, image):
        button = QToolButton()
        button.setIcon(QIcon(image))
        button.setIconSize(QSize(50, 50))
        button.setCheckable(False)
        button.clicked.connect(self.show_tool_choice_dialog)

        # self.buttonGroup_Plugin_install.addButton(button)

        layout = QGridLayout()
        layout.addWidget(button, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def create_install_llm_plugin_local_button(self, text, image):
        button = QToolButton()
        button.setIcon(QIcon(image))
        button.setIconSize(QSize(50, 50))
        button.setCheckable(False)
        button.clicked.connect(self.show_choice_dialog)

        # self.buttonGroup_Plugin_install.addButton(button)

        layout = QGridLayout()
        layout.addWidget(button, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def create_add_web_resource_button(self, text, image, type_flag="LLM"):
        button = QToolButton()
        button.setIcon(QIcon(image))
        button.setIconSize(QSize(50, 50))
        button.setCheckable(False)
        button.clicked.connect(lambda: self.add_web_resource(type_flag))

        # self.buttonGroup_Plugin_install.addButton(button)

        layout = QGridLayout()
        layout.addWidget(button, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def show_tool_choice_dialog(self):
        # 创建消息框并设置相关属性
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle('操作选择')
        msg_box.setText('您想通过导入还是拷贝来添加新的大模型连接器:')
        msg_box.setIcon(QMessageBox.Question)

        # 添加按钮
        copy_button = msg_box.addButton('拷贝', QMessageBox.AcceptRole)
        import_button = msg_box.addButton('导入', QMessageBox.RejectRole)

        # 显示消息框
        msg_box.exec()

        # 根据用户选择的按钮进行相应操作
        if msg_box.clickedButton() == copy_button:
            self.handle_copy_tool()
        elif msg_box.clickedButton() == import_button:
            self.handle_import()

    def show_choice_dialog(self):
        # 创建消息框并设置相关属性
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle('操作选择')
        msg_box.setText('您想通过导入还是拷贝来添加新的大模型连接器:')
        msg_box.setIcon(QMessageBox.Question)

        # 添加按钮
        copy_button = msg_box.addButton('拷贝', QMessageBox.AcceptRole)
        import_button = msg_box.addButton('导入', QMessageBox.RejectRole)

        # 显示消息框
        msg_box.exec()

        # 根据用户选择的按钮进行相应操作
        if msg_box.clickedButton() == copy_button:
            self.handle_copy()
        elif msg_box.clickedButton() == import_button:
            self.handle_import()

    def handle_import(self):
        self.plugin_install_local()

    def handle_copy(self):
        # 定义插件简称的有效性检查函数
        def is_valid_alias(alias):
            # 检查简称是否以字母开头，并且只包含字母、数字和下划线
            return bool(re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', alias))

        # 创建对话框
        transfer_dialog = QDialog()
        transfer_dialog.setWindowTitle("选择")
        transfer_dialog.setMinimumWidth(500)

        # 创建主垂直布局
        main_layout = QVBoxLayout()

        # 创建表单布局
        form_layout = QFormLayout()

        # 创建第一个组合框并填充数据
        transfer_dialog.comboBox = QComboBox()
        transfer_dialog.comboBox.setEditable(False)
        records = query_PluginMng_All(plugin_type="LLM_Connector")

        for record in records:
            transfer_dialog.comboBox.addItem(record.name, record.plugin_id)

        form_layout.addRow("选择要拷贝的大模型插件：", transfer_dialog.comboBox)

        # 添加插件名称输入框
        transfer_dialog.plugin_name_input = QLineEdit()
        form_layout.addRow("插件名称：", transfer_dialog.plugin_name_input)

        # 添加插件简称输入框
        transfer_dialog.alias_name_input = QLineEdit()
        form_layout.addRow("插件简称：", transfer_dialog.alias_name_input)

        # 将表单布局添加到主布局
        main_layout.addLayout(form_layout)

        # 创建按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)

        # 创建确定和取消按钮
        ok_button = QPushButton("确定")

        cancel_button = QPushButton("取消")

        # 连接按钮事件
        def on_ok_clicked():
            # 获取输入的插件名称和简称
            plugin_name = transfer_dialog.plugin_name_input.text()
            alias_name = transfer_dialog.alias_name_input.text()

            # 检查插件简称的有效性
            if not plugin_name.strip():
                QMessageBox.warning(transfer_dialog, "错误", "插件名称不能为空。")
                return

            if not is_valid_alias(alias_name):
                QMessageBox.warning(transfer_dialog, "错误", "插件简称无效。它必须以字母开头，并且只包含字母、数字和下划线。")
                return

            transfer_dialog.accept()

        ok_button.clicked.connect(on_ok_clicked)
        cancel_button.clicked.connect(transfer_dialog.reject)

        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        # 将按钮布局添加到主布局
        main_layout.addLayout(button_layout)

        # 设置主布局
        transfer_dialog.setLayout(main_layout)

        # 显示对话框并处理结果
        if transfer_dialog.exec():
            # 获取选择的插件ID
            plugin_id = transfer_dialog.comboBox.currentData()
            plugin_name = transfer_dialog.plugin_name_input.text()
            alias_name = transfer_dialog.alias_name_input.text()
            record = query_PluginMng(plugin_id=plugin_id)
            src_dir = util.build_full_path(f"pluginsmanager,plugins,{record.alias_name}")
            dst_dir = util.build_full_path(f"pluginsmanager,plugins,{alias_name}")
            util.copy_directory(src_dir, dst_dir)
            new_plugin_id = util.generate_random_id()
            dbfactory.copy_plugin_record(plugin_id, new_plugin_id, alias_name=alias_name, name=plugin_name, plugin_directory=alias_name)
            QMessageBox.information(self, '成功', f'插件拷贝成功。')
            self.refresh_toolbox_llm_plugin()
            # 在这里继续处理复制插件的逻辑
            # ...

    def handle_copy_tool(self):
        # 定义插件简称的有效性检查函数
        def is_valid_alias(alias):
            # 检查简称是否以字母开头，并且只包含字母、数字和下划线
            return bool(re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', alias))

        # 创建对话框
        transfer_dialog = QDialog()
        transfer_dialog.setWindowTitle("选择")
        transfer_dialog.setMinimumWidth(500)

        # 创建主垂直布局
        main_layout = QVBoxLayout()

        # 创建表单布局
        form_layout = QFormLayout()

        # 创建第一个组合框并填充数据
        transfer_dialog.comboBox = QComboBox()
        transfer_dialog.comboBox.setEditable(False)
        records = query_PluginMng_All_Tool()

        for record in records:
            transfer_dialog.comboBox.addItem(record.name, record.plugin_id)

        form_layout.addRow("选择要拷贝的插件：", transfer_dialog.comboBox)

        # 添加插件名称输入框
        transfer_dialog.plugin_name_input = QLineEdit()
        form_layout.addRow("插件名称：", transfer_dialog.plugin_name_input)

        # 添加插件简称输入框
        transfer_dialog.alias_name_input = QLineEdit()
        form_layout.addRow("插件简称：", transfer_dialog.alias_name_input)

        # 将表单布局添加到主布局
        main_layout.addLayout(form_layout)

        # 创建按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)

        # 创建确定和取消按钮
        ok_button = QPushButton("确定")

        cancel_button = QPushButton("取消")

        # 连接按钮事件
        def on_ok_clicked():
            # 获取输入的插件名称和简称
            plugin_name = transfer_dialog.plugin_name_input.text()
            alias_name = transfer_dialog.alias_name_input.text()

            # 检查插件简称的有效性
            if not plugin_name.strip():
                QMessageBox.warning(transfer_dialog, "错误", "插件名称不能为空。")
                return

            if not is_valid_alias(alias_name):
                QMessageBox.warning(transfer_dialog, "错误", "插件简称无效。它必须以字母开头，并且只包含字母、数字和下划线。")
                return

            transfer_dialog.accept()

        ok_button.clicked.connect(on_ok_clicked)
        cancel_button.clicked.connect(transfer_dialog.reject)

        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        # 将按钮布局添加到主布局
        main_layout.addLayout(button_layout)

        # 设置主布局
        transfer_dialog.setLayout(main_layout)

        # 显示对话框并处理结果
        if transfer_dialog.exec():
            # 获取选择的插件ID
            plugin_id = transfer_dialog.comboBox.currentData()
            plugin_name = transfer_dialog.plugin_name_input.text()
            alias_name = transfer_dialog.alias_name_input.text()
            record = query_PluginMng(plugin_id=plugin_id)
            plugin_dir = "plugins_gui" if record.plugin_type == "Tool_Gui" else "plugins_headless"
            src_dir = util.build_full_path(f"pluginsmanager,{plugin_dir},plugins,{record.alias_name}")
            dst_dir = util.build_full_path(f"pluginsmanager,{plugin_dir},plugins,{alias_name}")
            util.copy_directory(src_dir, dst_dir)
            new_plugin_id = util.generate_random_id()
            dbfactory.copy_plugin_record(plugin_id, new_plugin_id, alias_name=alias_name, name=plugin_name, plugin_directory=alias_name)
            QMessageBox.information(self, '成功', f'插件拷贝成功。')
            self.refresh_toolbox_tool_plugin()
            # 在这里继续处理复制插件的逻辑
            # ...

    def remove_llm_plugin(self):
        # 创建对话框
        transfer_dialog = QDialog()
        transfer_dialog.setWindowTitle("选择")
        transfer_dialog.setMinimumWidth(500)

        # 创建主垂直布局
        main_layout = QVBoxLayout()

        # 创建表单布局
        form_layout = QFormLayout()

        # 创建第一个组合框并填充数据
        transfer_dialog.comboBox = QComboBox()
        transfer_dialog.comboBox.setEditable(False)
        records = query_PluginMng_All(plugin_type="LLM_Connector")

        for record in records:
            transfer_dialog.comboBox.addItem(record.name, record.plugin_id)

        form_layout.addRow("选择要删除的大模型插件：", transfer_dialog.comboBox)

        # 将表单布局添加到主布局
        main_layout.addLayout(form_layout)

        # 创建按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)

        # 创建确定和取消按钮
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")

        # 连接按钮事件
        ok_button.clicked.connect(transfer_dialog.accept)
        cancel_button.clicked.connect(transfer_dialog.reject)

        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        # 将按钮布局添加到主布局
        main_layout.addLayout(button_layout)

        # 设置主布局
        transfer_dialog.setLayout(main_layout)

        # 显示对话框并处理结果
        if transfer_dialog.exec():
            reply = QMessageBox.question(self, '确认',
                                         "您确认要删除吗?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            # 如果用户确认删除
            if reply == QMessageBox.Yes:
                plugin_id = transfer_dialog.comboBox.currentData()
                record = query_PluginMng(plugin_id=plugin_id)

                path = util.build_full_path(f"pluginsmanager,plugins,{record.alias_name}")

                delete_PluginMng(plugin_id=plugin_id)

                if os.path.exists(path):
                    try:
                        shutil.rmtree(path)  # 递归删除目录及其内容
                        QMessageBox.information(self, '成功', f'插件已被成功删除。')
                        self.refresh_toolbox_llm_plugin()
                    except Exception as e:
                        QMessageBox.critical(self, 'Error', f'Error occurred while deleting directory: {e}')
                else:
                    QMessageBox.warning(self, 'Warning', 'The specified directory does not exist.')

    def add_web_resource(self, type_str="LLM"):
        # 创建对话框
        dialog = QDialog()
        dialog.setWindowTitle("添加Web资源")
        dialog.setMinimumWidth(500)

        # 创建主垂直布局
        main_layout = QVBoxLayout()

        # 创建表单布局
        form_layout = QFormLayout()

        # 添加标题输入框
        title_input = QLineEdit()
        form_layout.addRow("标题:", title_input)

        # 添加URL输入框
        url_input = QLineEdit()
        form_layout.addRow("URL地址:", url_input)

        # 添加图片选择按钮
        image_button = QPushButton("选择图片")
        image_path = QLineEdit()
        image_path.setReadOnly(True)
        form_layout.addRow("图片:", image_button)
        form_layout.addRow("图片路径:", image_path)

        # 将表单布局添加到主布局
        main_layout.addLayout(form_layout)

        # 创建按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)

        # 创建确定和取消按钮
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")

        # 连接按钮事件
        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)

        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        # 将按钮布局添加到主布局
        main_layout.addLayout(button_layout)

        # 设置主布局
        dialog.setLayout(main_layout)

        # 图片选择按钮点击事件
        def select_image():
            file_dialog = QFileDialog()
            file_dialog.setFileMode(QFileDialog.ExistingFile)
            file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp)")
            if file_dialog.exec_():
                selected_files = file_dialog.selectedFiles()
                if selected_files:
                    image_path.setText(selected_files[0])

        image_button.clicked.connect(select_image)

        # 显示对话框并处理结果
        if dialog.exec_():
            # 获取用户输入

            title = title_input.text()
            name = title
            url = url_input.text()
            image_file = image_path.text()

            # 生成12位随机ID
            web_id = util.generate_random_id()

            # 处理图片文件
            if image_file:
                # 获取图片文件名
                filename = os.path.basename(image_file)
                # 目标路径
                target_dir = os.path.join(QDir.currentPath(), "images")
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)
                # 处理文件名冲突
                base_name, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(os.path.join(target_dir, filename)):
                    filename = f"{base_name}_{counter:03d}{ext}"
                    counter += 1
                # 复制文件
                target_path = os.path.join(target_dir, filename)
                # copy2(image_file, target_path)

                # 使用QPixmap和QPainter处理图片
                pixmap = QPixmap(image_file)
                if not pixmap.isNull():
                    # 计算居中截取的区域
                    width = pixmap.width()
                    height = pixmap.height()
                    size = min(width, height)  # 取较小的边作为截取区域的大小
                    x = (width - size) // 2
                    y = (height - size) // 2

                    # 截取图片的中心区域
                    cropped_pixmap = pixmap.copy(x, y, size, size)

                    # 缩放截取后的图片到80x80
                    scaled_pixmap = cropped_pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)

                    # 创建圆角遮罩
                    rounded_pixmap = QPixmap(80, 80)
                    rounded_pixmap.fill(Qt.transparent)

                    painter = QPainter(rounded_pixmap)
                    painter.setRenderHint(QPainter.Antialiasing)
                    painter.setRenderHint(QPainter.SmoothPixmapTransform)

                    # 绘制圆角矩形路径
                    path = QPainterPath()
                    path.addRoundedRect(0, 0, 80, 80, 20, 20)
                    painter.setClipPath(path)

                    # 绘制图片
                    painter.drawPixmap(0, 0, scaled_pixmap)
                    painter.end()

                    # 保存处理后的图片
                    rounded_pixmap.save(target_path)



            else:
                filename = ""

            # 调用保存函数
            add_web_mng(web_id, name, title, type_str, "", filename, url)
            self.refresh_toolbox_llm_web(type_str)

            # 提示用户操作成功
            QMessageBox.information(self, "成功", "Web资源已成功添加！")

    def create_install_plugin_local_button(self, text, image):
        button = QToolButton()
        button.setIcon(QIcon(image))
        button.setIconSize(QSize(50, 50))
        button.setCheckable(False)
        # button.clicked.connect(self.plugin_install_local)
        button.clicked.connect(self.show_tool_choice_dialog)

        # self.buttonGroup_Plugin_install.addButton(button)

        layout = QGridLayout()
        layout.addWidget(button, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def create_remove_plugin_local_button(self, text, image):
        button = QToolButton()
        button.setIcon(QIcon(image))
        button.setIconSize(QSize(50, 50))
        button.setCheckable(False)
        button.clicked.connect(self.remove_tool_plugin)

        # self.buttonGroup_Plugin_install.addButton(button)

        layout = QGridLayout()
        layout.addWidget(button, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def remove_tool_plugin(self):
        # 创建对话框
        transfer_dialog = QDialog()
        transfer_dialog.setWindowTitle("选择")
        transfer_dialog.setMinimumWidth(500)

        # 创建主垂直布局
        main_layout = QVBoxLayout()

        # 创建表单布局
        form_layout = QFormLayout()

        # 创建第一个组合框并填充数据
        transfer_dialog.comboBox = QComboBox()
        transfer_dialog.comboBox.setEditable(False)
        records = query_PluginMng_All_Tool()

        for record in records:
            transfer_dialog.comboBox.addItem(record.name, record.plugin_id)

        form_layout.addRow("选择要删除的插件：", transfer_dialog.comboBox)

        # 将表单布局添加到主布局
        main_layout.addLayout(form_layout)

        # 创建按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)

        # 创建确定和取消按钮
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")

        # 连接按钮事件
        ok_button.clicked.connect(transfer_dialog.accept)
        cancel_button.clicked.connect(transfer_dialog.reject)

        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        # 将按钮布局添加到主布局
        main_layout.addLayout(button_layout)

        # 设置主布局
        transfer_dialog.setLayout(main_layout)

        # 显示对话框并处理结果

        if transfer_dialog.exec():
            reply = QMessageBox.question(self, '确认',
                                         "您确认要删除吗?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            # 如果用户确认删除
            if reply == QMessageBox.Yes:
                plugin_id = transfer_dialog.comboBox.currentData()
                plugin_name = transfer_dialog.comboBox.currentText()
                record = query_PluginMng(plugin_id=plugin_id)
                plugin_dir = "plugins_gui" if record.plugin_type == "Tool_Gui" else "plugins_headless"
                path = util.build_full_path(f"pluginsmanager,{plugin_dir},plugins,{record.alias_name}")

                delete_PluginMng(plugin_id=plugin_id)

                if os.path.exists(path):
                    try:
                        shutil.rmtree(path)  # 递归删除目录及其内容
                        QMessageBox.information(self, '成功', f'插件已被成功删除。')

                        self.refresh_toolbox_tool_plugin()
                    except Exception as e:
                        QMessageBox.critical(self, 'Error', f'Error occurred while deleting directory: {e}')
                else:
                    QMessageBox.warning(self, 'Warning', 'The specified directory does not exist.')

    def create_new_note_button(self, text, km_cfg, image):
        button = QToolButton()
        button.setIcon(QIcon('images/task.png'))
        button.setIconSize(QSize(50, 50))
        button.setCheckable(False)
        button.clicked.connect(lambda: self.create_new_note_editor(km_cfg))

        layout = QGridLayout()
        layout.addWidget(button, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def create_new_note_editor(self, km_cfg):
        self.open_note_editor(km_cfg)

    def create_new_note_buttonbak(self, text, image):
        # agetnconfigdlg = FreezeTableDialog(self)
        agentcfgbutton = QToolButton()
        agentcfgbutton.setIcon(QIcon(image))
        agentcfgbutton.setIconSize(QSize(50, 50))
        agentcfgbutton.setCheckable(False)
        # agentcfgbutton.clicked.connect(lambda:self.createNewKM(kmrecord))

        # self.backgroundButtonGroup.addButton(agentcfgbutton)

        layout = QGridLayout()
        layout.addWidget(agentcfgbutton, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def create_new_km_button(self, text, kmrecord, image):
        # agetnconfigdlg = FreezeTableDialog(self)
        agentcfgbutton = QToolButton()
        agentcfgbutton.setIcon(QIcon(image))
        agentcfgbutton.setIconSize(QSize(50, 50))
        agentcfgbutton.setCheckable(False)
        agentcfgbutton.clicked.connect(lambda: self.createNewKM(kmrecord))

        # self.backgroundButtonGroup.addButton(agentcfgbutton)

        layout = QGridLayout()
        layout.addWidget(agentcfgbutton, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def createCellWidgetAgentMng(self, text, image):
        # agetnconfigdlg = FreezeTableDialog(self)
        agentcfgbutton = QToolButton()
        agentcfgbutton.setIcon(QIcon(image))
        agentcfgbutton.setIconSize(QSize(50, 50))
        agentcfgbutton.setCheckable(False)
        agentcfgbutton.clicked.connect(self.agentopendialog)

        # self.settingbuttonGroup.addButton(agentcfgbutton)

        layout = QGridLayout()
        layout.addWidget(agentcfgbutton, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def createCellWidgetAgentMultiMng(self, text, image):
        # agetnconfigdlg = FreezeTableDialog(self)
        agentcfgbutton = QToolButton()
        agentcfgbutton.setIcon(QIcon(image))
        agentcfgbutton.setIconSize(QSize(50, 50))
        agentcfgbutton.setCheckable(False)
        agentcfgbutton.clicked.connect(self.agentmultiopendialog)

        # self.settingbuttonGroup.addButton(agentcfgbutton)

        layout = QGridLayout()
        layout.addWidget(agentcfgbutton, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def createCellWidgetAgentMultiPrompt(self, text, image):
        # agetnconfigdlg = FreezeTableDialog(self)
        agentcfgbutton = QToolButton()
        agentcfgbutton.setIcon(QIcon(image))
        agentcfgbutton.setIconSize(QSize(50, 50))
        agentcfgbutton.setCheckable(False)
        # agentcfgbutton.clicked.connect(self.agentmultiopendialog)
        agentcfgbutton.clicked.connect(lambda: self.show_prompt_list(lt(
            "Prompt List", "提示词列表")))

        # self.settingbuttonGroup.addButton(agentcfgbutton)

        layout = QGridLayout()
        layout.addWidget(agentcfgbutton, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def createCellWidgetAgentMultiEval(self, text, image):
        # agetnconfigdlg = FreezeTableDialog(self)
        agentcfgbutton = QToolButton()
        agentcfgbutton.setIcon(QIcon(image))
        agentcfgbutton.setIconSize(QSize(50, 50))
        agentcfgbutton.setCheckable(False)
        # agentcfgbutton.clicked.connect(self.agentmultiopendialog)
        agentcfgbutton.clicked.connect(lambda: self.show_eval_list(lt(
            "Question List", "问题列表")))

        # self.settingbuttonGroup.addButton(agentcfgbutton)

        layout = QGridLayout()
        layout.addWidget(agentcfgbutton, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def createNewKM(self, kmrecord):
        filepath = self.setOpenFileName()
        filename = Path(filepath).name
        kmrecord = query_KMCfg(km_id=kmrecord.km_id)
        vector_type = kmrecord.vectortype
        config_param = kmrecord.config_param
        km_path = kmrecord.kmpath
        config = None

        if filename != "":
            if vector_type == "Pinecone":
                try:
                    # 将JSON字符串解析为Python字典
                    params = json.loads(config_param)

                    # 提取各个参数
                    config = {
                        "api_key": params.get("api_key"),
                        "cloud": params.get("cloud"),
                        "region": params.get("region"),
                        "index_name": params.get("index_name"),
                        "namespace": params.get("namespace"),
                        "top_k": params.get("top_k"),
                        "embed_model": params["embed"].get("model"),
                        "embed_field_map": params["embed"].get("field_map"),
                        "rerank_model": params["rerank"].get("model"),
                        "rerank_top_n": params["rerank"].get("top_n"),
                        "rerank_fields": params["rerank"].get("rank_fields"),
                        "fields": params.get("fields")
                    }


                except json.JSONDecodeError as e:
                    # 捕获JSON解析错误并打印错误信息
                    print("Error decoding JSON:", e)
                    return None
                except KeyError as e:
                    # 捕获访问未定义键的错误
                    print("Missing key in JSON data:", e)
                    return None



            # doc_directory = os.path.join("km",km_path,"doc")
            doc_directory = os.path.join(os.getcwd(), "km", km_path, "doc")
            if not os.path.exists(doc_directory):
                os.makedirs(doc_directory)
            shutil.copy(filepath, doc_directory)
            # persist_directory = os.path.join("km",km_path,"vector")
            persist_directory = os.path.join(os.getcwd(), "km", km_path, "vector")
            if not os.path.exists(persist_directory):
                os.makedirs(persist_directory)
            embedding_model_name = kmrecord.embeddingmodel
            # embedding_model_name = 'shibing624/text2vec-bge-large-chinese'
            if embedding_model_name.lower() == "openai":
                emb_type = "openai"
            else:
                emb_type = "other"
            chunk_size = kmrecord.textblocklength
            chunk_overlap = kmrecord.overlaplength

            km_id = kmrecord.km_id
            filename = filename
            filenum = 1

            if kmrecord.vectorization == 1 and kmrecord.stopvectorization == 1:
                # 如果可向量化且暂停了向量化则需要等待向量化
                waitvectorization = True
            else:
                waitvectorization = False

            record_id = add_KMData(km_id, filename, filenum, chunk_size, chunk_overlap, waitvectorization)
            print(filename)
            km_list = self.kmlist_list[kmrecord.km_id]
            km_list.addItem(filename, record_id)

            if kmrecord.vectorization == 1 and kmrecord.stopvectorization == 0:
                # 如果可向量化且没有暂停向量化则需要向量化

                self.thread = WorkerThread(filepath, persist_directory, embedding_model_name, emb_type, chunk_size,
                                           chunk_overlap,vector_type,config)
                self.thread.finished.connect(self.on_thread_finished)  # 连接信号
                self.thread.start()

    def on_thread_finished(self):
        """处理线程完成的信号"""
        print("线程已完成，准备清理")
        self.thread.quit()  # 请求线程退出
        self.thread.wait()  # 等待线程结束
        del self.thread  # 删除线程对象（如果需要）

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

    def setOpenFileNames(self):
        openFilesPath = ""
        openFileNamesLabel = ""
        options = QFileDialog.Options()
        native = True
        if not native:
            options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self,
                                                "QFileDialog.getOpenFileNames()", openFilesPath,
                                                "All Files (*);;Text Files (*.txt)", options=options)
        if files:
            openFilesPath = files[0]
            openFileNamesLabel = ("[%s]" % ', '.join(files))
        print(openFileNamesLabel)
        return openFileNamesLabel

    def open_agent_task_chat(self, agent):
        agent_cfg = agent.agent_cfg
        print("in createDialog")
        # if not self.dialog:
        # self.dialog = QDialog()
        if agent_cfg.user_id in self.agent_chat_window_list:
            dialog = self.agent_chat_window_list[agent_cfg.user_id]
        else:
            dialog = QWidget(self)  # 需要吧application作为父对象引入后面的流程中
            dialog.setWindowIcon(QIcon("images/mail.png"))

            msg = TaskPage(self, agent)
            msg.setObjectName('TaskPageObject')
            layout = QVBoxLayout(dialog)
            layout.addWidget(msg)
            dialog.setLayout(layout)
            # self.dialog.setWindowTitle(self.dialog.tr("Chat with ") + ai_chat_cfg.name)
            # self.dialog.show() #orgok
            # self.dialog.raise_() #orgok
            print("goingaddconver")
            self.stack_main_widget.addWidget(dialog)
            print("goingaddconver2")
            # self.mainwindow.stack_main_widget.setCurrentIndex(2) #setCurrentWidget
            self.agent_chat_window_list[agent_cfg.user_id] = dialog
        taskPage = dialog.findChild(TaskPage, "TaskPageObject")
        taskPage.new_task()
        taskPage.messageEdit.setFocus()
        self.stack_main_widget.setCurrentWidget(dialog)

    def open_note_editor(self, km_cfg, id=0):
        if km_cfg.km_id in self.km_note_window_list:
            note_widget = self.km_note_window_list[km_cfg.km_id]
        else:
            note_widget = QWidget(self)  # 需要吧application作为父对象引入后面的流程中
            note_widget.setWindowIcon(QIcon("images/mail.png"))
            layout = QVBoxLayout(note_widget)

            editor = NoteEditor(self)

            editor.setObjectName('NoteEditorObject')

            editor.show()

            layout.addWidget(editor)
            note_widget.setLayout(layout)
            self.km_note_window_list[km_cfg.km_id] = note_widget
        self.current_note_widget = note_widget
        self.stack_main_widget.addWidget(self.current_note_widget)

        self.stack_main_widget.setCurrentWidget(self.current_note_widget)

        note_editor = note_widget.findChild(QMainWindow, "NoteEditorObject")

        note_editor.record_id = id
        note_editor.km_id = km_cfg.km_id
        note_editor.km_cfg = km_cfg
        note_editor.loadFile()

    def open_exist_agent_task_chat(self, agent):
        agent_cfg = agent.agent_cfg
        print("in createDialog")
        print("agent.agent_cfg.user_id:", agent.agent_cfg.user_id)
        # if not self.dialog:
        # self.dialog = QDialog()
        if agent_cfg.user_id in self.agent_chat_window_list:
            print("goingaddconver1111")
            dialog = self.agent_chat_window_list[agent_cfg.user_id]
        else:
            print("goingaddconver11112222")
            dialog = QWidget(self)  # 需要吧application作为父对象引入后面的流程中
            dialog.setWindowIcon(QIcon("images/mail.png"))
            print("goingaddconver11113333")
            msg = TaskPage(self, agent)
            print("goingaddconver11114444")
            msg.setObjectName('TaskPageObject')
            layout = QVBoxLayout(dialog)
            layout.addWidget(msg)
            dialog.setLayout(layout)
            # self.dialog.setWindowTitle(self.dialog.tr("Chat with ") + ai_chat_cfg.name)
            # self.dialog.show() #orgok
            # self.dialog.raise_() #orgok
            print("goingaddconver")
            self.stack_main_widget.addWidget(dialog)
            print("goingaddconver2")
            # self.mainwindow.stack_main_widget.setCurrentIndex(2) #setCurrentWidget
            self.agent_chat_window_list[agent_cfg.user_id] = dialog
            taskPage = dialog.findChild(TaskPage, "TaskPageObject")
            taskPage.new_task()
        self.stack_main_widget.setCurrentWidget(dialog)

    def open_multi_agent_task_chat(self, agentcfg):
        if agentcfg.group_id in self.multi_agent_chat_window_list:
            dialog = self.multi_agent_chat_window_list[agentcfg.group_id]
        else:
            dialog = QWidget(self)  # 需要吧application作为父对象引入后面的流程中
            dialog.setWindowIcon(QIcon("images/mail.png"))

            msg = TaskPageGroup(self, agentcfg)
            msg.setObjectName('TaskPageGroupObject')
            layout = QVBoxLayout(dialog)
            layout.addWidget(msg)
            dialog.setLayout(layout)
            self.stack_main_widget.addWidget(dialog)
            self.multi_agent_chat_window_list[agentcfg.group_id] = dialog
        taskPage = dialog.findChild(TaskPageGroup, "TaskPageGroupObject")
        taskPage.new_task()
        self.stack_main_widget.setCurrentWidget(dialog)

    def plugin_install_dialog(self, plugin_data):
        plugin_name = plugin_data["name"]
        plugin_version = plugin_data["version"]
        plugin_company = plugin_data["company"]
        plugin_description = plugin_data["description"]
        plugin_url = plugin_data["url"]
        message_box = QMessageBox()
        message_box.setWindowTitle("您是否要安装该插件？")
        message_box.setText(
            "名称：" + plugin_name + ":" + plugin_version + "\n" + "公司：" + plugin_company + "\n" + "说明：" + plugin_description)

        message_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        message_box.setDefaultButton(QMessageBox.Ok)

        # 显示消息框，并获取用户的响应
        user_response = message_box.exec()

        # 根据用户的响应进行处理
        if user_response == QMessageBox.Ok:
            print("User clicked OK")
            file_name = os.path.basename(plugin_url)
            file__without_extension = os.path.splitext(file_name)[0]
            file_extension = os.path.splitext(file_name)[1]
            file_path = os.path.join(Path(__file__).resolve().parent.parent, "download", file_name)

            if os.path.exists(file_path):
                current_timestamp = str(time.time()).replace('.', '')
                file_name = file__without_extension + current_timestamp + file_extension
                file_path = os.path.join(Path(__file__).resolve().parent.parent, "download", file_name)
            self.download_file(plugin_url, file_path)
            self.plugin_install(file_path)
        else:
            print("User clicked Cancel")

    def plugin_install(self, zip_file_path):
        file__without_extension = os.path.splitext(os.path.basename(zip_file_path))[0]
        extract_to_path = os.path.join(Path(__file__).resolve().parent.parent, "download", "temp",
                                       file__without_extension)
        self.unzip_file(zip_file_path, extract_to_path)
        print("install.....")
        message_box = QMessageBox()
        message_box.setWindowTitle("提示")
        message_box.setText("安装成功!")

        message_box.setStandardButtons(QMessageBox.Ok)
        # message_box.setDefaultButton(QMessageBox.Ok)
        user_response = message_box.exec()

    def createTaskGroup(self, agent):
        print("in createDialogGroup")
        # if not self.dialog:
        # self.dialog = QDialog()
        if agent.group_id in self.muti_agent_chat_window_list:
            dialog = self.muti_agent_chat_window_list[agent.group_id]
        else:
            dialog = QWidget(self)  # 需要吧application作为父对象引入后面的流程中
            dialog.setWindowIcon(QIcon("images/mail.png"))

            msg = TaskPageGroup(dialog, None, agent.group_id, agent.name)
            layout = QVBoxLayout(dialog)
            layout.addWidget(msg)
            dialog.setLayout(layout)
            # self.dialog.setWindowTitle(self.dialog.tr("Chat with ") + "wangwang")
            # self.dialog.show() #orgok
            # self.dialog.raise_() #orgok
            print("goingaddconver")
            self.stack_main_widget.addWidget(dialog)
            print("goingaddconver2")
            # self.mainwindow.stack_main_widget.setCurrentIndex(2) #setCurrentWidget
            self.muti_agent_chat_window_list[agent.group_id] = dialog
        self.stack_main_widget.setCurrentWidget(dialog)
        print("goingaddconver3")

    def open_plugin_market(self):
        self.app_home.page().load(QUrl("http://www.ai-sns.org/index_plugin.html"))

    def open_plugin_publish(self):
        self.app_home.page().load(QUrl("http://www.ai-sns.org/index_plugin.html"))

    def download_plugin_button(self, text):
        button = QToolButton()
        button.setIcon(QIcon('images/download.png'))
        button.setIconSize(QSize(50, 50))
        button.setCheckable(True)
        button.clicked.connect(self.open_plugin_market)

        self.buttonGroup_Plugin_install.addButton(button, 0)  # to toggle button status改变按钮点击的状态

        layout = QGridLayout()
        layout.addWidget(button, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def publish_plugin_button(self, text):
        button = QToolButton()
        button.setIcon(QIcon('images/publish.png'))
        button.setIconSize(QSize(50, 50))
        button.setCheckable(True)
        button.clicked.connect(self.open_plugin_publish)

        self.buttonGroup_Plugin_install.addButton(button, 1)  # to toggle button status改变按钮点击的状态

        layout = QGridLayout()
        layout.addWidget(button, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def create_new_task_button(self, text, agent, diagramType):
        button = QToolButton()
        button.setIcon(QIcon('images/task.png'))
        button.setIconSize(QSize(50, 50))
        button.setCheckable(False)

        button.clicked.connect(lambda: self.create_new_task_chat(agent))
        # button.setShortcut(QtGui.QKeySequence(Qt.KeyboardModifier.ControlModifier | Qt.Key.Key_N))
        button.setShortcut(QtGui.QKeySequence(Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier | Qt.Key.Key_N))

        # self.buttonGroup.addButton(button, diagramType)  # to toggle button status改变按钮点击的状态

        layout = QGridLayout()
        layout.addWidget(button, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def create_new_task_chat(self, agent):
        agent_cfg = agent.agent_cfg
        taskList = self.tasklist_list[agent_cfg.user_id]
        taskList.deselect_all_items()
        self.open_agent_task_chat(agent)

    def create_new_group_task_button(self, text, agentcfg, diagramType):
        # item = DiagramItem(diagramType, self.itemMenu)
        # icon = QIcon(item.image())

        button = QToolButton()
        button.setIcon(QIcon('images/task.png'))
        button.setIconSize(QSize(50, 50))
        button.setCheckable(False)
        button.clicked.connect(lambda: self.open_multi_agent_task_chat(agentcfg))

        # self.buttonGroup.addButton(button, diagramType)

        layout = QGridLayout()
        layout.addWidget(button, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def createCellWidget(self, text, diagramType):
        # item = DiagramItem(diagramType, self.itemMenu)
        # icon = QIcon(item.image())
        agetnconfigdlg = AgentConfigDialog(self)
        agentcfgbutton = QToolButton()
        agentcfgbutton.setIcon(QIcon('images/moresetting.png'))
        agentcfgbutton.setIconSize(QSize(50, 50))
        agentcfgbutton.setCheckable(False)
        agentcfgbutton.clicked.connect(agetnconfigdlg.exec)

        # self.buttonGroup.addButton(agentcfgbutton, diagramType)

        layout = QGridLayout()
        layout.addWidget(agentcfgbutton, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def createCellWidgetLogMng(self, text, diagramType):
        agentcfgbutton = QToolButton()
        agentcfgbutton.setIcon(QIcon('images/moresetting.png'))
        agentcfgbutton.setIconSize(QSize(50, 50))
        agentcfgbutton.setCheckable(False)
        agentcfgbutton.clicked.connect(self.logopendialog)

        # self.buttonGroup.addButton(agentcfgbutton, diagramType)

        layout = QGridLayout()
        layout.addWidget(agentcfgbutton, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def createCellWidgetGeneralCfg(self, text, diagramType):
        # item = DiagramItem(diagramType, self.itemMenu)
        # icon = QIcon(item.image())
        agetnconfigdlg = ConfigDialog(self)
        agentcfgbutton = QToolButton()
        agentcfgbutton.setIcon(QIcon('images/moresetting.png'))
        agentcfgbutton.setIconSize(QSize(50, 50))
        agentcfgbutton.setCheckable(False)
        agentcfgbutton.clicked.connect(agetnconfigdlg.exec)

        # self.buttonGroup.addButton(agentcfgbutton, diagramType)

        layout = QGridLayout()
        layout.addWidget(agentcfgbutton, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget
    def createCellWidgetHelp(self, text, diagramType):
        # item = DiagramItem(diagramType, self.itemMenu)
        # icon = QIcon(item.image())

        agentcfgbutton = QToolButton()
        agentcfgbutton.setIcon(QIcon('images/help.png'))
        agentcfgbutton.setIconSize(QSize(50, 50))
        agentcfgbutton.setCheckable(False)
        agentcfgbutton.clicked.connect(lambda: webbrowser.open("http://www.ai-sns.org"))


        # self.buttonGroup.addButton(agentcfgbutton, diagramType)

        layout = QGridLayout()
        layout.addWidget(agentcfgbutton, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def open_wizard_cfg_dialog(self):
        agentconfigdlg = WizardConfigDialog(self)
        agentconfigdlg.exec()

    def createCellWidgetInitCfg(self, text, diagramType):
        # item = DiagramItem(diagramType, self.itemMenu)
        # icon = QIcon(item.image())
        # agetnconfigdlg = ConfigDialog(self)
        # agetnconfigdlg = WizardConfigDialog(self)
        agentcfgbutton = QToolButton()
        agentcfgbutton.setIcon(QIcon('images/wizard.png'))
        agentcfgbutton.setIconSize(QSize(50, 50))
        agentcfgbutton.setCheckable(False)
        agentcfgbutton.clicked.connect(lambda: self.open_wizard_cfg_dialog())

        # self.buttonGroup.addButton(agentcfgbutton, diagramType)

        layout = QGridLayout()
        layout.addWidget(agentcfgbutton, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget




    def create_human_cfg_button(self, text, agent, diagramType):
        agentconfigdlg = HumanChatConfigDialog(self, agent)
        self.human_chat_cfg_dialog_list[agent.user_id] = agentconfigdlg
        agentcfgbutton = QToolButton()
        agentcfgbutton.setIcon(QIcon('images/moresetting.png'))
        agentcfgbutton.setIconSize(QSize(50, 50))
        agentcfgbutton.setCheckable(False)
        agentconfigdlg.configured.connect(self.on_configured_human)
        agentcfgbutton.clicked.connect(agentconfigdlg.exec)

        # self.buttonGroup.addButton(agentcfgbutton, diagramType)

        layout = QGridLayout()
        layout.addWidget(agentcfgbutton, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def create_km(self):
        print("create agent")
        agetnconfigdlg = KmConfigDialog(self)
        agetnconfigdlg.exec()

    def createCellWidgetKMNew(self, text, image):
        # item = DiagramItem(diagramType, self.itemMenu)
        # icon = QIcon(item.image())

        agentcfgbutton = QToolButton()
        agentcfgbutton.setIcon(QIcon(image))
        agentcfgbutton.setIconSize(QSize(50, 50))
        agentcfgbutton.setCheckable(False)
        agentcfgbutton.clicked.connect(self.create_km)

        # self.buttonGroup.addButton(agentcfgbutton)

        layout = QGridLayout()
        layout.addWidget(agentcfgbutton, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def create_note_cfg_button(self, text, diagramType):
        # pass
        kmrecord = query_KMCfg(kmtype="1")
        agentconfigdlg = KmConfigDialog(self, kmrecord)
        self.km_cfg_dialog_list[kmrecord.km_id] = agentconfigdlg
        agentcfgbutton = QToolButton()
        agentcfgbutton.setIcon(QIcon('images/moresetting.png'))
        agentcfgbutton.setIconSize(QSize(50, 50))
        agentcfgbutton.setCheckable(False)
        agentcfgbutton.clicked.connect(agentconfigdlg.exec)

        # self.buttonGroup.addButton(agentcfgbutton, diagramType)

        layout = QGridLayout()
        layout.addWidget(agentcfgbutton, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def create_km_cfg_button(self, text, kmrecord, diagramType):
        agentconfigdlg = KmConfigDialog(self, kmrecord)
        self.km_cfg_dialog_list[kmrecord.km_id] = agentconfigdlg
        agentcfgbutton = QToolButton()
        agentcfgbutton.setIcon(QIcon('images/moresetting.png'))
        agentcfgbutton.setIconSize(QSize(50, 50))
        agentcfgbutton.setCheckable(False)
        agentcfgbutton.clicked.connect(agentconfigdlg.exec)

        # self.buttonGroup.addButton(agentcfgbutton, diagramType)

        layout = QGridLayout()
        layout.addWidget(agentcfgbutton, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def open_ai_chat_cfg_dialog_earth(self, agent=None):
        agent = query_AiChatCfg_map()
        agentconfigdlg = AiMapConfigDialog(self, agent)
        self.ai_chat_cfg_dialog_list[agent.user_id] = agentconfigdlg
        agentconfigdlg.configured.connect(self.on_configured_ai_map)
        agentconfigdlg.exec()

    def create_ai_cfg_button_earth(self, text, agent, diagramType):
        # agentconfigdlg = AiMapConfigDialog(self, agent)
        # self.ai_chat_cfg_dialog_list[agent.user_id] = agentconfigdlg

        # 创建按钮并添加图标
        agentcfgbutton = QPushButton(lt("Setting", "设置"))
        agentcfgbutton.setIcon(QIcon('images/setting.png'))  # 添加配置管理图标

        # agentconfigdlg.configured.connect(self.on_configured_ai_map)
        agentcfgbutton.clicked.connect(lambda: self.open_ai_chat_cfg_dialog_earth(agent))

        agentcfgbutton.setVisible(False)
        # self.buttonGroup.addButton(agentcfgbutton, diagramType)

        return agentcfgbutton

    def open_new_map_task(self):
        ai_map_task_dialog = AiMapTaskDialog(self)
        ai_map_task_dialog.configured.connect(self.on_configured_ai_map)
        ai_map_task_dialog.exec()

    def create_ai_task_button_earth(self, text, agent, diagramType):
        # 创建按钮并添加图标
        task_button = QPushButton(lt("New Task", "指派任务"))
        task_button.setIcon(QIcon('images/mission.png'))  # 添加配置管理图标

        task_button.clicked.connect(self.open_new_map_task)

        task_button.setVisible(False)
        # self.buttonGroup.addButton(task_button, diagramType)

        return task_button


    def open_ai_chat_cfg_dialog(self, agent):
        agent = query_AiChatCfg_common()
        agentconfigdlg = AiChatConfigDialog(self, agent)
        self.ai_chat_cfg_dialog_list[agent.user_id] = agentconfigdlg
        agentconfigdlg.configured.connect(self.on_configured_ai)
        agentconfigdlg.exec()

    def create_ai_cfg_button(self, text, agent, diagramType):
        # agentconfigdlg = AiChatConfigDialog(self, agent)
        # self.ai_chat_cfg_dialog_list[agent.user_id] = agentconfigdlg
        agentcfgbutton = QToolButton()
        agentcfgbutton.setIcon(QIcon('images/moresetting.png'))
        agentcfgbutton.setIconSize(QSize(50, 50))
        agentcfgbutton.setCheckable(False)
        # agentconfigdlg.configured.connect(self.on_configured_ai)
        # agentcfgbutton.clicked.connect(agentconfigdlg.exec)
        agentcfgbutton.clicked.connect(lambda: self.open_ai_chat_cfg_dialog(agent))

        # self.buttonGroup.addButton(agentcfgbutton, diagramType)

        layout = QGridLayout()
        layout.addWidget(agentcfgbutton, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def createCellWidget(self, text, diagramType):
        # item = DiagramItem(diagramType, self.itemMenu)
        # icon = QIcon(item.image())
        agetnconfigdlg = AgentConfigDialog(self)
        agentcfgbutton = QToolButton()
        agentcfgbutton.setIcon(QIcon('images/moresetting.png'))
        agentcfgbutton.setIconSize(QSize(50, 50))
        agentcfgbutton.setCheckable(False)
        agentcfgbutton.clicked.connect(agetnconfigdlg.exec)

        # self.buttonGroup.addButton(agentcfgbutton, diagramType)

        layout = QGridLayout()
        layout.addWidget(agentcfgbutton, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def open_multi_agent_cfg_dialog(self, agent):
        group_id = agent.group_id
        agent_group_cfg = query_MutiAgentCfg(group_id=group_id)
        agentconfigdlg = AgentMutiConfigDialog(self, agent_group_cfg)
        agentconfigdlg.exec()

    def create_muti_agent_cfg_button(self, text, agent, diagramType):
        # item = DiagramItem(diagramType, self.itemMenu)
        # icon = QIcon(item.image())
        # agentconfigdlg = AgentMutiConfigDialog(self, agent)
        agentcfgbutton = QToolButton()
        agentcfgbutton.setIcon(QIcon('images/moresetting.png'))
        agentcfgbutton.setIconSize(QSize(50, 50))
        agentcfgbutton.setCheckable(False)
        agentcfgbutton.clicked.connect(lambda: self.open_multi_agent_cfg_dialog(agent))

        # self.buttonGroup.addButton(agentcfgbutton, diagramType)

        layout = QGridLayout()
        layout.addWidget(agentcfgbutton, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def open_agent_cfg_dialog(self, agent):
        user_id = agent.agent_cfg.user_id
        agent_cfg = query_AgentCfg(user_id=user_id)
        agent = Agent(agent_cfg)
        agentconfigdlg = AgentConfigDialog(self, agent)

        self.agent_cfg_dialog_list[agent_cfg.user_id] = agentconfigdlg
        agentconfigdlg.exec()

    def create_agent_cfg_button(self, text, agent, diagramType):
        # item = DiagramItem(diagramType, self.itemMenu)
        # icon = QIcon(item.image())
        agent_cfg = agent.agent_cfg
        # agentconfigdlg = AgentConfigDialog(self, agent)
        # self.agent_cfg_dialog_list[agent_cfg.user_id] = agentconfigdlg
        agentcfgbutton = QToolButton()
        agentcfgbutton.setIcon(QIcon('images/moresetting.png'))
        agentcfgbutton.setIconSize(QSize(50, 50))
        agentcfgbutton.setCheckable(False)
        agentcfgbutton.clicked.connect(lambda: self.open_agent_cfg_dialog(agent))

        # self.buttonGroup.addButton(agentcfgbutton, diagramType)

        layout = QGridLayout()
        layout.addWidget(agentcfgbutton, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def create_agent(self):
        print("create agent")
        agetnconfigdlg = AgentConfigDialog(self)
        agetnconfigdlg.exec()

    def createCellWidgetAgentNew(self, text, image):
        # item = DiagramItem(diagramType, self.itemMenu)
        # icon = QIcon(item.image())

        agentcfgbutton = QToolButton()
        agentcfgbutton.setIcon(QIcon(image))
        agentcfgbutton.setIconSize(QSize(50, 50))
        agentcfgbutton.setCheckable(False)
        agentcfgbutton.clicked.connect(self.create_agent)

        # self.settingbuttonGroup.addButton(agentcfgbutton)

        layout = QGridLayout()
        layout.addWidget(agentcfgbutton, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def create_multi_agent(self):
        print("create agent")
        agetnconfigdlg = AgentMutiConfigDialog(self)
        agetnconfigdlg.exec()

    def createCellWidgetAgentMultiNew(self, text, image):
        # item = DiagramItem(diagramType, self.itemMenu)
        # icon = QIcon(item.image())

        agentcfgbutton = QToolButton()
        agentcfgbutton.setIcon(QIcon(image))
        agentcfgbutton.setIconSize(QSize(50, 50))
        agentcfgbutton.setCheckable(False)
        agentcfgbutton.clicked.connect(self.create_multi_agent)

        # self.settingbuttonGroup.addButton(agentcfgbutton)

        layout = QGridLayout()
        layout.addWidget(agentcfgbutton, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def createCellWidgetAiChatNew(self, text, image):
        # item = DiagramItem(diagramType, self.itemMenu)
        # icon = QIcon(item.image())
        agentconfigdlg = AiChatConfigDialog(self)
        agentcfgbutton = QToolButton()
        agentcfgbutton.setIcon(QIcon(image))
        agentcfgbutton.setIconSize(QSize(50, 50))
        agentcfgbutton.setCheckable(False)
        agentconfigdlg.configured.connect(self.on_configured_ai)
        agentcfgbutton.clicked.connect(agentconfigdlg.exec)

        # self.buttonGroup.addButton(agentcfgbutton)

        layout = QGridLayout()
        layout.addWidget(agentcfgbutton, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def createCellWidgetHumanChatNew(self, text, image):
        # item = DiagramItem(diagramType, self.itemMenu)
        # icon = QIcon(item.image())
        agetnconfigdlg = HumanChatConfigDialog(self)
        agentcfgbutton = QToolButton()
        agentcfgbutton.setIcon(QIcon(image))
        agentcfgbutton.setIconSize(QSize(50, 50))
        agentcfgbutton.setCheckable(False)
        agentcfgbutton.clicked.connect(agetnconfigdlg.exec)

        # self.buttonGroup.addButton(agentcfgbutton)

        layout = QGridLayout()
        layout.addWidget(agentcfgbutton, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

        # for plugin

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

    def open_website(self, url="http://www.ai-sns.org", type_str="LLM"):
        # 检测当前操作系统
        is_windows = platform.system() == 'Windows'

        # 根据操作系统判断使用的修饰符
        if is_windows and QApplication.keyboardModifiers() == Qt.KeyboardModifier.ControlModifier:
            # Windows下的Ctrl键被按下
            webbrowser.open(url)
            return
        elif not is_windows and QApplication.keyboardModifiers() == Qt.KeyboardModifier.MetaModifier:
            # 其他系统（如 macOS）下的Command键被按下
            webbrowser.open(url)
            return

        if type_str == "LLM":
            if not self.web_llm_home:
                self.web_llm_home = QWebEngineView()
            self.web_llm_home.setZoomFactor(0.75)

            if not self.web_llm_home_frame:
                self.web_llm_home_frame = QtWidgets.QFrame(self)
                self.web_llm_home_frame.setContentsMargins(0, 0, 0, 0)
                self.web_llm_home_frame.setStyleSheet(
                    "QFrame { border: 1px solid #c0c0c0;margin:0,0,0,0;padding:0,0,0,0;border-radius: 8px;}")
                web_llm_home_frame_layout = QtWidgets.QVBoxLayout(self.web_llm_home_frame)
                web_llm_home_frame_layout.addWidget(self.web_llm_home)

                self.stack_main_widget.addWidget(self.web_llm_home_frame)

            self.stack_main_widget.setCurrentWidget(self.web_llm_home_frame)
            self.web_llm_home.page().load(QUrl(url))
        else:
            if not self.web_tools_home:
                self.web_tools_home = QWebEngineView()
                self.web_tools_home.page().profile().downloadRequested.connect(self.handle_download_requested)
            self.web_tools_home.setZoomFactor(0.75)
            if not self.web_tools_home_frame:
                self.web_tools_home_frame = QtWidgets.QFrame(self)
                self.web_tools_home_frame.setContentsMargins(0, 0, 0, 0)
                self.web_tools_home_frame.setStyleSheet(
                    "QFrame { border: 1px solid #c0c0c0;margin:0,0,0,0;padding:0,0,0,0;border-radius: 8px;}")
                web_tools_home_frame_layout = QtWidgets.QVBoxLayout(self.web_tools_home_frame)
                web_tools_home_frame_layout.addWidget(self.web_tools_home)

                self.stack_main_widget.addWidget(self.web_tools_home_frame)

            self.stack_main_widget.setCurrentWidget(self.web_tools_home_frame)
            self.web_tools_home.page().load(QUrl(url))

    def handle_download_requested(self, download: QWebEngineDownloadRequest):
        """
        处理下载请求。

        Args:
            download: QWebEngineDownloadItem 对象，包含下载信息。
        """
        # 弹出文件对话框让用户选择保存路径
        download_path, _ = QFileDialog.getSaveFileName(self, "Save File", download.downloadFileName())

        if download_path:
            # 提取目录路径和文件名
            download_directory = os.path.dirname(download_path)
            download_filename = os.path.basename(download_path)

            # 设置下载目录和文件名
            download.setDownloadDirectory(download_directory)
            download.setDownloadFileName(download_filename)
            download.accept()  # 接受下载请求，开始下载

            print(f"Downloading {download_filename} to {download_directory}")

            # 连接下载完成信号
            download.isFinishedChanged.connect(lambda: self.on_download_finished(download))

    def on_download_finished(self, download):
        """
        下载完成后的处理。

        Args:
            download: QWebEngineDownloadItem 对象，包含下载信息。
        """
        if download.state() == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
            print(f"Download completed: {download.downloadFileName()} saved to {download.downloadDirectory()}")
        elif download.state() == QWebEngineDownloadRequest.DownloadState.DownloadInterrupted:
            print(f"Download interrupted: {download.interruptReasonString()}")

    def show_plugin_cfg(self, plugin_full_name):
        print("opening baichuan connector...")
        __cli_args = self.__init_cli().parse_args()
        print("cjrok")
        print(__cli_args.log)
        print("cjrok2")
        # delegate = self.__init_app({
        #     'log_level': __cli_args.log,
        #     'directory': __cli_args.directory
        # })

        delegate = global_plugin_list[plugin_full_name]

        if plugin_full_name == "函数管理器":
            content = delegate.invoke(command=["open_config_dialog"], app=self)
        else:
            content = delegate.invoke(command=["open_config_dialog"])

    def show_plugin_tool_cfg(self, record):
        plugin = load_plugin_tool(self, record)
        plugin.open_config_dialog()

    def show_workflow_list(self, plugin_full_name):
        if not self.workflow_list_shown:
            if not self.workflow_widget:
                workflow_widget = WorkFlowManager()
                workflow_widget.setObjectName("workflowmanager")
                self.workflow_widget = workflow_widget
                self.stack_main_widget.addWidget(self.workflow_widget)
            self.stack_main_widget.setCurrentWidget(self.workflow_widget)

            self.workflow_list_shown = True
            self.schedule_list_shown = False
        else:
            self.workflow_list_shown = False
            self.stack_main_widget.setCurrentWidget(self.app_home_frame)
            self.app_home.page().load(QUrl("http://www.ai-sns.org/index_humanchat.html"))

    def show_task_schedule(self):
        if not self.schedule_list_shown:
            if not self.task_schedule_widget:
                task_schedule_widget = TaskSchedule()
                task_schedule_widget.setObjectName("taskschedule")
                self.task_schedule_widget = task_schedule_widget
                self.stack_main_widget.addWidget(self.task_schedule_widget)
            self.stack_main_widget.setCurrentWidget(self.task_schedule_widget)

            self.schedule_list_shown = True
            self.workflow_list_shown = False
        else:
            self.schedule_list_shown = False
            self.stack_main_widget.setCurrentWidget(self.app_home_frame)
            self.app_home.page().load(QUrl("http://www.ai-sns.org/index_humanchat.html"))

    def show_prompt_list(self, plugin_full_name):
        prompt_dialog = PromptManager(self)
        prompt_dialog.setObjectName("promptmanager")
        self.stack_main_widget.addWidget(prompt_dialog)
        self.stack_main_widget.setCurrentWidget(prompt_dialog)

    def show_eval_list(self, plugin_full_name):
        eval_dialog = ModelEvaluationDialog()
        eval_dialog.setObjectName("evalmanager")
        self.stack_main_widget.addWidget(eval_dialog)
        self.stack_main_widget.setCurrentWidget(eval_dialog)

    def show_function_list(self, type_str):
        if type_str == "1":
            if not self.function_list_shown:
                if not self.function_widget:
                    function_widget = FunctionManager(type_str)
                    function_widget.setObjectName("functionmanager")
                    self.function_widget = function_widget
                    self.stack_main_widget.addWidget(self.function_widget)
                self.stack_main_widget.setCurrentWidget(self.function_widget)

                self.function_list_shown = True
                self.function_list_draft_shown = False
            else:
                self.function_list_shown = False
                self.stack_main_widget.setCurrentWidget(self.app_home_frame)
                self.app_home.page().load(QUrl("http://www.ai-sns.org/index_plugin.html"))
        else:
            if not self.function_list_draft_shown:
                if not self.function_widget_draft:
                    function_widget_draft = FunctionManager(type_str)
                    function_widget_draft.setObjectName("functionmanagerdraft")
                    self.function_widget_draft = function_widget_draft
                    self.stack_main_widget.addWidget(self.function_widget_draft)
                self.stack_main_widget.setCurrentWidget(self.function_widget_draft)

                self.function_list_draft_shown = True
                self.function_list_shown = False
            else:
                self.function_list_draft_shown = False
                self.stack_main_widget.setCurrentWidget(self.app_home_frame)
                self.app_home.page().load(QUrl("http://www.ai-sns.org/index_plugin.html"))

    def show_mcp_list(self, type_str):
        if type_str == "1":
            if not self.mcp_list_shown:
                if not self.mcp_widget:
                    mcp_widget = McpManager(type_str)
                    mcp_widget.setObjectName("mcpmanager")
                    self.mcp_widget = mcp_widget
                    self.stack_main_widget.addWidget(self.mcp_widget)
                self.stack_main_widget.setCurrentWidget(self.mcp_widget)

                self.mcp_list_shown = True
                self.mcp_list_draft_shown = False
            else:
                self.mcp_list_shown = False
                self.stack_main_widget.setCurrentWidget(self.app_home_frame)
                self.app_home.page().load(QUrl("http://www.ai-sns.org/index_plugin.html"))
        else:
            if not self.mcp_list_draft_shown:
                if not self.mcp_widget_draft:
                    mcp_widget_draft = McpManager(type_str)
                    mcp_widget_draft.setObjectName("mcpmanagerdraft")
                    self.mcp_widget_draft = mcp_widget_draft
                    self.stack_main_widget.addWidget(self.mcp_widget_draft)
                self.stack_main_widget.setCurrentWidget(self.mcp_widget_draft)

                self.mcp_list_draft_shown = True
                self.mcp_list_shown = False
            else:
                self.mcp_list_draft_shown = False
                self.stack_main_widget.setCurrentWidget(self.app_home_frame)
                self.app_home.page().load(QUrl("http://www.ai-sns.org/index_plugin.html"))


    def show_skill_list(self, type_str):
        if type_str == "1":
            if not self.skill_list_shown:
                if not self.skill_widget:
                    skill_widget = SkillManager(type_str, self)
                    skill_widget.setObjectName("skillmanager")
                    self.skill_widget = skill_widget
                    self.stack_main_widget.addWidget(self.skill_widget)
                self.stack_main_widget.setCurrentWidget(self.skill_widget)

                self.skill_list_shown = True
                self.skill_list_draft_shown = False
            else:
                self.skill_list_shown = False
                self.stack_main_widget.setCurrentWidget(self.app_home_frame)
                self.app_home.page().load(QUrl("http://www.ai-sns.org/index_plugin.html"))
        else:
            if not self.skill_list_draft_shown:
                if not self.skill_widget_draft:
                    skill_widget_draft = SkillManager(type_str, self)
                    skill_widget_draft.setObjectName("skillmanagerdraft")
                    self.skill_widget_draft = skill_widget_draft
                    self.stack_main_widget.addWidget(self.skill_widget_draft)
                self.stack_main_widget.setCurrentWidget(self.skill_widget_draft)

                self.skill_list_draft_shown = True
                self.skill_list_shown = False
            else:
                self.skill_list_draft_shown = False
                self.stack_main_widget.setCurrentWidget(self.app_home_frame)
                self.app_home.page().load(QUrl("http://www.ai-sns.org/index_plugin.html"))

    def create_plugin_skill_button(self, type_str, diagramType):
        button = QToolButton()
        button.setIcon(QIcon('images/plugin.png'))
        button.setIconSize(QSize(50, 50))
        button.setCheckable(True)
        if type_str == "1":
            button_label = lt("Pulished", "已发布")
        else:
            button_label = lt("Draft", "未发布")

        button.clicked.connect(lambda: self.show_skill_list(type_str))

        self.buttonGroup_Plugin_skill.addButton(button, diagramType)
        # self.buttonGroup.addButton(button, diagramType)

        layout = QGridLayout()
        layout.addWidget(button, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(button_label), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def skill_search(self, keyword, type_str="0"):
        # type_str:"0","1","2"
        print("keyword", keyword)

        if keyword == "$$$cjrok":
            type_str = "2"
        print(keyword)
        print("type_str", type_str)
        skill_dialog = SkillManager(type_str, self)
        skill_dialog.setObjectName("skillmanager")
        self.stack_main_widget.addWidget(skill_dialog)
        self.stack_main_widget.setCurrentWidget(skill_dialog)

    def create_plugin_function_button(self, type_str, diagramType):
        button = QToolButton()
        button.setIcon(QIcon('images/plugin.png'))
        button.setIconSize(QSize(50, 50))
        button.setCheckable(True)
        if type_str == "1":
            button_label = lt("Published", "已发布")
        else:
            button_label = lt("Draft", "未发布")

        button.clicked.connect(lambda: self.show_function_list(type_str))

        self.buttonGroup_Plugin_function.addButton(button, diagramType)
        # self.buttonGroup.addButton(button, diagramType)

        layout = QGridLayout()
        layout.addWidget(button, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(button_label), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def function_search(self, keyword, type_str="0"):
        # type_str:"0","1","2"
        print("keyword", keyword)

        if keyword == "$$$cjrok":
            type_str = "2"
        print(keyword)
        print("type_str", type_str)
        fun_dialog = FunctionManager(type_str)
        fun_dialog.setObjectName("functionmanager")
        self.stack_main_widget.addWidget(fun_dialog)
        self.stack_main_widget.setCurrentWidget(fun_dialog)

    def create_plugin_mcp_button(self, type_str, diagramType):
        button = QToolButton()
        button.setIcon(QIcon('images/plugin.png'))
        button.setIconSize(QSize(50, 50))
        button.setCheckable(True)
        if type_str == "1":
            button_label = lt("Published", "已发布")
        else:
            button_label = lt("Draft", "未发布")

        button.clicked.connect(lambda: self.show_mcp_list(type_str))

        self.buttonGroup_Plugin_mcp.addButton(button, diagramType)
        # self.buttonGroup.addButton(button, diagramType)

        layout = QGridLayout()
        layout.addWidget(button, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(button_label), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def mcp_search(self, keyword, type_str="0"):
        # type_str:"0","1","2"
        print("keyword", keyword)

        if keyword == "$$$cjrok":
            type_str = "2"
        print(keyword)
        print("type_str", type_str)
        mcp_dialog = McpManager(type_str)
        mcp_dialog.setObjectName("mcpmanager")
        self.stack_main_widget.addWidget(mcp_dialog)
        self.stack_main_widget.setCurrentWidget(mcp_dialog)


    def create_open_web_button(self, record, diagramType, type_str="LLM"):
        button = QToolButton()
        button.setIcon(QIcon(f'images/{record.filename}'))

        button.setStyleSheet("""QToolButton {
                               border:solid 0px;
                            }""")
        button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        button.setIconSize(QSize(50, 50))
        button.setCheckable(False)

        # button.clicked.connect(lambda: self.show_plugin_cfg(record.name + ": " + record.version))
        button.clicked.connect(lambda: self.open_website(record.url, type_str))
        self.buttonGroup_Plugin.addButton(button, diagramType)
        # self.buttonGroup.addButton(button, diagramType)

        layout = QGridLayout()
        layout.addWidget(button, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(record.name), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        # 增加名称
        widget.name = record.name
        widget.setLayout(layout)

        return widget

    def create_plugin_cfg_button(self, record, diagramType):
        button = QToolButton()
        button.setIcon(QIcon(f'images/{record.filename}'))

        button.setStyleSheet("""QToolButton {
                               border:solid 0px;
                            }""")
        button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        button.setIconSize(QSize(50, 50))
        button.setCheckable(False)

        # button.clicked.connect(lambda: self.show_plugin_cfg(record.name + ": " + record.version))
        button.clicked.connect(lambda: self.show_plugin_cfg(record.name))
        self.buttonGroup_Plugin.addButton(button, diagramType)
        # self.buttonGroup.addButton(button, diagramType)

        layout = QGridLayout()
        layout.addWidget(button, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(record.name), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        # 增加名称
        widget.name = record.name
        widget.setLayout(layout)

        return widget

    def create_plugin_tool_cfg_button(self, record, diagramType):
        button = QToolButton()
        button.setIcon(QIcon('images/plugin.png'))
        button.setIconSize(QSize(50, 50))
        button.setCheckable(False)

        button.clicked.connect(lambda: self.show_plugin_tool_cfg(record))

        self.buttonGroup_Plugin.addButton(button, diagramType)
        # self.buttonGroup.addButton(button, diagramType)

        layout = QGridLayout()
        layout.addWidget(button, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(record.name), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.name = record.name
        widget.setLayout(layout)

        return widget

    def create_workflow_cfg_button(self, diagramType):
        button = QToolButton()
        button.setIcon(QIcon('images/plugin.png'))
        button.setIconSize(QSize(50, 50))
        button.setCheckable(True)

        button.clicked.connect(lambda: self.show_workflow_list(lt("Workflow "
                                                                  "List",
                                                                  "工作流列表")))
        # button.clicked.connect(lambda: self.show_prompt_list("提示词管理"))
        self.buttonGroup_WorkFlow.addButton(button, diagramType)
        # self.buttonGroup.addButton(button, diagramType)

        layout = QGridLayout()
        layout.addWidget(button, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(lt("All WorkFlow", "全部工作流")), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def create_task_schedule_button(self, diagramType):
        button = QToolButton()
        button.setIcon(QIcon('images/Calendar.png'))
        button.setIconSize(QSize(50, 50))
        button.setCheckable(True)

        button.clicked.connect(self.show_task_schedule)
        self.buttonGroup_WorkFlow.addButton(button, diagramType)

        layout = QGridLayout()
        layout.addWidget(button, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(lt("Schedule", "定时运行")), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def createCellWidgetnewkm(self, text, diagramType):
        # item = DiagramItem(diagramType, self.itemMenu)
        # icon = QIcon(item.image())

        button = QToolButton()
        button.setIcon(QIcon('images/fileplus.png'))
        button.setIconSize(QSize(50, 50))
        button.setCheckable(False)

        # self.buttonGroup.addButton(button, diagramType)

        layout = QGridLayout()
        layout.addWidget(button, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def show_add_buddy_dialog(self, ai_chat_cfg):
        print("going to add buddy")
        # self.add_buddy()
        jid = ai_chat_cfg.account
        current_connectorThread = self.connectorThread_list.get(ai_chat_cfg.user_id, None)
        current_buddyList = self.buddylist_list.get(ai_chat_cfg.user_id, None)
        if current_connectorThread is None:
            QMessageBox.critical(self, "警告", "该帐号尚未登录！", QMessageBox.Ok)
            return
        else:
            if current_connectorThread.isConnected == False:
                QMessageBox.critical(self, "警告", "该帐号尚未登录！", QMessageBox.Ok)
                return
        # newBuddy = AddBuddyDialog(self, current_connectorThread.jabber_xmpp, list(current_buddyList.groups.keys()), "")
        newBuddy = AddBuddyDialog(self, current_connectorThread.jabber, list(current_buddyList.groups.keys()), "")
        newBuddy.show()

    def create_new_contact_group_button(self, text, agent, diagramType):
        button = QToolButton()
        button.setIcon(QIcon('images/addchat.png'))
        button.setIconSize(QSize(50, 50))
        button.setCheckable(False)
        button.clicked.connect(lambda: self.show_add_buddy_dialog(agent))

        # self.buttonGroup.addButton(button, diagramType)

        layout = QGridLayout()
        layout.addWidget(button, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget
