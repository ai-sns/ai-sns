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
from PyQt6.QtWidgets import QCheckBox, QLabel, QSplitter, QTabWidget, QVBoxLayout, QWidget, QMessageBox, QLineEdit, QComboBox, QPushButton
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


from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget,
    QTextEdit, QPushButton, QHBoxLayout, QLabel
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QPixmap
import sys, math
from PyQt6.QtGui import QFontDatabase, QFont
import platform

class SpinnerIcon(QWidget):
    """旋转的加载图标"""
    def __init__(self, size=16, parent=None):
        super().__init__(parent)
        self.angle = 0
        self.icon_size = size
        self.setFixedSize(size, size)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)

    def start(self):
        self.timer.start(50)
        self.show()

    def stop(self):
        self.timer.stop()
        self.hide()

    def rotate(self):
        self.angle = (self.angle + 30) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        center_x, center_y = self.width() / 2, self.height() / 2
        radius = self.icon_size / 4
        for i in range(8):
            angle = math.radians(self.angle + i * 45)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            opacity = 255 - (i * 30)
            color = QColor(0, 120, 215, opacity)
            painter.setPen(QPen(color, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawPoint(int(x), int(y))


class LoadingTabWidget(QWidget):
    """带加载图标的标签"""
    def __init__(self, text, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.spinner = SpinnerIcon(14)
        self.spinner.hide()
        self.label = QLabel(text)
        layout.addWidget(self.spinner)
        layout.addWidget(self.label)

    def start_loading(self):
        self.label.setText("Think    ")
        self.spinner.start()

    def stop_loading(self):
        self.spinner.stop()
        self.label.setText("    Think    ")


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
    on_show_status = pyqtSignal(str)
    on_show_alert = pyqtSignal(str)
    on_command_message = pyqtSignal(str, str, str)
    on_message_checked = pyqtSignal(int, str)
    on_edit_content_message = pyqtSignal(str, str)
    on_message_file_clicked = pyqtSignal(str)
    on_message_open_link = pyqtSignal(str)
    on_msg_from_js = pyqtSignal(str)
    on_user_request_service  = pyqtSignal(str, str)
    on_user_send_im = pyqtSignal(str, str, str)
    on_info_load_more = pyqtSignal(str)
    on_info_load_more_chat = pyqtSignal()
    on_load_map_setting = pyqtSignal()
    on_update_map_setting = pyqtSignal(str,str)
    on_open_url = pyqtSignal(str)
    on_open_sns_profile = pyqtSignal(str)
    on_user_setting = pyqtSignal()
    on_show_game_target = pyqtSignal()
    on_job_setting = pyqtSignal()
    on_user_info = pyqtSignal()
    on_adv_setting = pyqtSignal()
    on_maximize = pyqtSignal()
    on_minimize = pyqtSignal()
    on_mapcfg_setting = pyqtSignal()
    on_close_sns_profile = pyqtSignal()
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

    def show_status_on_map(self,status):
        self.on_show_status.emit(status)

    def show_alert_on_map(self,status):
        self.on_show_alert.emit(status)


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
    def info_load_more_chat(self):
        self.on_info_load_more_chat.emit()

    @pyqtSlot()
    def load_map_setting(self):
        self.on_load_map_setting.emit()

    @pyqtSlot(str,str, result=str)
    def update_map_setting(self, field_name, field_value):
        self.on_update_map_setting.emit(field_name, field_value)

    @pyqtSlot(str, result=str)
    def open_url(self,url):
        self.on_open_url.emit(url)

    @pyqtSlot(str, result=str)
    def open_sns_profile(self,url):
        self.on_open_sns_profile.emit(url)

    @pyqtSlot()
    def user_setting(self):
        print("get from html")
        self.on_user_setting.emit()

    @pyqtSlot()
    def show_game_target(self):
        print("get from html")
        self.on_show_game_target.emit()


    @pyqtSlot()
    def job_setting(self):
        print("get from html")
        self.on_job_setting.emit()

    @pyqtSlot()
    def user_info(self):
        print("get from html")
        self.on_user_info.emit()

    @pyqtSlot()
    def adv_setting(self):
        print("get from html")
        self.on_adv_setting.emit()

    @pyqtSlot()
    def maximize(self):
        print("get from html")
        self.on_maximize.emit()

    @pyqtSlot()
    def minimize(self):
        print("get from html")
        self.on_minimize.emit()


    @pyqtSlot()
    def mapcfg_setting(self):
        print("get from html")
        self.on_mapcfg_setting.emit()


    @pyqtSlot()
    def close_sns_profile(self):
        print("get from html")
        self.on_close_sns_profile.emit()

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






        self.tab_plan = QtWidgets.QWidget()
        self.tab_plan.setObjectName("tab_plan")
        self.tabLayout_plan = QtWidgets.QVBoxLayout(self.tab_plan)
        self.tabLayout_plan.setContentsMargins(0, 0, 0, 0)
        self.plan_edit = QtWidgets.QTextEdit(self.tab_plan)
        # self.set_monospace_font(self.plan_edit,size=9)
        self.plan_edit.setText(lt("💡️ Push the Start button to start","💡️ 请点击开始按钮以开始任务"))
        self.plan_edit.setReadOnly(True)
        self.tabLayout_plan.addWidget(self.plan_edit)
        self.tabWidget.addTab(self.tab_plan, lt("Process","过程"))

        self.tab_res = QtWidgets.QWidget()
        self.tab_res.setObjectName("tab_res")
        self.tabLayout_res = QtWidgets.QVBoxLayout(self.tab_res)
        self.tabLayout_res.setContentsMargins(0, 0, 0, 0)
        self.res_edit = QtWidgets.QTextEdit(self.tab_res)
        self.res_edit.setText(lt("💡️ No Resource Nearby", "💡️ 附近暂无资源"))
        self.res_edit.setReadOnly(True)
        self.tabLayout_res.addWidget(self.res_edit)
        self.tabWidget.addTab(self.tab_res, lt("Resource", "资源"))




        self.tab_thinking = QtWidgets.QWidget()
        self.tab_thinking.setObjectName("tab_thinking")
        self.tabLayout_thinking = QVBoxLayout(self.tab_thinking)
        self.tabLayout_thinking.setContentsMargins(0, 0, 0, 0)
        self.thinking_edit = QtWidgets.QTextEdit(self.tab_thinking)
        self.thinking_edit.setReadOnly(True)
        self.thinking_edit.append(self.get_ai_model_display_name())
        self.tabLayout_thinking.addWidget(self.thinking_edit)
        self.loading_tab = LoadingTabWidget("    Think    ")
        # self.tabWidget.addTab(self.tab_thinking, lt("Think","思考"))
        self.tabWidget.addTab(self.tab_thinking, "")
        self.tabWidget.tabBar().setTabButton(2, self.tabWidget.tabBar().ButtonPosition.LeftSide, self.loading_tab)

        # self.init_document_structure()

        self.tab_profile=None
        # self.tab_profile = QtWidgets.QWidget()
        # self.tab_profile.setObjectName("tab_profile")
        # self.tabLayout_profile = QVBoxLayout(self.tab_profile)
        # self.tabLayout_profile.setContentsMargins(0, 0, 0, 0)
        # self.profile_webview = QWebEngineView(self.tab_profile)
        # self.profile_webview.setObjectName("profile_webview")
        # self.profile_webview.setUrl(QUrl("https://x.com/BillGates"))
        # self.tabLayout_profile.addWidget(self.profile_webview)
        # self.tabWidget.addTab(self.tab_profile, lt("Profile","社交资料"))






        # Create search input
        # textEdit = QLineEdit()
        # textEdit.setPlaceholderText("关键词+回车搜索，空+回车复原")
        # palette = textEdit.palette()
        # palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("gray"))  # 可以改为其他颜色
        # textEdit.setPalette(palette)
        # textEdit.setToolTip("关键字以+++开头表示在搜索结果中继续搜索")
        #
        # tab_widget = QWidget()
        # self.tab_chat_list = ChatList(self, self.ai_chat_cfg)
        # self.tab_chat_list.setObjectName("chat_list")
        # self.tabLayout_chat_list = QVBoxLayout(tab_widget)
        # self.tabLayout_chat_list.addWidget(textEdit)
        # self.tabLayout_chat_list.addWidget(self.tab_chat_list)
        # self.tabLayout_chat_list.setContentsMargins(5, 5, 5, 5)
        # # Connect returnPressed signal to search function
        # textEdit.returnPressed.connect(lambda: self.tab_chat_list.search(textEdit.text()))
        #
        # self.tabWidget.addTab(tab_widget, "聊天历史")
        #
        # Create search input
        # textEdit_label = QLineEdit()
        # textEdit_label.setPlaceholderText("关键词+回车搜索，空+回车复原")
        # palette = textEdit_label.palette()
        # palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("gray"))  # 可以改为其他颜色
        # textEdit_label.setPalette(palette)
        # textEdit_label.setToolTip("关键字以+++开头表示在搜索结果中继续搜索")
        # tab_widget_label = QWidget()
        # self.tab_chat_list_label = ChatListLabel(self, self.ai_chat_cfg)
        # self.tab_chat_list_label.setObjectName("chat_list_label")
        # self.tabLayout_chat_list_label = QVBoxLayout(tab_widget_label)
        # self.tabLayout_chat_list_label.addWidget(textEdit_label)
        # self.tabLayout_chat_list_label.addWidget(self.tab_chat_list_label)
        # self.tabLayout_chat_list_label.setContentsMargins(5, 5, 5, 5)
        # # Connect returnPressed signal to search function
        # textEdit_label.returnPressed.connect(lambda: self.tab_chat_list_label.search(textEdit_label.text()))
        # self.tabWidget.addTab(tab_widget_label, "聊天标签")

        # self.splitter.setSizes([1, ])  # 设置初始状态不显示输出窗口
        # self.splitter.setSizes([300, 1])

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


        self.humantakeoverCheckBox = QCheckBox(lt("Human take control","人类控制"))
        self.humantakeoverCheckBox.setObjectName("humantakeoverCheckBox")
        self.humantakeoverCheckBox.setEnabled(False)
        self.humantakeoverCheckBox.setVisible(False)
        self.hboxlayout.addWidget(self.humantakeoverCheckBox)
        self.humantakeoverCheckBox.setShortcut(QtGui.QKeySequence(Qt.KeyboardModifier.ControlModifier | Qt.Key.Key_H))



        self.talk_type_combo = QComboBox(MessageWidget)
        self.talk_type_combo.addItem(lt("Talk to My AI","指挥我的AI"), "Mine")
        self.talk_type_combo.addItem(lt("Talk to Friend","和朋友交谈"), "Friend")
        self.talk_type_combo.setVisible(False)
        self.hboxlayout.addWidget(self.talk_type_combo)


        self.startButton = QtWidgets.QPushButton(MessageWidget)
        self.startButton.setIcon(QtGui.QIcon("images/startcircle.png"))
        self.startButton.setObjectName("startButton")
        self.startButton.setCursor(Qt.CursorShape.PointingHandCursor)
        self.hboxlayout.addWidget(self.startButton)

        self.map_type_combo = QComboBox(MessageWidget)
        self.map_type_combo.addItem("Google map","Google")
        self.map_type_combo.addItem("Baidu map", "Baidu")
        self.map_type_combo.currentIndexChanged.connect(self.change_map)
        self.map_type_combo.setVisible(False)
        # self.hboxlayout.addWidget(self.map_type_combo)


        self.role_label = QPushButton(MessageWidget)
        role_icon = "images/usermng.png"

        self.role_label.setIcon(QtGui.QIcon(role_icon))

        # 设置按钮的样式表，修改边框颜色
        self.role_label.setStyleSheet("""
                                                            QPushButton {
                                                        border: 0px;                /* 默认无边框 */
                                                        border-radius: 2px;         /* 边框圆角 */
                                                        padding: 2px;               /* 按钮内边距 */
                                                        height: 28px;               /* 按钮高度 */
                                                        width: 28px;                /* 按钮宽度 */
                                                        margin:0px 0px 0px 2px;
                                                    }

                                                        """)
        self.role_label.setCursor(Qt.CursorShape.PointingHandCursor)

        self.role_label.setToolTip("点此处选择角色")
        self.role_label.clicked.connect(self.open_user_config)
        self.role_label.setVisible(False)
        # self.role_label.setFixedWidth(30)
        self.hboxlayout.addWidget(self.role_label)


        self.code_label = QPushButton(MessageWidget)
        code_icon = "images/code.png"

        self.code_label.setIcon(QtGui.QIcon(code_icon))
        self.code_label.setVisible(False)

        # 设置按钮的样式表，修改边框颜色
        self.code_label.setStyleSheet("""
                                                            QPushButton {
                                                        border: 0px;                /* 默认无边框 */
                                                        border-radius: 2px;         /* 边框圆角 */
                                                        padding: 0px;               /* 按钮内边距 */
                                                        height: 28px;               /* 按钮高度 */
                                                        width: 28px;                /* 按钮宽度 */
                                                        margin:0px 5px 0px -5px;
                                                    }

                                                        """)
        self.code_label.setCursor(Qt.CursorShape.PointingHandCursor)

        self.code_label.setToolTip(lt("Call a tool to help AI making decision","调用工具辅助AI决策"))
        self.code_label.clicked.connect(self.open_run_tool_setting)
        # self.code_label.setFixedWidth(30)
        self.hboxlayout.addWidget(self.code_label)





        self.pauseCheckBox = QCheckBox(lt("Pause","暂停"))
        self.pauseCheckBox.setObjectName("pauseCheckBox")
        self.pauseCheckBox.setVisible(False)
        # self.hboxlayout.addWidget(self.pauseCheckBox)

        # 添加 "输出" QCheckBox
        self.output_checkbox = QCheckBox(lt("Side Pane|边窗"), MessageWidget)
        self.output_checkbox.stateChanged.connect(self.toggle_output_checkbox)
        self.output_checkbox.setChecked(False)
        self.output_checkbox.setVisible(False)

        self.hboxlayout.addWidget(self.output_checkbox)
        self.output_checkbox.setShortcut(QtGui.QKeySequence(Qt.KeyboardModifier.ControlModifier | Qt.Key.Key_P))


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

        self.messageEdit.setPlaceholderText(lt("Input @ to get command list","输入@可获取常用命令列表"))
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
        self.messageEdit.setVisible(False)
        self.hboxlayout1.addWidget(self.messageEdit)

        self.sendButton = QtWidgets.QPushButton(MessageWidget)
        self.sendButton.setIcon(QtGui.QIcon("images/sendmessage.png"))
        self.sendButton.setObjectName("sendButton")
        self.sendButton.setEnabled(False)
        self.sendButton.setVisible(False)
        self.hboxlayout1.addWidget(self.sendButton)

        self.upButton = QPushButton(MessageWidget)
        self.upButton.setObjectName("upButton")
        self.hboxlayout1.addWidget(self.upButton)
        self.upButton.setMinimumSize(1, 1)
        self.upButton.setMaximumSize(1, 1)

        self.downButton = QPushButton(MessageWidget)
        self.downButton.setObjectName("downButton")
        self.hboxlayout1.addWidget(self.downButton)
        self.downButton.setMinimumSize(1, 1)
        self.downButton.setMaximumSize(1, 1)




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
        url_string_baidu = QUrl("http://localhost:8900/scripts/map.html")
        # url_string = QUrl("http://localhost:8900/scripts/baidumaprouteandmovev2trackanivation.html")
        # url_string = QUrl("http://localhost:8900/scripts/googlemap19.html")#https://developers.google.com/maps/documentation/javascript/examples/move-camera-ease
        url_string_google = QUrl("http://localhost:8900/scripts/googlemap3d.html")
        # url_string = QUrl("http://localhost:8900/scripts/googlemap007bakokok-cbotmove2.html")  # https://developers.google.com/maps/documentation/javascript/examples/move-camera-ease
        # url_string = QUrl("http://localhost:8900/scripts/googlemap20inlondon.html")  # https://developers.google.com/maps/documentation/javascript/examples/move-camera-ease
        # # url_string = QUrl("https://developers.google.com/maps/documentation/javascript/examples/move-camera-ease")  #
        # googlemap007bakokok-cbotmove2.html
        if self.ai_chat_cfg.map_type == "0":
            url_string = url_string_google
        else:
            url_string = url_string_baidu
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
        message_handler.on_info_load_more_chat.connect(self.handle_info_load_more_chat)
        message_handler.on_load_map_setting.connect(self.handle_load_map_setting)
        message_handler.on_update_map_setting.connect(self.handle_update_map_setting)
        message_handler.on_open_url.connect(self.handle_open_url)
        message_handler.on_open_sns_profile.connect(self.handle_open_sns_profile)
        message_handler.on_user_setting.connect(self.handle_user_setting)
        message_handler.on_show_game_target.connect(self.handle_show_game_target)
        message_handler.on_job_setting.connect(self.handle_job_setting)
        message_handler.on_user_info.connect(self.handle_user_info)
        message_handler.on_adv_setting.connect(self.handle_adv_setting)
        message_handler.on_maximize.connect(self.handle_maximize)
        message_handler.on_minimize.connect(self.handle_minimize)
        message_handler.on_mapcfg_setting.connect(self.handle_mapcfg_setting)
        message_handler.on_close_sns_profile.connect(self.handle_close_sns_profile)


        self.fontButton.setText(QtCore.QCoreApplication.translate("MessageWidget", lt("Emoji","表情"), None))
        self.videoButton.setText(QtCore.QCoreApplication.translate("MessageWidget", lt("Attachment","附件"), None))
        self.enterButton.setText(QtCore.QCoreApplication.translate("MessageWidget", lt("Enter","进入"), None))
        self.startButton.setText(QtCore.QCoreApplication.translate("MessageWidget", lt("Start","开始"), None))
        self.sendButton.setText(QtCore.QCoreApplication.translate("MessageWidget", lt("Send","发送"), None))
        # self.sendButton.setShortcut(QtCore.QCoreApplication.translate("MessageWidget", "Return", None))
        self.sendButton.setShortcut(QtGui.QKeySequence(Qt.KeyboardModifier.ControlModifier | Qt.Key.Key_Return))
        self.upButton.setShortcut(QtGui.QKeySequence(Qt.KeyboardModifier.ControlModifier | Qt.Key.Key_Up))
        self.downButton.setShortcut(QtGui.QKeySequence(Qt.KeyboardModifier.ControlModifier | Qt.Key.Key_Down))

        self.output_checkbox.setChecked(True)

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
        # cursor.insertText("\n请稍候...")  # Static text
        cursor.insertText("\n ")
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
        text = f"正在思考，请稍候{'.' * self.dot_count}"

        # Replace selected text with formatted spinner and default text
        cursor.removeSelectedText()
        cursor.insertText(spinner, self.spinner_format)
        cursor.insertText("  ")  # Insert space separator
        cursor.insertText(text)

    def set_monospace_font(self,widget, size=12):
        """
        为指定的 PyQt 控件设置跨平台、中英文兼容的等宽字体。
        :param widget: 任意 QWidget (QTextEdit, QLabel, QPlainTextEdit, 等)
        :param size: 字号大小
        """
        system_name = platform.system()

        # Step 1️⃣ - 获取系统默认等宽字体
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        font.setPointSize(size)

        # Step 2️⃣ - 根据操作系统增加 fallback（支持中文）
        if system_name == "Windows":
            font.setFamily("Consolas, Courier New, 微软雅黑, Microsoft YaHei, monospace")
        elif system_name == "Darwin":  # macOS
            font.setFamily("Menlo, PingFang SC, monospace")
        else:  # Linux or others
            font.setFamily("DejaVu Sans Mono, Noto Sans Mono CJK SC, monospace")

        widget.setFont(font)

    def get_ai_model_display_name(self):
        """
        获取AI模型显示名称，格式为"🧠 {provider} {model_name}"
        """
        try:
            from db.DBFactory import query_AgentCfg

            # 获取账户信息
            snsaccount = self.aichatcfg_record.account
            agent_cfg = query_AgentCfg(snsaccount=snsaccount)

            # 获取默认模型
            if agent_cfg and agent_cfg.defaultmodel:
                defaultmodel = agent_cfg.defaultmodel
                return f"🧠 {defaultmodel}"
            else:
                return "🧠 OpenAI gpt-4o-mini"  # 默认值
        except Exception as e:
            print(f"获取AI模型名称时出错: {e}")
            return "🧠 OpenAI gpt-4o-mini"  # 出错时的默认值

    def update_ai_model_display_name(self):
        """
        安全高效地更新 thinking_edit 第一行的 AI 模型名称
        自动判断是否需要换行，保持文档结构一致
        """
        doc = self.thinking_edit.document()
        block = doc.firstBlock()

        if not block.isValid():
            return

        cursor = QtGui.QTextCursor(block)
        cursor.select(QtGui.QTextCursor.BlockUnderCursor)

        new_first_line = self.get_ai_model_display_name()

        # 获取下一个 block
        next_block = block.next()

        # 如果还有下一行，说明第一行本来有换行符 → 不额外加 '\n'
        # 如果没有下一行，说明是单行文本（例如 setPlainText）→ 需要手动补 '\n'
        cursor.insertText(new_first_line)

    def update_resource_display(self):
        """
        更新资源显示内容，包括工具列表、人员名单和地址列表
        """
        # 获取各类资源数据
        tool_list = self.get_tool_list()
        people_list = self.get_people_list()
        place_list = self.get_place_list()

        # 格式化内容
        formatted_content = self._format_resource_content(tool_list, people_list, place_list)+"\n"

        # 更新 res_edit 内容
        self.res_edit.setPlainText(formatted_content)

    def _format_resource_content(self, tool_list, people_list, place_list):
        """
        格式化资源内容显示
        """
        content = ""

        # 格式化工具列表
        if tool_list:
            content += f"🌐 服务列表（共 {len(tool_list)} 项）\n"
            content += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

            for i, tool in enumerate(tool_list):
                # 工具ID和名称
                content += f"#{tool.get('id', '')} {tool.get('name', '')}\n"


                # 地理坐标信息（如果lng,lat有值且不为0）
                lng = tool.get('lng', 0)
                lat = tool.get('lat', 0)
                if lng and lat and lng != 0 and lat != 0:
                    # 格式化坐标，最多8位小数，去除尾随零
                    formatted_lng = f"{lng:.8g}"
                    formatted_lat = f"{lat:.8g}"
                    content += f"📍 坐标：{formatted_lng}, {formatted_lat}\n"
                elif 'place' in tool and tool['place']:
                    content += f"🌍 位置：{tool['place']}\n"

                # 描述信息
                if 'description' in tool and tool['description']:
                    content += f"💬 描述：{tool['description']}\n"

                # 地址信息
                if 'address' in tool and tool['address'] and tool['address'] != "Not needed":
                    content += f"🔗 地址：{tool['address']}\n"

                # 类型和方法信息
                type_info = tool.get('type', '')
                method_info = tool.get('method', '')

                # 参数信息
                param_info = ""
                if 'parameter' in tool and tool['parameter']:
                    if isinstance(tool['parameter'], dict):
                        param_strs = [f"{k}={v}" for k, v in tool['parameter'].items()]
                        param_info = f"({', '.join(param_strs)})" if param_strs else ""
                    else:
                        param_info = f"({tool['parameter']})" if tool['parameter'] != "None" else ""

                content += f"⚙️ 类型：{type_info} ｜ 方法：{method_info}{param_info}\n"

                # 分隔线（除了最后一个工具）
                if i < len(tool_list) - 1:
                    content += "\n──────────────────────────\n\n"

            content += "\n\n"

        # 格式化人员名单
        if people_list:
            content += f"🧑‍🤝‍🧑 人员名单（共 {len(people_list)} 位）\n"
            content += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

            for i, person in enumerate(people_list):
                # 姓名和职业
                nick_name = person.get('nick_name', '')
                profession = person.get('profession', '')
                content += f"🧑‍ {nick_name} ｜ 👩‍💻 {profession}\n"

                # 位置信息
                location = person.get('location', [])
                if location and len(location) >= 2:
                    lng, lat = location[0], location[1]
                    # 简化城市信息

                    # 格式化经纬度，最多显示8位小数，不补零
                    formatted_lng = f"{lng:.8f}".rstrip('0').rstrip('.')
                    formatted_lat = f"{lat:.8f}".rstrip('0').rstrip('.')
                    content += f"📍 位置：{formatted_lng}, {formatted_lat}\n"

                # 账户信息
                account = person.get('account', '')
                if account:
                    content += f"💬 account: {account}\n"

                # SNS信息
                sns_url = person.get('sns_url', '')
                if sns_url:
                    content += f"🔗 sns: {sns_url}\n"

                # ID信息
                nation_id = person.get('nation_id', '')
                if nation_id:
                    content += f"🆔 nation_id: {nation_id}\n"

                # 简介信息
                profile = person.get('profile', '')
                if profile:
                    content += f"📝 profile: {profile}\n"

                # 分隔线（除了最后一个人）
                if i < len(people_list) - 1:
                    content += "\n──────────────────────────\n\n"

            content += "\n\n"

        # 格式化地址列表
        if place_list:
            content += f"🗺️ 地址列表（共 {len(place_list)} 处）\n"
            content += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

            for i, place in enumerate(place_list):
                # 地点名称
                place_name = place.get('place_name', '')
                content += f"🏞️ {place_name}\n"

                # 位置坐标
                position = place.get('place_position', [])
                if position and len(position) >= 2:
                    lng, lat = position[0], position[1]
                    # 格式化经纬度，最多显示8位小数，不补零
                    formatted_lng = f"{lng:.8f}".rstrip('0').rstrip('.')
                    formatted_lat = f"{lat:.8f}".rstrip('0').rstrip('.')
                    content += f"📍 {formatted_lng}, {formatted_lat}\n"

                # 描述信息
                description = place.get('description', '')
                if description:
                    content += f"📖 {description}\n"

                # 分隔线（除了最后一个地点）
                if i < len(place_list) - 1:
                    content += "\n──────────────────────────\n\n"

            content += "\n"

        return content.strip()
