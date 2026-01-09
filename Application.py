import os
import re
import time
from pathlib import Path
import json
import shutil
import threading
import http.server
from PyQt6.QtWidgets import QApplication, QMessageBox
import subprocess
import ctypes
# 获取当前文件的目录
app_directory = Path(__file__).resolve().parent

# 设置工作目录为 app.py 所在的目录
os.chdir(app_directory)

# 验证工作目录
print("当前工作目录:", os.getcwd())

import sys
import datetime
from db.DBFactory import add_AgentCfg, query_AgentCfg_All, update_AgentCfg, delete_AgentCfg, query_AiChatCfg, \
    query_AIFriend_All_Orderby_Updatetime, update_AIFriend, query_skill_mng,query_MutiAgentCfg,query_KMCfg,query_workflow_mng_all
import copy
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QSystemTrayIcon, QMenu, QStyle
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtGui import QIcon, QKeySequence, QFont, QColor, QShortcut, QAction, QGuiApplication, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QTextEdit,
    QDialog,
    QMessageBox,
    QTreeWidgetItem,
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QSize, QUrl, QCoreApplication
# from qdarkstyle import LightPalette
from skilllearning.utils import *

from ui.ui_mainwindow import Ui_MainWindow
# from pyqt_explanation_balloon.explanationBalloon import ExplanationBalloon
# from AboutDialog import AboutDialog
from ConnectionDialog import ConnectionDialog
from ConnectorThread import ConnectorThread

from MessageBoxEarth import MessageBox
from BuddyList import BuddyList
from TaskList import TaskList
from KMList import KMList
from TechList import TechList
from RosterRequest import RosterRequest
from AddBuddyDialog import AddBuddyDialog
# from AddGroupDialog import AddGroupDialog
from i18n import lt
from jabber import STATUS
import asyncio

# from qt_material import apply_stylesheet
# import qdarkstyle

import qtmodern.styles
import qtmodern.windows
import markdown
import webbrowser

from pluginsmanager import PluginEngine

import argparse

from pluginsmanager import FileSystem

from globals import global_agent_list, global_plugin_list, global_buddy_list
from PyQt6.QtWebEngineWidgets import QWebEngineView

from TaskPage import TaskPage

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QWidget, QApplication, QMessageBox, QMainWindow, QPushButton, QVBoxLayout
from PyQt6.QtCore import pyqtSlot, Qt, QUrl, QFileInfo, pyqtProperty
from Agent import Agent
# import qdarkgraystyle
# import qtvscodestyle as qtvsc
# import qdarktheme
from db.DBFactory import query_SystemCfg

from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage

from apscheduler.schedulers.qt import QtScheduler
from apscheduler.triggers.cron import CronTrigger


class CustomModernWindow(qtmodern.windows.ModernWindow):
    def __init__(self, window):
        super(CustomModernWindow, self).__init__(window)

        # Init QSystemTrayIcon

        # 初始化托盘图标
        self.tray_icon = QSystemTrayIcon(self)

        # 加载图像并调整其大小
        pixmap = QPixmap('images/logowhite.svg')
        scaled_pixmap = pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # 这里设置你希望的大小
        icon = QIcon(scaled_pixmap)
        # icon =QIcon('images/logowhite.svg')

        # 设置自定义图标
        self.tray_icon.setIcon(icon)

        # 显示托盘图标
        self.tray_icon.setVisible(True)
        '''
            Define and add steps to work with the system tray icon
            show - show window
            hide - hide window
            exit - exit from application
        '''
        show_action = QAction(lt("Show", "显示"), self)
        quit_action = QAction(lt("Exit", "退出"), self)
        hide_action = QAction(lt("Hide", "隐藏"), self)
        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(QApplication.instance().quit)
        # quit_action.triggered.connect(self.close)
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

    def closeEvent(self, event):
        # 忽略关闭事件，窗口将不会关闭
        agent = query_SystemCfg()
        use_tray = agent.minirunontray
        print(use_tray)
        if use_tray:
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "AI-SNS",
                "应用最小化到托盘，可点击恢复，或语音：HI,AISNS唤醒数字人",
                QSystemTrayIcon.Information,
                500
            )
        else:
            super(CustomModernWindow, self).closeEvent(event)  # 调用父类的 closeEvent 方法
        # event.ignore()

    def show_window(self):
        # 显示窗口并恢复正常大小
        self.showMaximized()

    def on_tray_icon_activated(self, reason):
        # 根据托盘图标的激活原因显示窗口
        if reason == QSystemTrayIcon.Trigger:  # 单击托盘图标
            if self.isVisible():
                self.hide()
            else:
                self.show_window()


class MainWindow(QMainWindow, Ui_MainWindow):
    connectorThread = None
    tray_icon = None
    run_workflow_signal = pyqtSignal(str,str,str,str)
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.window_max_width = 0
        self.window_max_height = 0

        self.setWindowIcon(QIcon("images/aisns.png"))
        self.agent_cfg_dialog_list = {}
        self.ai_chat_cfg_dialog_list = {}
        self.human_chat_cfg_dialog_list = {}
        self.km_cfg_dialog_list = {}
        self.km_note_window_list = {}
        self.agent_chat_window_list = {}
        self.multi_agent_chat_window_list = {}
        self.connectorThread_list = {}
        self.connectorThread_human_list = {}
        self.notelist_all_list = {}
        self.notelist_all_list_label = {}
        self.tasklist_list = {}
        self.labellist_list = {}
        self.techlist_list = {}
        self.tasklist_group_list = {}
        self.labellist_group_list = {}
        self.memberlist_group_list = {}
        self.buddylist_list = {}
        self.common_buddy_list = None
        self.map_message_box = None
        self.map_buddy_list = None
        self.current_buddylist = None
        self.buddylist_human_list = {}
        self.contactlist_list = {}
        self.contactlist_human_list = {}
        self.kmlist_list = {}
        self.kmlist_list_deleted = {}
        self.get_all_agent()
        self.current_note_widget = None
        self.workflow_list_shown=False
        self.workflow_widget = None
        self.schedule_list_shown = False
        self.task_schedule_widget = None
        self.function_list_shown =False
        self.function_list_draft_shown = False
        self.function_widget = None
        self.function_widget_draft = None
        self.mcp_list_shown =False
        self.mcp_list_draft_shown = False
        self.mcp_widget = None
        self.mcp_widget_draft = None
        self.skill_list_shown =False
        self.skill_list_draft_shown = False
        self.skill_widget = None
        self.skill_widget_draft = None
        self.web_llm_home = None
        self.web_tools_home=None
        self.web_llm_home_frame = None
        self.web_tools_home_frame = None

        self.setupUi(self)  # 调用Ui_MainWindow的函数初始化界面，包括菜单等
        self.scheduler = None

        self.run_workflow_signal.connect(self.run_scheduled_workflow)
        self.scheduler = QtScheduler()
        self.setup_schedule()


    def resizeEvent(self, event):
        super().resizeEvent(event)

        # 获取窗口大小信息
        new_size = event.size()
        old_size = event.oldSize()

        # 更新窗口大小标签
        print(f"窗口大小: {new_size.width()} x {new_size.height()} (旧大小: {old_size.width()} x {old_size.height()})")

        if new_size.width() >= self.window_max_width and new_size.height() >= self.window_max_height:
            print("chang to max")
            self.main_statusbar.setVisible(False)
        else:
            print("chang to normal")
            self.main_statusbar.setVisible(True)

        if new_size.width() > self.window_max_width:
            self.window_max_width = new_size.width()

        if new_size.height() > self.window_max_height:
            self.window_max_height = new_size.height()

        print(self.windowState())

        # if self.windowState()==Qt.WindowNoState:
        #     print("nomal")
        # elif self.windowState()==Qt.WindowMaximized:
        #     print("max")
        # else:
        #     print("other")

    def get_all_agent(self):
        agent_cfgs = query_AgentCfg_All()
        for agent_cfg in agent_cfgs:
            agent = Agent(agent_cfg)
            global_agent_list[agent_cfg.user_id] = agent
        # print("global_agent_list.values",)

    @pyqtSlot(str, str, str, str)  # 也可以没有这个
    # @pyqtSlot(int)#不能用这个
    def on_configured_ai(self, user_id, jid, password, status):
        buddyList = self.buddylist_list[user_id]
        buddyList.ai_chat_cfg = query_AiChatCfg(user_id=user_id)
        self.buddylist_list[user_id] = buddyList

        if status == "0":
            img_url = 'images/messageoffline.png'
        elif status == "1":
            img_url = 'images/messageonline.png'
        else:
            img_url = 'images/messagehuman.png'

        if user_id in self.connectorThread_list:
            connectorThread = self.connectorThread_list[user_id]
            connectorThread.set_jid(jid)
            connectorThread.set_password(password)
            self.connectorThread_list[user_id] = connectorThread

            if connectorThread.isConnected():
                # 已经连接
                if status == "1":
                    self.toolBox_AiChat.setItemIcon(
                        self.toolBox_AiChat.indexOf(self.toolBox_AiChat.findChild(QWidget, user_id)), QIcon(img_url))
                    return
                elif status == "2":
                    self.toolBox_AiChat.setItemIcon(
                        self.toolBox_AiChat.indexOf(self.toolBox_AiChat.findChild(QWidget, user_id)), QIcon(img_url))
                    return
                else:
                    connectorThread.disconnect()
                    buddyList = self.buddylist_list[user_id]
                    buddyList.clear()
                    buddyList.re_init()

                    infoList = self.contactlist_list[user_id]
                    infoList.clear()
                    infoList.re_init()

                    self.toolBox_AiChat.setItemIcon(
                        self.toolBox_AiChat.indexOf(self.toolBox_AiChat.findChild(QWidget, user_id)), QIcon(img_url))
            else:
                # 未连接

                if status == "1":
                    buddyList = self.buddylist_list[user_id]
                    buddyList.topLevelItem(0).setText(0, "等待登录加载中...")

                    infoList = self.contactlist_list[user_id]
                    infoList.topLevelItem(0).setText(0, "等待登录加载中...")

                    connectorThread.start()

                    infoList.load()
                    self.toolBox_AiChat.setItemIcon(
                        self.toolBox_AiChat.indexOf(self.toolBox_AiChat.findChild(QWidget, user_id)), QIcon(img_url))

                elif status == "2":
                    buddyList = self.buddylist_list[user_id]
                    buddyList.topLevelItem(0).setText(0, "等待登录加载中...")

                    infoList = self.contactlist_list[user_id]
                    infoList.topLevelItem(0).setText(0, "等待登录加载中...")

                    connectorThread.start()

                    infoList.load()

                    self.toolBox_AiChat.setItemIcon(
                        self.toolBox_AiChat.indexOf(self.toolBox_AiChat.findChild(QWidget, user_id)), QIcon(img_url))

                else:
                    return

            connectorThread.status = status
        else:
            if status == "0":
                return
            print("on_configured_ai")
            print("user_id", user_id)
            buddyList = self.buddylist_list[user_id]
            infoList = self.contactlist_list[user_id]
            buddyList.topLevelItem(0).setText(0, "等待登录加载中...")
            infoList.topLevelItem(0).setText(0, "等待登录加载中...")
            connectorThread = ConnectorThread(status, jid, password)
            connectorThread.start()
            connectorThread.message.connect(buddyList.message)
            connectorThread.friend_subscribe_request.connect(infoList.get_friend_subscribe_request)
            connectorThread.error.connect(self.error)
            connectorThread.connected.connect(lambda: self.connected_ai(user_id))
            connectorThread.addBuddySig.connect(self.addBuddy)
            infoList.load()
            self.connectorThread_list[user_id] = connectorThread
            self.connectorThread = connectorThread
            self.common_buddy_list = buddyList
            self.BuddyList = buddyList
            self.InfoList = infoList

            # 处理在线状态
            # self.toolBox_AiChat.setItemText(self.toolBox_AiChat.findChild(QWidget,user_id), "Ai智能体管理")
            print(self.toolBox_AiChat.findChild(QWidget, user_id))
            print(self.toolBox_AiChat.indexOf(self.toolBox_AiChat.findChild(QWidget, user_id)))
            self.toolBox_AiChat.setItemIcon(
                self.toolBox_AiChat.indexOf(self.toolBox_AiChat.findChild(QWidget, user_id)), QIcon(img_url))

    @pyqtSlot(str, str, str, str)  # 也可以没有这个
    # @pyqtSlot(int)#不能用这个
    def on_configured_ai_map(self, user_id, jid, password, status):

        if status == "0":
            img_url = 'images/earth.png'
        elif status == "1":
            img_url = 'images/earth.png'
        else:
            img_url = 'images/earth.png'

        if user_id in self.connectorThread_list:
            connectorThread = self.connectorThread_list[user_id]

            if connectorThread.isConnected():
                # 已经连接
                if status == "1":
                    self.toolBox_AiChat.setItemIcon(
                        self.toolBox_AiChat.indexOf(self.toolBox_AiChat.findChild(QWidget, user_id)), QIcon(img_url))
                    return
                elif status == "2":
                    self.toolBox_AiChat.setItemIcon(
                        self.toolBox_AiChat.indexOf(self.toolBox_AiChat.findChild(QWidget, user_id)), QIcon(img_url))
                    return
                else:
                    connectorThread.disconnect()
                    buddyList = self.map_buddy_list
                    buddyList.clear()
                    buddyList.re_init()

                    infoList = self.contactlist_list[user_id]
                    infoList.clear()
                    infoList.re_init()

                    self.toolBox_AiChat.setItemIcon(
                        self.toolBox_AiChat.indexOf(self.toolBox_AiChat.findChild(QWidget, user_id)), QIcon(img_url))
            else:
                # 未连接

                if status == "1":
                    buddyList = self.map_buddy_list
                    buddyList.topLevelItem(0).setText(0, "等待登录加载中...")

                    infoList = self.contactlist_list[user_id]
                    infoList.topLevelItem(0).setText(0, "等待登录加载中...")

                    connectorThread.start()

                    infoList.load()
                    self.toolBox_AiChat.setItemIcon(
                        self.toolBox_AiChat.indexOf(self.toolBox_AiChat.findChild(QWidget, user_id)), QIcon(img_url))

                elif status == "2":
                    buddyList = self.map_buddy_list
                    buddyList.topLevelItem(0).setText(0, "等待登录加载中...")

                    infoList = self.contactlist_list[user_id]
                    infoList.topLevelItem(0).setText(0, "等待登录加载中...")

                    connectorThread.start()

                    infoList.load()

                    self.toolBox_AiChat.setItemIcon(
                        self.toolBox_AiChat.indexOf(self.toolBox_AiChat.findChild(QWidget, user_id)), QIcon(img_url))

                else:
                    return

            connectorThread.status = status
        else:
            if status == "0":
                return
            print("on_configured_ai")
            print("user_id", user_id)
            buddyList = self.map_buddy_list
            infoList = self.contactlist_list[user_id]
            buddyList.topLevelItem(0).setText(0, "等待登录加载中...")
            infoList.topLevelItem(0).setText(0, "等待登录加载中...")
            connectorThread = ConnectorThread(status, jid, password)
            connectorThread.start()
            connectorThread.message.connect(buddyList.message)#收到消息
            connectorThread.friend_subscribe_request.connect(infoList.get_friend_subscribe_request)
            connectorThread.error.connect(self.error)
            connectorThread.connected.connect(lambda: self.connected_ai(user_id))
            connectorThread.addBuddySig.connect(self.addBuddy)
            infoList.load()
            self.connectorThread_list[user_id] = connectorThread
            self.connectorThread = connectorThread
            self.BuddyList = buddyList
            self.InfoList = infoList

            # 处理在线状态
            # self.toolBox_AiChat.setItemText(self.toolBox_AiChat.findChild(QWidget,user_id), "Ai智能体管理")
            print(self.toolBox_AiChat.findChild(QWidget, user_id))
            print(self.toolBox_AiChat.indexOf(self.toolBox_AiChat.findChild(QWidget, user_id)))
            self.toolBox_AiChat.setItemIcon(
                self.toolBox_AiChat.indexOf(self.toolBox_AiChat.findChild(QWidget, user_id)), QIcon(img_url))

        self.map_connectorThread = connectorThread

        if self.map_message_box.con is None:
            self.map_message_box.setConnection(self.map_connectorThread)


    @pyqtSlot(str, str, str)  # 也可以没有这个
    # @pyqtSlot(int)#不能用这个
    def on_configured_human(self, user_id, jid, password):
        status = STATUS.available

        if user_id in self.connectorThread_human_list:
            connectorThread = self.connectorThread_human_list[user_id]
            if connectorThread.isConnected():
                connectorThread.changeStatus(status, self.statusEdit.text())
                self.statusEdit.clearFocus()
        else:
            print("on_configured_human")
            print("user_id", user_id)
            buddyList = self.buddylist_human_list[user_id]
            buddyList.topLevelItem(0).setText(0, "等待登录加载中...")
            connectorThread = ConnectorThread(status, jid, password)
            connectorThread.start()
            connectorThread.message.connect(buddyList.message)
            connectorThread.error.connect(self.error)
            connectorThread.connected.connect(lambda: self.connected_human(user_id))
            connectorThread.addBuddySig.connect(self.addBuddy)
            self.connectorThread_human_list[user_id] = connectorThread

    @pyqtSlot(int)
    def connection(self, status=STATUS.available):
        if not self.connectorThread:
            self.connectorThread = ConnectorThread(status)
            self.connectorThread.start()
            self.connectorThread.message.connect(self.BuddyList.message)
            self.connectorThread.error.connect(self.error)
            self.connectorThread.connected.connect(self.connected)
            self.connectorThread.disconnected.connect(self.disconnect)
            self.connectorThread.presence.connect(self.BuddyList.presence)
            self.connectorThread.debug.connect(self.debug)
            self.connectorThread.subscriptionRequest.connect(self.subscriptionRequest)
            self.connectorThread.addBuddy.connect(self.addBuddy)
        elif self.connectorThread.isConnected():
            self.connectorThread.changeStatus(status, self.statusEdit.text())
            self.statusEdit.clearFocus()

    def openLink(self, url):
        webbrowser.open(url.toString())

    def connected_ai(self, user_id):
        connectorThread = self.connectorThread_list[user_id]
        buddyList = self.buddylist_list[user_id]
        buddyList.setConnection(connectorThread)
        infoList = self.contactlist_list[user_id]
        infoList.setConnection(connectorThread)
        self.getRoster_ai(connectorThread, user_id)

    def connected_human(self, user_id):
        connectorThread = self.connectorThread_human_list[user_id]
        buddyList = self.buddylist_human_list[user_id]
        buddyList.setConnection(connectorThread)
        infoList = self.contactlist_list[user_id]
        infoList.setConnection(connectorThread)
        self.getRoster_human(connectorThread, user_id)

    def error(self, title, content):
        QMessageBox.critical(self, title, content, QMessageBox.Ok)


    def closeEvent(self, event):
        self.quit()

    def quit(self):
        self.disconnect()
        QApplication.instance().quit()

    def getRoster_ai(self, connectorThread, user_id):
        # pass
        # roster = connectorThread.getRoster()#改为使用下面获取本地数据库存储
        roster = self.get_roster_local(user_id)
        buddyList = self.buddylist_list[user_id]
        for buddy in roster:
            buddyList.addItem(buddy)
        if user_id !="1":
            buddyList.itemDoubleClicked.connect(self.open_ai_chat_window)
        global_buddy_list["buddylist"] = buddyList
        print("connect buddylist")

    def getRoster_human(self, connectorThread, user_id):
        # pass
        roster = connectorThread.getRoster()
        buddyList = self.buddylist_human_list[user_id]
        for buddy in roster:
            buddyList.addItem(buddy)
        buddyList.itemDoubleClicked.connect(self.open_ai_chat_window)
        global_buddy_list["buddylist"] = buddyList
        print("connect buddylist")

    def get_roster_local(self, user_id):
        aichat_cfg = query_AiChatCfg(user_id=user_id)
        owner_sns_account = aichat_cfg.account
        records = query_AIFriend_All_Orderby_Updatetime(owner_sns_account=owner_sns_account)
        roster = []
        for record in records:
            roster.append(record.account)
        return roster

    @pyqtSlot(QTreeWidgetItem, int)
    def open_ai_chat_window(self, item, column):
        print("in clickitem")
        # id_value = item.data(column, Qt.ItemDataRole.UserRole)
        # # print("双击了：", id_value)
        # if id_value == None:
        #     return (False)
        if item.__class__.__name__ == "BuddyGroup":
            return

        if item and item.type() == QTreeWidgetItem.ItemType.UserType + 1:
            item.setIcon(0, QIcon())
            account = item.jid
            owner_sns_account = item.ai_chat_cfg.account
            # update_time = datetime.datetime.now()
            update_AIFriend(account, owner_sns_account, new_message_flag=False)

        self.current_buddylist.current_chat_item = item

        item.open_chat_window()

    def show_agent_current_main_widget(self):
        item_type = self.get_toolbox_agentchat_current_item_type()
        item_id = self.get_toolbox_agentchat_current_item_id()
        if item_type=="agent":
            agent_cfg = global_agent_list[item_id]
            self.open_exist_agent_task_chat(agent_cfg)
        elif item_type=="agent_group":
            agent_group_cfg = query_MutiAgentCfg(group_id=item_id)
            self.open_multi_agent_task_chat(agent_group_cfg)
        else:
            self.stack_main_widget.setCurrentWidget(self.app_home_frame)
            self.app_home.page().load(QUrl("http://www.ai-sns.org/index_agent.html"))

    def show_ai_current_main_widget(self):
        item_type = self.get_toolbox_aichat_current_item_type()
        item_id = self.get_toolbox_aichat_current_item_id()
        if item_type == "ai_map":
            self.stack_main_widget.setCurrentWidget(self.map_window_widget)
        elif item_type == "ai_chat":
            chat_item = self.current_buddylist.current_chat_item
            if chat_item:
                chat_item.open_chat_window()
            else:
                self.stack_main_widget.setCurrentWidget(self.app_home_frame)
                self.app_home.page().load(QUrl("http://www.ai-sns.org/index.html"))
        else:
            self.stack_main_widget.setCurrentWidget(self.app_home_frame)
            self.app_home.page().load(QUrl("http://www.ai-sns.org/index.html"))

    def show_km_current_main_widget(self):
        item_type = self.get_toolbox_km_current_item_type()
        item_id = self.get_toolbox_km_current_item_id()
        if item_type == "note":
            if self.current_note_widget:
                self.stack_main_widget.setCurrentWidget(self.current_note_widget)
            else:
                km_cfg=query_KMCfg(km_id=item_id)
                self.open_note_editor(km_cfg)
        elif item_type == "kb":
            self.stack_main_widget.setCurrentWidget(self.app_home_frame)
            self.app_home.page().load(QUrl("http://www.ai-sns.org/index_km.html"))
        else:
            self.stack_main_widget.setCurrentWidget(self.app_home_frame)
            self.app_home.page().load(QUrl("http://www.ai-sns.org/index_km.html"))

    def show_workflow_current_main_widget(self):
        if self.workflow_list_shown:
            self.stack_main_widget.setCurrentWidget(self.workflow_widget)
        elif self.schedule_list_shown:
            self.stack_main_widget.setCurrentWidget(self.task_schedule_widget)
        else:
            self.stack_main_widget.setCurrentWidget(self.app_home_frame)
            self.app_home.page().load(QUrl("http://www.ai-sns.org/index_humanchat.html"))


    def show_plugin_current_main_widget(self):
        item_type = self.get_toolbox_plugin_current_item_type()
        item_id = self.get_toolbox_plugin_current_item_id()

        if item_type == "llm_setting":
            self.stack_main_widget.setCurrentWidget(self.app_home_frame)
            self.app_home.page().load(QUrl("http://www.ai-sns.org/index_plugin.html"))

        elif item_type == "tools_setting":
            self.stack_main_widget.setCurrentWidget(self.app_home_frame)
            self.app_home.page().load(QUrl("http://www.ai-sns.org/index_plugin.html"))

        elif item_type == "mcp_setting":
            if self.mcp_list_shown:
                self.stack_main_widget.setCurrentWidget(self.mcp_widget)
            elif self.mcp_list_draft_shown:
                self.stack_main_widget.setCurrentWidget(self.mcp_widget_draft)
            else:
                self.stack_main_widget.setCurrentWidget(self.app_home_frame)
                self.app_home.page().load(QUrl("http://www.ai-sns.org/index_plugin.html"))

        elif item_type == "function_setting":
            if self.function_list_shown:
                self.stack_main_widget.setCurrentWidget(self.function_widget)
            elif self.function_list_draft_shown:
                self.stack_main_widget.setCurrentWidget(self.function_widget_draft)
            else:
                self.stack_main_widget.setCurrentWidget(self.app_home_frame)
                self.app_home.page().load(QUrl("http://www.ai-sns.org/index_plugin.html"))

        elif item_type == "skill_setting":

            if self.skill_list_shown:
                self.stack_main_widget.setCurrentWidget(self.skill_widget)
            elif self.skill_list_draft_shown:
                self.stack_main_widget.setCurrentWidget(self.skill_widget_draft)
            else:
                self.stack_main_widget.setCurrentWidget(self.app_home_frame)
                self.app_home.page().load(QUrl("http://www.ai-sns.org/index_plugin.html"))

        elif item_type == "market_setting":
            self.stack_main_widget.setCurrentWidget(self.app_home_frame)
            self.app_home.page().load(QUrl("http://www.ai-sns.org/index_plugin.html"))

    def show_web_current_main_widget(self):
        item_type = self.get_toolbox_web_current_item_type()
        item_id = self.get_toolbox_web_current_item_id()

        if item_type == "web_llm":
            if not self.web_llm_home_frame:
                self.open_website("http://www.ai-sns.org", "LLM")
            else:
                self.stack_main_widget.setCurrentWidget(self.web_llm_home_frame)


        elif item_type == "web_tools":
            if not self.web_tools_home_frame:
                self.open_website("http://www.ai-sns.org", "Tool")
            else:
                self.stack_main_widget.setCurrentWidget(self.web_tools_home_frame)


    def show_app_home_current_main_widget(self):
        self.stack_main_widget.setCurrentWidget(self.app_home_frame)
        self.app_home.setHtml(self.html_with_style)

    @pyqtSlot(dict)
    def subscriptionRequest(self, presence):
        request = RosterRequest(self, self.connectorThread.jabber, presence)
        request.show()

    def opendochelp(self):

        self.stack_main_widget.setCurrentIndex(1)

    def openwebhelp(self):
        webbrowser.open("http://www.ai-sns.org")

    @pyqtSlot()
    def addBuddy(self, item=None):
        print("in addbuddy")
        if self.connectorThread:
            if item:
                jid = item.jid
            else:
                jid = ""
            newBuddy = AddBuddyDialog(self, self.connectorThread.jabber_xmpp, list(self.BuddyList.groups.keys()), jid)
            newBuddy.show()

    def setup_schedule(self):
        """设置调度器并添加任务。"""
        records = query_workflow_mng_all()

        for record in records:
            quartz_cron = record.timer_cron
            run_agent_id = record.run_agent_id
            run_agent_name = record.run_agent_name
            workflow_name = record.title
            workflow_id = record.workflow_id

            if quartz_cron:
                trigger = self.parse_quartz_cron(quartz_cron)
                if trigger:
                    # ✅ 方法 1：lambda + 默认参数（推荐）
                    self.scheduler.add_job(
                        lambda run_agent_id=run_agent_id,
                               run_agent_name=run_agent_name,
                               workflow_name=workflow_name,
                               workflow_id=workflow_id:
                        self.scheduled_to_run(run_agent_id, run_agent_name, workflow_name, workflow_id),
                        trigger,
                        id=f"job_{workflow_id}",
                        replace_existing=True
                    )

        self.scheduler.start()


    def parse_quartz_cron(self, cron_expression):
        """
        解析Quartz cron表达式并返回APScheduler兼容的CronTrigger。

        Args:
            cron_expression (str): Quartz cron表达式。

        Returns:
            CronTrigger: 如果解析成功，则返回CronTrigger对象；否则返回None。
        """
        try:
            # 匹配6个字段的Quartz cron表达式
            match = re.match(r"(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)", cron_expression)
            if not match:
                raise ValueError("Cron表达式格式无效")

            # 提取cron表达式字段
            seconds, minutes, hours, day_of_month, month, day_of_week = match.groups()

            # 将Quartz day_of_week（1=星期日）转换为APScheduler格式（0=星期一）
            if day_of_week.isdigit():
                day_of_week = str((int(day_of_week) % 7))

            # 创建APScheduler CronTrigger
            return CronTrigger(second=seconds, minute=minutes, hour=hours,
                               day=day_of_month, month=month, day_of_week=day_of_week)
        except Exception as e:
            print(f"错误解析cron表达式: {e}")
            return None

    def scheduled_to_run(self,run_agent_id,run_agent_name,workflow_name,workflow_id):
        self.run_workflow_signal.emit(run_agent_id,run_agent_name,workflow_name,workflow_id)

    def run_scheduled_workflow(self,agent_id,agent_name,workflow_name,workflow_id):
        """要执行的计划任务。"""
        now = datetime.now()
        print(f"任务运行在：{now}")
        # return
        self.show_agent_toolbox_stack()
        agent_item = self.toolBox_AgentChat.findChild(QWidget, agent_id)
        if agent_item:
            current_index = self.toolBox_AgentChat.indexOf(agent_item)  # 获取当前索引
            self.toolBox_AgentChat.setCurrentIndex(current_index)
        agents = global_agent_list.values()  # 前面已经从数据库中初始化了agent列表，直接使用前面已经初始化的列表获取其agent_cfg即可
        for agent in agents:
            if agent.name == agent_name:
                self.open_exist_agent_task_chat(agent)

                agent_chat_window = self.agent_chat_window_list[agent_id]
                taskpage = agent_chat_window.findChild(TaskPage, "TaskPageObject")

                browser_page = taskpage.messageBrowser.page()
                browser_page.loadFinished.connect(lambda success: self.onBrowserLoadFinished(success,taskpage, workflow_name, workflow_id))  # 第一次可能page没来得及load，所以需要在onload中处理
                print("taskpage.is_browser_page_loaded",taskpage.is_browser_page_loaded)
                self.is_browser_page_loaded = False
                if taskpage.is_browser_page_loaded == True:  # page是否已经load了
                    self.is_browser_page_loaded = True

                if self.is_browser_page_loaded == True:
                    self.onBrowserLoadFinished(True,taskpage, workflow_name, workflow_id)


    def onBrowserLoadFinished(self, success,taskpage,workflow_name,workflow_id):
        print("onBrowserLoadFinished")
        if success:
            print("success:",success)
            # taskpage = self.taskpage_for_workflow
            taskpage.messageEdit.setFocus()

            taskpage.messageEdit.setPlainText(f"请运行一下工作流:{workflow_name},//workflow_id:{workflow_id}")
            taskpage.sendMessage()



def __description() -> str:
    return "Create your own anime meta data"


def __usage() -> str:
    return "vrv-meta.py --service vrv"


def __init_cli() -> argparse:
    parser = argparse.ArgumentParser(description=__description(), usage=__usage())
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


def __print_program_end() -> None:
    print("-----------------------------------")
    print("End of execution")
    print("-----------------------------------")


def __init_app(parameters: dict) -> None:
    return PluginEngine(options=parameters).start()


def initialize_application():
    # 获取当前工作目录
    work_dir = os.getcwd()

    # 设置数据库目录及文件路径
    db_dir = os.path.join(work_dir, 'db')
    db_file = os.path.join(db_dir, 'db.sqlite')
    db_template_file = os.path.join(db_dir, 'db_template.sqlite')

    # 如果没有 db.sqlite 文件，拷贝 db_template.sqlite 为 db.sqlite
    if not os.path.exists(db_file):
        if os.path.exists(db_template_file):
            shutil.copyfile(db_template_file, db_file)
            print(f"{db_template_file} copied to {db_file}.")
        else:
            print("Database template file not found.")

    # 需要检查和创建的目录列表
    directories_to_create = [
        'coding',
        'download',
        'km',
        os.path.join('resource', 'attachment', 'chat'),
        os.path.join('resource', 'attachment', 'skill'),
        os.path.join('skilllearning', 'screenshot'),
        os.path.join('skilllearning', 'data'),
        os.path.join('skilllearning', 'imgs')
    ]

    # 检查并创建目录
    for dir_name in directories_to_create:
        full_path = os.path.join(work_dir, dir_name)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
            print(f"Directory {full_path} created.")
        else:
            print(f"Directory {full_path} already exists.")

    # 启动 HTTP 服务器的函数
    def start_http_server():
        os.chdir(work_dir)  # 确保工作目录
        handler = http.server.SimpleHTTPRequestHandler
        server = http.server.ThreadingHTTPServer(('0.0.0.0', 8900), handler)
        server.serve_forever()

    # 用线程启动 HTTP 服务器
    http_server_thread = threading.Thread(target=start_http_server, daemon=True)
    http_server_thread.start()
    print("HTTP server started on port 8900.")

    # 获取虚拟环境的路径
    if hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix:
        venv_path = sys.prefix  # 当前虚拟环境的路径
    else:
        venv_path = None  # 如果不是在虚拟环境中，则返回 None

    print(f"Virtual Environment Path: {venv_path}")

    # 获取当前 Python 解释器的路径
    python_executable = os.path.dirname(os.__file__)
    print(f"Python Executable Path: {python_executable}")

    # 获取当前 Python 解释器的路径
    python_executable_path = sys.executable

    print(f"Python Interpreter Path: {python_executable_path}")


if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("images/logowhite.svg"))

    # Windows系统特殊处理
    if sys.platform == 'win32':
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('ai-sns_unique_id_1118')  # [1]


    QApplication.setApplicationName("AI-SNS")
    # 设置高 DPI 缩放策略
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    try:
        initialize_application()
        # QMessageBox.information(None, "Initialization", "Application initialized successfully.")
    except Exception as e:
        print("Initialization Error", str(e))

    __cli_args = __init_cli().parse_args()
    print("cjrok")
    print(__cli_args.log)
    print("cjrok2")

    # load plugins load插件
    # initiate plugins 初始化插件
    __init_app({
        'log_level': __cli_args.log,
        'directory': __cli_args.directory
    })

    print(global_plugin_list)

    window = MainWindow()

    # subprocess.Popen(["/Library/ai-sns/venv/bin/python",
    #                   "/Library/ai-sns/getmousekeyboard005.py"])

    # self.learn_operation_bar.start_record()
    # Automatically start capturing keys
    # Key listener thread
    # window.start_keyboardmouse()
    # if not self.key_thread.isRunning():
    #     self.key_thread.start()
    #
    # else:
    #     self.key_thread.resume()

    # window.setWindowIcon(QIcon("C:\\dev\\ai-sns\\PyTalk\\pytalk\\images\\aisns.png"))
    #
    # window.showMaximized()
    #
    # window.showagenthome()
    #
    # # 设置深色主题
    # app.setStyleSheet(qdarkstyle.load_stylesheet())afsfsfs

    qtmodern.styles.light(app)  # qtmodern dark or light
    #
    mw = CustomModernWindow(window)
    #
    # if sys.platform == "win32":
    #     mw.showMaximized()  # qtmodern 保留操作系统工具栏
    # elif sys.platform == "darwin":
    #     mw.showFullScreen()  # 不保留操作系统工具栏
    # else:
    #     mw.showMaximized()  # qtmodern 保留操作系统工具栏
    # #
    # mw.setWindowIcon(QIcon("C:\\dev\\ai-sns\\PyTalk\\pytalk\\images\\aisns.png"))
    # app.setWindowIcon(QIcon("C:\\dev\\ai-sns\\PyTalk\\pytalk\\images\\aisns.png"))
    # app.setStyle('Windows')
    # qtmodern.styles.light(app)  # qtmodern dark or light
    # qtmodern.styles.dark(app)
    # mw = qtmodern.windows.ModernWindow(window)  # qtmodern

    mw.showMaximized()  # qtmodern 保留操作系统工具栏
    #

    # window.showMaximized()  # 注释掉：不需要单独显示原始窗口，因为已经被 CustomModernWindow 包装
    # mw = CustomModernWindow(window)
    sys.exit(app.exec())
