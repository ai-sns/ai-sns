# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_MessageWidget.ui'
#
# Created: Tue Jan 22 07:03:54 2008
#      by: PyQt6 UI code generator 5.15.4
#
# WARNING! All changes made in this file will be lost!
import webbrowser
import os

from pathlib import Path
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QUrl, pyqtSignal, pyqtSlot, pyqtProperty
from PyQt6.QtGui import QPalette, QColor, QTextCursor, QTextCharFormat
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QCheckBox, QLabel, QSplitter, QTabWidget, QVBoxLayout, QWidget, QMessageBox, QLineEdit,QComboBox
from PyQt6.QtCore import Qt, QMetaObject, pyqtSignal, pyqtSlot, QEvent
from PyQt6.QtWebChannel import QWebChannel

from ChatListEarthLabel import ChatListLabel
from i18n import lt
from ChatListEarth import ChatList
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QPoint
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
                             QLabel, QMenu)


class CustomTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Enable custom context menu for the tab bar
        self.tabBar().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabBar().customContextMenuRequested.connect(self.show_tab_context_menu)

    def show_tab_context_menu(self, pos: QPoint):
        # Get the index of the tab under the mouse cursor
        tab_index = self.tabBar().tabAt(pos)
        if tab_index < 0:
            return  # No tab was clicked

        # Create and populate the context menu
        menu = QMenu(self)

        # Action to close the current tab
        close_action = QAction("关闭当前页", self)
        close_action.triggered.connect(lambda: self.close_tab(tab_index))
        menu.addAction(close_action)

        # Action to close the current tab
        help_action = QAction("使用说明", self)
        help_action.triggered.connect(lambda: self.close_tab(tab_index))
        menu.addAction(help_action)

        # Check if the current tab is the profile tab
        # if self.tabText(tab_index) == "社交资料" or self.tabText(tab_index) == "Profile":  # Assuming the tab label for profile is "社交资料"
        if self.widget(tab_index).objectName() == "tab_profile":
            open_in_browser_action = QAction("用浏览器打开", self)
            open_in_browser_action.triggered.connect(lambda: self.open_profile_in_browser(tab_index))
            menu.addAction(open_in_browser_action)

        # Display the menu at the global position of the mouse
        global_pos = self.tabBar().mapToGlobal(pos)
        menu.exec(global_pos)

    def close_tab(self, index: int):
        # Close the tab at the given index
        self.removeTab(index)

    def open_profile_in_browser(self, tab_index: int):
        # Open the URL of the profile webview in the system's default web browser
        profile_webview = self.widget(tab_index).findChild(QWebEngineView, "profile_webview")
        if profile_webview:
            url = profile_webview.url().toString()
            webbrowser.open(url)  # Open the URL in the default browser

class MessageHandler(QWidget):
    on_message = pyqtSignal(str)
    on_chat_message =  pyqtSignal(str,str,str)
    on_command_message = pyqtSignal(str, str, str)
    on_message_checked = pyqtSignal(int, str)
    on_edit_content_message = pyqtSignal(str, str)
    on_message_file_clicked = pyqtSignal(str)
    on_message_open_link = pyqtSignal(str)
    on_msg_from_js = pyqtSignal(str)
    on_user_request_service  = pyqtSignal(str, str)
    on_user_send_im = pyqtSignal(str, str, str)
    on_info_load_more = pyqtSignal(str)
    on_load_map_setting = pyqtSignal()
    on_update_map_setting = pyqtSignal(str,str)

    def __init__(self):
        super().__init__()
        self.theinnervalue = "cjrok"

    def PyQt52WebValue(self):
        return self.theinnervalue

    @pyqtSlot(str, result=str)
    def Web2PyQt5Value(self, tmpstr):
        self.theinnervalue = self.theinnervalue + tmpstr
        QMessageBox.information(self, "从网页来的信息", tmpstr)

    @pyqtSlot(int, str, result=str)
    def check_message(self, i, status):
        print("i:", i)
        print("status", status)
        self.on_message_checked.emit(i, status)

    @pyqtSlot(str, str, result=str)
    def edit_content_message(self, code_type, text):
        print("codetype:", code_type)
        print("text:", text)
        self.on_edit_content_message.emit(code_type, text)

    @pyqtSlot(str, result=str)
    def file_clicked_message(self, file_path):
        print("file_path:", file_path)
        self.on_message_file_clicked.emit(file_path)

    @pyqtSlot(str, result=str)
    def open_link_message(self, url):
        print("url:", url)
        self.on_message_open_link.emit(url)

    def pass_message(self, messsage):
        self.on_message.emit(messsage)

    def send_talk_message(self,fromuser,touser, messsage):
        self.on_chat_message.emit(fromuser,touser,messsage)

    def send_command_to_map(self, command, param_1, param_2):
        self.on_command_message.emit(command, param_1, param_2)



    @pyqtSlot(str, result=str)
    def get_msg_from_js(self,theteststr):
        print(theteststr)
        self.on_msg_from_js.emit(theteststr)

    @pyqtSlot(str,str, result=str)
    def request_service(self,type_str,address):
        self.on_user_request_service.emit(type_str,address)

    @pyqtSlot(str,str,str, result=str)
    def send_im(self,fromuser,touser, messsage):
        self.on_user_send_im.emit(fromuser,touser, messsage)


    @pyqtSlot(str, result=str)
    def info_load_more(self,type_str):
        print("type_str:",type_str)

        self.on_info_load_more.emit(type_str)

    @pyqtSlot()
    def load_map_setting(self):
        self.on_load_map_setting.emit()

    @pyqtSlot(str,str, result=str)
    def update_map_setting(self, field_name, field_value):
        self.on_update_map_setting.emit(field_name, field_value)


    thevalue = pyqtProperty(str, fget=PyQt52WebValue, fset=Web2PyQt5Value)


class Ui_MessageWidget(object):
    def setupUi(self, MessageWidget):
        MessageWidget.setObjectName("MessageWidget")
        MessageWidget.resize(
            QtCore.QSize(QtCore.QRect(0, 0, 800, 600).size()).expandedTo(MessageWidget.minimumSizeHint()))
        MessageWidget.setContentsMargins(0, 0, 0, 0)  # 不留间隙

        self.vboxlayout = QtWidgets.QVBoxLayout(MessageWidget)
        self.vboxlayout.setObjectName("vboxlayout")
        self.vboxlayout.setContentsMargins(0, 0, 0, 0)  # 不留间隙

        # # 添加标签到布局中
        # title_label = QLabel("聊天对象：" + self.name, MessageWidget)
        # title_label.setStyleSheet("color: #146ebe;font-weight:bold")
        # title_label.setContentsMargins(0, 0, 0, 0)  # 不留间隙
        # title_label.setFixedHeight(30)  # 影响间隙
        #
        #
        # self.vboxlayout.addWidget(title_label)

        # 添加标签到布局中
        self.hboxlayoutlabel = QtWidgets.QHBoxLayout()

        spacerItem_label_left = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding,
                                                      QtWidgets.QSizePolicy.Policy.Minimum)
        self.hboxlayoutlabel.addItem(spacerItem_label_left)  # 通过留空来居中

        # self.title_label = QLabel("聊天对象：" + self.name, MessageWidget)#Around the World in 80 Days
        self.title_label = QLabel("Around the World in 80 Days", MessageWidget)
        self.title_label.setStyleSheet("color: #146ebe;font-weight:bold")
        self.title_label.setContentsMargins(0, 0, 0, 0)  # 不留间隙
        self.title_label.setFixedHeight(30)  # 影响间隙

        self.title_label.setStyleSheet("color: #146ebe;font-weight:bold")
        self.title_label.setFixedHeight(30)  # 影响间隙
        self.title_label.setContentsMargins(0, 0, 0, 0)  # 不留间隙
        self.hboxlayoutlabel.addWidget(self.title_label)

        spacerItem_label_right = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding,
                                                       QtWidgets.QSizePolicy.Policy.Minimum)
        self.hboxlayoutlabel.addItem(spacerItem_label_right)  # 通过留空来居中

        self.vboxlayout.addLayout(self.hboxlayoutlabel)

        # self.messageBrowser = QtWidgets.QTextBrowser(MessageWidget)
        # self.messageBrowser.setObjectName("messageBrowser")
        # self.vboxlayout.addWidget(self.messageBrowser)

        # 使用 QSplitter 来管理 self.frame 和 self.tabWidget
        # self.splitter = QSplitter(Qt.Orientation.Horizontal, None)
        self.splitter = QSplitter(MessageWidget)

        # self.messageBrowser = QtWidgets.QTextBrowser(TaskWidget)
        # self.messageBrowser = QtWidgets.QTextBrowser(MessageWidget)
        self.messageBrowser = QWebEngineView()
        self.messageBrowser.setZoomFactor(0.75)
        self.messageBrowser.setObjectName("messageBrowser")

        self.frame = QtWidgets.QFrame(self.splitter)
        self.frame.setStyleSheet("QFrame { border: 1px solid #c0c0c0;}")
        self.frame_layout = QtWidgets.QVBoxLayout(self.frame)
        self.frame_layout.addWidget(self.messageBrowser)

        # 创建 QTabWidget 控件及其页签，设置页签在底部
        # self.tabWidget = QTabWidget(self.splitter)
        self.tabWidget = CustomTabWidget(self.splitter)
        self.tabWidget.setObjectName("tabWidget")
        self.tabWidget.setTabPosition(QTabWidget.TabPosition.South)



        self.tab_activity = QtWidgets.QWidget()
        self.tab_activity.setObjectName("tab_activity")
        self.tabLayout_activity = QVBoxLayout(self.tab_activity)
        self.tabLayout_activity.setContentsMargins(0, 0, 0, 0)
        self.activity_edit = QtWidgets.QTextEdit(self.tab_activity)
        self.activity_edit.setReadOnly(True)
        self.tabLayout_activity.addWidget(self.activity_edit)
        self.tabWidget.addTab(self.tab_activity, lt("Activity","活动"))



        self.tab_profile = QtWidgets.QWidget()
        self.tab_profile.setObjectName("tab_profile")
        self.tabLayout_profile = QVBoxLayout(self.tab_profile)
        self.tabLayout_profile.setContentsMargins(0, 0, 0, 0)
        self.profile_webview = QWebEngineView(self.tab_profile)
        self.profile_webview.setObjectName("profile_webview")
        self.profile_webview.setUrl(QUrl("https://x.com/BillGates"))
        self.tabLayout_profile.addWidget(self.profile_webview)
        self.tabWidget.addTab(self.tab_profile, lt("Profile","社交资料"))



        self.tab_thinking = QtWidgets.QWidget()
        self.tab_thinking.setObjectName("tab_thinking")
        self.tabLayout_thinking = QVBoxLayout(self.tab_thinking)
        self.tabLayout_thinking.setContentsMargins(0, 0, 0, 0)
        self.thinking_edit = QtWidgets.QTextEdit(self.tab_thinking)
        self.thinking_edit.setReadOnly(True)
        self.tabLayout_thinking.addWidget(self.thinking_edit)
        self.tabWidget.addTab(self.tab_thinking, lt("Thinking","思考"))
        self.init_document_structure()

        self.tab_plan = QtWidgets.QWidget()
        self.tab_plan.setObjectName("tab_plan")
        self.tabLayout_plan = QtWidgets.QVBoxLayout(self.tab_plan)
        self.tabLayout_plan.setContentsMargins(0, 0, 0, 0)
        self.plan_edit = QtWidgets.QTextEdit(self.tab_plan)
        self.tabLayout_plan.addWidget(self.plan_edit)
        self.tabWidget.addTab(self.tab_plan, lt("Plan","计划"))


        # Create search input
        textEdit = QLineEdit()
        textEdit.setPlaceholderText("关键词+回车搜索，空+回车复原")
        palette = textEdit.palette()
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("gray"))  # 可以改为其他颜色
        textEdit.setPalette(palette)
        textEdit.setToolTip("关键字以+++开头表示在搜索结果中继续搜索")

        tab_widget = QWidget()
        self.tab_chat_list = ChatList(self, self.ai_chat_cfg)
        self.tab_chat_list.setObjectName("chat_list")
        self.tabLayout_chat_list = QVBoxLayout(tab_widget)
        self.tabLayout_chat_list.addWidget(textEdit)
        self.tabLayout_chat_list.addWidget(self.tab_chat_list)
        self.tabLayout_chat_list.setContentsMargins(5, 5, 5, 5)
        # Connect returnPressed signal to search function
        textEdit.returnPressed.connect(lambda: self.tab_chat_list.search(textEdit.text()))

        self.tabWidget.addTab(tab_widget, "聊天历史")

        # Create search input
        textEdit_label = QLineEdit()
        textEdit_label.setPlaceholderText("关键词+回车搜索，空+回车复原")
        palette = textEdit_label.palette()
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("gray"))  # 可以改为其他颜色
        textEdit_label.setPalette(palette)
        textEdit_label.setToolTip("关键字以+++开头表示在搜索结果中继续搜索")
        tab_widget_label = QWidget()
        self.tab_chat_list_label = ChatListLabel(self, self.ai_chat_cfg)
        self.tab_chat_list_label.setObjectName("chat_list_label")
        self.tabLayout_chat_list_label = QVBoxLayout(tab_widget_label)
        self.tabLayout_chat_list_label.addWidget(textEdit_label)
        self.tabLayout_chat_list_label.addWidget(self.tab_chat_list_label)
        self.tabLayout_chat_list_label.setContentsMargins(5, 5, 5, 5)
        # Connect returnPressed signal to search function
        textEdit_label.returnPressed.connect(lambda: self.tab_chat_list_label.search(textEdit_label.text()))
        self.tabWidget.addTab(tab_widget_label, "聊天标签")

        # self.splitter.setSizes([1, ])  # 设置初始状态不显示输出窗口
        self.splitter.setSizes([300, 1])

        self.vboxlayout.addWidget(self.splitter)

        self.hboxlayout = QtWidgets.QHBoxLayout()
        self.hboxlayout.setObjectName("hboxlayout")

        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.hboxlayout.addItem(spacerItem)

        self.fontButton = QtWidgets.QPushButton(MessageWidget)
        self.fontButton.setIcon(QtGui.QIcon("images/face.png"))
        self.fontButton.setObjectName("fontButton")
        self.fontButton.setVisible(False)
        self.hboxlayout.addWidget(self.fontButton)

        self.videoButton = QtWidgets.QPushButton(MessageWidget)
        self.videoButton.setIcon(QtGui.QIcon("images/attachment.png"))
        self.videoButton.setObjectName("videoButton")
        self.videoButton.setVisible(False)
        self.hboxlayout.addWidget(self.videoButton)

        self.enterButton = QtWidgets.QPushButton(MessageWidget)
        self.enterButton.setIcon(QtGui.QIcon("images/enter.png"))
        self.enterButton.setObjectName("enterButton")
        self.enterButton.setHidden(True)
        # self.hboxlayout.addWidget(self.enterButton)

        self.exitButton = QtWidgets.QPushButton(MessageWidget)
        self.exitButton.setIcon(QtGui.QIcon("images/exit.png"))
        self.exitButton.setObjectName("exitButton")
        self.hboxlayout.addWidget(self.exitButton)

        self.map_type_combo = QComboBox(MessageWidget)
        self.map_type_combo.addItem("Google map","Google")
        self.map_type_combo.addItem("Baidu map", "Baidu")
        self.map_type_combo.currentIndexChanged.connect(self.change_map)
        self.hboxlayout.addWidget(self.map_type_combo)

        self.talk_type_combo = QComboBox(MessageWidget)
        self.talk_type_combo.addItem(lt("Talk to My AI","指挥我的AI"), "Mine")
        self.talk_type_combo.addItem(lt("Talk to Friend","和朋友交谈"), "Friend")
        self.talk_type_combo.setVisible(False)
        self.hboxlayout.addWidget(self.talk_type_combo)


        self.humantakeoverCheckBox = QCheckBox(lt("Human take control",
                                                  "人类控制"))
        self.humantakeoverCheckBox.setObjectName("humantakeoverCheckBox")
        self.hboxlayout.addWidget(self.humantakeoverCheckBox)

        # 添加 "输出" QCheckBox
        self.output_checkbox = QCheckBox(lt("Side Pane|边窗"), MessageWidget)
        self.output_checkbox.stateChanged.connect(self.toggle_output_checkbox)
        self.output_checkbox.setChecked(False)
        self.output_checkbox.setChecked(True)
        self.hboxlayout.addWidget(self.output_checkbox)


        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.hboxlayout.addItem(spacerItem1)
        self.vboxlayout.addLayout(self.hboxlayout)

        self.hboxlayout1 = QtWidgets.QHBoxLayout()
        self.hboxlayout1.setObjectName("hboxlayout1")

        # self.messageEdit = QtWidgets.QLineEdit(MessageWidget)

        self.messageEdit = QtWidgets.QTextEdit(MessageWidget)
        self.messageEdit.setAcceptRichText(False)  # 设置为不接受富文本，否则格式特别是背景总数很混乱
        self.messageEdit.setFixedHeight(45)  # 假设每行高度为20像素
        # self.messageEdit.setStyleSheet("""
        #     QTextEdit {
        #         border-radius: 2px; /* 设置圆角 */
        #         border: 1px solid #c0c0c0; /* 设置边框 */
        #     }
        #     QTextEdit:focus {
        #         border-color: #61addf; /* 设置焦点时的边框颜色 */
        #     }
        # """)

        self.messageEdit.setPlaceholderText(lt("Emoji: Win + . or Control + Command + Space on Mac", "Emoji: Win + . 如在Mac上:Control + Command + Space"))
        self.messageEdit.setStyleSheet("""

                    QTextEdit {
                    border: 1px solid #c0c0c0; /* 边框颜色 */
                    border-radius: 8px;       /* 圆角半径 */
                    padding: 2px;              /* 内边距 */
                    background-color: #F0F0F0; /* 背景颜色 */
                }
                    QTextEdit:focus {
                        border-color: #146ebe; /* 设置焦点时的边框颜色 */
                    }

                """)

        # 获取当前调色板并修改占位符颜色
        palette = self.messageEdit.palette()
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("gray"))  # 可以改为其他颜色
        self.messageEdit.setPalette(palette)




        self.messageEdit.setObjectName("messageEdit")
        # 连接 textChanged 信号到槽函数
        self.messageEdit.textChanged.connect(self.adjustHeight)
        self.messageEdit.setEnabled(False)
        self.hboxlayout1.addWidget(self.messageEdit)

        self.sendButton = QtWidgets.QPushButton(MessageWidget)
        self.sendButton.setIcon(QtGui.QIcon("images/sendmessage.png"))
        self.sendButton.setObjectName("sendButton")
        self.sendButton.setEnabled(False)
        self.hboxlayout1.addWidget(self.sendButton)
        self.vboxlayout.addLayout(self.hboxlayout1)

        self.retranslateUi(MessageWidget)
        QtCore.QMetaObject.connectSlotsByName(MessageWidget)



    def adjustHeight(self):
        line_height = 20  # 每行高度为20像素
        min_height = 40  # 最小高度为40像素
        max_height = 200  # 最大高度为90像素
        print("in adjustHeight")

        # 计算文本行数
        document = self.messageEdit.document()
        document_height = document.size().height()
        lines = int(document_height / line_height)

        # 计算新的高度
        new_height = max(min_height, min(max_height, lines * line_height))

        # 设置新的高度
        self.messageEdit.setFixedHeight(new_height + 5)

    def retranslateUi(self, MessageWidget):
        MessageWidget.setWindowTitle(QtCore.QCoreApplication.translate("MessageWidget", "Message", None))
        # self.messageBrowser.setHtml(QtCore.QCoreApplication.translate("MessageWidget", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        # "p, li { white-space: pre-wrap; }\n"
        # "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
        # "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600; color:#00008b;\">[14:51] Mauryson :</span><span style=\" color:#00008b;\"> </span><span style=\" color:#000000;\">Salut</span></p>\n"
        # "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; color:#000000;\"><span style=\" font-weight:600; font-style:italic; color:#8b0000;\">[14:52] Natim :</span> Coucou</p></body></html>", None))
        # self.messageBrowser.setHtml(QtCore.QCoreApplication.translate("MessageWidget", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        #                                                      "p, li { white-space: pre-wrap; }\n"
        #                                                      "</style></head><body style=\" font-family:\'Microsoft YaHei\'; font-size:14pt; font-weight:400; font-style:normal;\">"
        #                                                      "</body></html>"))

        file_path = os.path.join(Path(__file__).resolve().parent.parent, "scripts", "aichatmessagepage.html")
        file_path = os.path.join(Path(__file__).resolve().parent.parent, "scripts", "map.html")
        # file_path = os.path.join(Path(__file__).resolve().parent.parent, "scripts", "googlemap19.html")
        # file_path = os.path.join(Path(__file__).resolve().parent.parent, "scripts", "index3.html")
        print(file_path)
        url_string = QUrl.fromLocalFile(file_path)
        # url_string = urllib.request.pathname2url(os.path.join(Path(__file__).resolve().parent.parent, "scripts", "aichatmessagepage.html"))
        print("transform")
        print(url_string)

        # self.output_webview.page().load(mind_url_string)
        print("url_string:", url_string)
        # url_string= QUrl("https://lbsyun.baidu.com/jsdemo.htm#gl-threeLayer")#http://localhost:63342/ai-sns/pytalk/scripts/map.html?_ijt=293b8tbsh3rhl0shc3bu7mof83
        # url_string = QUrl("http://localhost:8900/scripts/googlemap17.html")  #
        url_string = QUrl("http://localhost:8900/scripts/map.html")
        # url_string = QUrl("http://localhost:8900/scripts/baidumaprouteandmovev2trackanivation.html")
        # url_string = QUrl("http://localhost:8900/scripts/googlemap19.html")#https://developers.google.com/maps/documentation/javascript/examples/move-camera-ease
        url_string = QUrl("http://localhost:8900/scripts/googlemap3d.html")
        # url_string = QUrl("http://localhost:8900/scripts/googlemap007bakokok-cbotmove2.html")  # https://developers.google.com/maps/documentation/javascript/examples/move-camera-ease
        # url_string = QUrl("http://localhost:8900/scripts/googlemap20inlondon.html")  # https://developers.google.com/maps/documentation/javascript/examples/move-camera-ease
        # # url_string = QUrl("https://developers.google.com/maps/documentation/javascript/examples/move-camera-ease")  #
        # googlemap007bakokok-cbotmove2.html
        self.messageBrowser.page().load(url_string)
        global channel
        global message_handler
        channel = QWebChannel()
        message_handler = MessageHandler()
        self.message_handler = message_handler
        self.channel = channel
        channel.registerObject("message_handler", message_handler)

        # self.messageBrowser.page().setWebChannel(channel)
        self.messageBrowser.page().setWebChannel(channel)

        message_handler.on_msg_from_js.connect(self.handle_get_msg_from_js)
        message_handler.on_user_request_service.connect(self.enterscene)
        message_handler.on_user_send_im.connect(self.handle_user_send_im)
        message_handler.on_info_load_more.connect(self.handle_info_load_more)
        message_handler.on_load_map_setting.connect(self.handle_load_map_setting)
        message_handler.on_update_map_setting.connect(self.handle_update_map_setting)



        self.fontButton.setText(QtCore.QCoreApplication.translate("MessageWidget", lt("Emoji","表情"), None))
        self.videoButton.setText(QtCore.QCoreApplication.translate("MessageWidget", lt("Attachment","附件"), None))
        self.enterButton.setText(QtCore.QCoreApplication.translate("MessageWidget", lt("Enter","进入"), None))
        self.exitButton.setText(QtCore.QCoreApplication.translate("MessageWidget", lt("Back to Map","返回地图"), None))
        self.sendButton.setText(QtCore.QCoreApplication.translate("MessageWidget", lt("Send","发送"), None))
        # self.sendButton.setShortcut(QtCore.QCoreApplication.translate("MessageWidget", "Return", None))
        self.sendButton.setShortcut(QtGui.QKeySequence(Qt.KeyboardModifier.ControlModifier | Qt.Key.Key_Return))

    def init_document_structure(self):
        # Animation attributes
        self.animation_phase = 0
        self.dot_count = 0
        self.max_dots = 3
        # Spinner character array representing different states of animation
        self.spinner_chars = ['🕐', '🕑', '🕒', '🕓', '🕔', '🕕', '🕖', '🕗', '🕘', '🕙', '🕚', '🕛']

        # Initialize text format for spinner characters
        self.spinner_format = QTextCharFormat()
        self.spinner_format.setForeground(QColor(70, 130, 180))

        # Set up a timer for animation updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(300)


        """Initialize the document structure with static elements."""
        cursor = self.thinking_edit.textCursor()

        # Insert initial dynamic content placeholder
        # cursor.insertText("🕐  正在思考")
        cursor.insertText(" ")
        cursor.insertBlock()  # Move to a new paragraph
        cursor.insertText("\n请稍候...")  # Static text

        # Align entire document to center
        self.thinking_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def update_animation(self):
        """Update only the dynamic content portion of the document."""
        # Compute animation phase and dot count
        self.animation_phase = (self.animation_phase + 1) % len(self.spinner_chars)
        self.dot_count = (self.dot_count + 1) % (self.max_dots + 1)

        # Get the first block of the document (where dynamic content resides)
        cursor = self.thinking_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)

        # Construct the dynamic content
        spinner = self.spinner_chars[self.animation_phase]
        text = f"正在思考{'.' * self.dot_count}"

        # Replace selected text with formatted spinner and default text
        cursor.removeSelectedText()
        cursor.insertText(spinner, self.spinner_format)
        cursor.insertText("  ")  # Insert space separator
        cursor.insertText(text)
