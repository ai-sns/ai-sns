import os
import webbrowser

import PyQt6
from PyQt6 import QtWidgets
from PyQt6.QtCore import QDate, QSize, Qt, QRect, pyqtSignal, QEvent
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QPen, QPainterPath, QIntValidator, QMouseEvent
from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
                             QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
                             QListView, QListWidget, QListWidgetItem, QPushButton, QSpinBox,
                             QStackedWidget, QVBoxLayout, QWidget, QDialogButtonBox, QRadioButton, QFileDialog, QSizePolicy, QMessageBox, QTextEdit, QPlainTextEdit, QFrame)
from db.DBFactory import add_AiChatCfg, query_AiChatCfg, query_AiChatCfg_All, update_AiChatCfg, delete_AiChatCfg
from db.DBFactory import add_AgentCfg,query_AgentCfg,query_AgentCfg_All,update_AgentCfg,delete_AgentCfg
from agentconfigdialog import ConfigDialog as AgentConfigDialog
import configdialog_rc
import datetime
import random
import string

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QFrame, QWidget, QSizePolicy
from PyQt6.QtGui import QPixmap, QMouseEvent
import subprocess
import platform

# from datetime import datetime
from i18n import lt
class ImageSelector(QWidget):
    selected = PyQt6.QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()

        # Paths to images - 动态读取 scripts/avatar3d 目录下的所有 PNG 文件
        avatar3d_dir = os.path.join('scripts', 'avatar3d')
        if os.path.exists(avatar3d_dir):
            self.images = sorted([
                os.path.join(avatar3d_dir, f)
                for f in os.listdir(avatar3d_dir)
                if f.lower().endswith('.png')
            ])
        else:
            self.images = []
        self.current_index = 0
        self.selected_index = None

        # Main layout
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Navigation buttons
        self.prev_button = self.create_navigation_button("◀")
        self.next_button = self.create_navigation_button("▶")

        # Connect buttons to slots
        self.next_button.clicked.connect(self.show_next_images)
        self.prev_button.clicked.connect(self.show_previous_images)

        # Image grid setup
        self.image_grid = QGridLayout()
        self.grid_frame = QFrame()
        self.grid_frame.setLayout(self.image_grid)
        self.grid_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #c0c0c0;
                background: white;
                
            }
        """)
        self.grid_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Image labels
        self.labels = [QLabel() for _ in range(5)]
        for i, label in enumerate(self.labels):
            self.image_grid.addWidget(label, i // 5, i % 5)
            label.mousePressEvent = self.create_label_click_handler(i)
            label.setStyleSheet("border: 2px solid transparent;")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Assemble main layout
        self.main_layout.addWidget(self.prev_button)
        self.main_layout.addWidget(self.grid_frame)
        self.main_layout.addWidget(self.next_button)
        self.setLayout(self.main_layout)


        # Initial image display
        self.update_images()

    def create_navigation_button(self, symbol: str) -> QPushButton:
        """Create and style a navigation button."""
        button = QPushButton(symbol)
        button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        button.setStyleSheet("""
            QPushButton {
                font-size: 24px;
                min-width: 20px;
                border: none;
                background: #f0f0f0;
            }
            QPushButton:hover {
                background: #e0e0e0;
            }
        """)
        return button

    def create_label_click_handler(self, index: int):
        """Create a handler for mouse press events on image labels."""
        def handler(event: QMouseEvent):
            if event.button() == Qt.MouseButton.LeftButton:
                if event.type() == QEvent.Type.MouseButtonDblClick:  # Handle double-click
                    self.show_fullsize_image(self.current_index + index)
                else:  # Handle single-click
                    self.select_image(index)
        return handler

    def update_imagesbak(self):
        """Update displayed images."""
        for i, label in enumerate(self.labels):
            image_index = self.current_index + i
            # Check if image_index is within bounds
            if image_index < len(self.images):
                # Load the original image
                pixmap = QPixmap(self.images[image_index])
                # Scale the pixmap to ensure the short edge is 60, expanding the longer edge
                scaled_pixmap = pixmap.scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                # Crop the pixmap to a 60x60 region starting at the center
                width = scaled_pixmap.width()
                height = scaled_pixmap.height()
                x_offset = (width - 60) // 2
                y_offset = (height - 60) // 2
                cropped_pixmap = scaled_pixmap.copy(x_offset, y_offset, 60, 60)
                # Set the cropped pixmap to the label
                label.setPixmap(cropped_pixmap)
                label.setScaledContents(False)
                # Highlight selected image
                border_color = "#146ebe" if self.selected_index == image_index else "transparent"
                label.setStyleSheet(f"border: 2px solid {border_color};")
            else:
                # Clear label if no image
                label.clear()
                label.setStyleSheet("border: 2px solid transparent;")

    def update_images(self):
        """更新显示的图片，并按要求进行缩放和裁剪。"""
        for i, label in enumerate(self.labels):
            image_index = self.current_index + i
            if image_index < len(self.images):
                # 加载原始图片
                pixmap = QPixmap(self.images[image_index])

                # 计算缩放大小，短边固定为60
                if pixmap.width() < pixmap.height():
                    # 横向图片 - 宽度固定为60，高度按比例缩放
                    scaled_size = QSize(60, int(60 * pixmap.height() / pixmap.width()))
                else:
                    # 纵向图片 - 高度固定为60，宽度按比例缩放
                    scaled_size = QSize(int(60 * pixmap.width() / pixmap.height()), 60)

                # 对图片进行平滑缩放
                scaled_pixmap = pixmap.scaled(
                    scaled_size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )

                # 创建60x60裁剪区域，纵向从上往下，横向居中
                crop_rect = QRect(
                    (scaled_pixmap.width() - 60) // 2,  # 横向居中
                    0,  # 纵向从上开始
                    60, 60
                )
                cropped_pixmap = scaled_pixmap.copy(crop_rect)

                # 设置最终的pixmap
                label.setPixmap(cropped_pixmap)
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)

                # 突出显示选中的图片
                border_color = "#146ebe" if self.selected_index == image_index else "transparent"
                label.setStyleSheet(f"border: 2px solid {border_color};")
                # label.setFixedHeight(20)
            else:
                label.clear()
                label.setStyleSheet("border: 2px solid transparent;")

    def select_image(self, label_index: int):
        """Select image and emit signal."""
        image_index = self.current_index + label_index
        if image_index < len(self.images):
            self.selected_index = image_index
            self.selected.emit(self.images[image_index])
            self.update_images()

    def show_next_images(self):
        """Show next set of images if possible."""
        if self.current_index + 5 < len(self.images):
            self.current_index += 5
            self.update_images()

    def show_previous_images(self):
        """Show previous set of images if possible."""
        if self.current_index - 5 >= 0:
            self.current_index -= 5
            self.update_images()

    def show_image(self, index):
        """
        Show the image at the specified index, ensuring the correct set of images
        is displayed and the target image is selected.

        :param index: The index of the image to display and select.
        """
        if 0 <= index < len(self.images):
            # Calculate the appropriate current index to ensure the target image is visible
            self.current_index = (index // 5) * 5

            # Update the images displayed
            self.update_images()

            # Ensure the image at the specified index is selected
            # Calculate the local label index within the current subset of visible images
            local_label_index = index % 5
            self.select_image(local_label_index)


    def show_fullsize_image(self, image_index: int):
        """Open the selected image in the system's default image viewer."""
        if 0 <= image_index < len(self.images):
            image_path = self.images[image_index]
            # Determine the platform and open the image using the default viewer
            try:
                if platform.system() == "Windows":
                    subprocess.run(["start", image_path], shell=True)
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", image_path])
                else:  # Assume Linux
                    subprocess.run(["xdg-open", image_path])
            except Exception as e:
                print(f"Failed to open image: {str(e)}")



class ConfigDialog(QDialog):
    configured = pyqtSignal(str,str,str,str)
    connectcancel = pyqtSignal(str)

    def __init__(self, parent=None, ai_chat_cfg=None):
        super(ConfigDialog, self).__init__(parent)
        print("initialing.....")
        self.contentsWidget = QListWidget()
        self.contentsWidget.setViewMode(QListView.ViewMode.IconMode)
        self.contentsWidget.setIconSize(QSize(96, 84))
        self.contentsWidget.setMovement(QListView.Movement.Static)
        self.contentsWidget.setMaximumWidth(128)
        self.contentsWidget.setSpacing(12)
        # self.contentsWidget.setStyleSheet("QListWidget{margin-top: -150px; border: solid 1px red;}")

        self.ai_chat_cfg = ai_chat_cfg
        self.app =parent

        self.generalPage = GeneralPage(self.ai_chat_cfg,parent=self.app)
        self.userinfoPage = UserInfoPage(self.ai_chat_cfg)
        self.connectionPage = ConnectionPage(self.ai_chat_cfg)
        self.securityPage = SecurityPage(self.ai_chat_cfg)

        self.pagesWidget = QStackedWidget()
        self.pagesWidget.addWidget(self.generalPage)
        self.pagesWidget.addWidget(self.userinfoPage)
        self.pagesWidget.addWidget(self.connectionPage)
        self.pagesWidget.addWidget(self.securityPage)

        closeButton = QPushButton("Close")

        self.createIcons()#创建contentsWidget的列表，工具列表
        self.contentsWidget.setCurrentRow(0)

        closeButton.clicked.connect(self.close)



        horizontalLayout = QHBoxLayout()
        horizontalLayout.addWidget(self.contentsWidget)
        horizontalLayout.addWidget(self.pagesWidget, 1)

        buttonsLayout = QHBoxLayout()
        buttonsLayout.addStretch(1)
        buttonsLayout.addWidget(closeButton)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(horizontalLayout)
        mainLayout.addStretch(1)
        mainLayout.addSpacing(12)
        # mainLayout.addLayout(buttonsLayout)

        # Add OK and Cancel buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setText("确定")
        cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_button.setText("取消")
        button_box.accepted.connect(self.accept_close)
        button_box.rejected.connect(self.reject_close)

        mainLayout.addWidget(button_box)

        self.setLayout(mainLayout)

        self.setWindowTitle("Ai漫游地球设置")

    def accept_close(self):
        print("accept")

        # generalpage
        nationid = self.generalPage.useridEdit.text()
        if not nationid:  # Check if plugins are empty
            QMessageBox.warning(self, "警告", "用户ID不能为空。")
            return
        userpassword = self.generalPage.userpasswordEdit.text()
        if not userpassword:  # Check if plugins are empty
            QMessageBox.warning(self, "警告", "用户密码不能为空。")
            return

        account = self.generalPage.accountEdit.text()
        if not account:  # Check if plugins are empty
            QMessageBox.warning(self, "警告", "帐号不能为空。")
            return
        password = self.generalPage.passwordEdit.text()
        if not password:  # Check if plugins are empty
            QMessageBox.warning(self, "警告", "密码不能为空。")
            return


        nickname = self.userinfoPage.nicknameEdit.text()
        if not nickname:  # Check if plugins are empty
            QMessageBox.warning(self, "警告", "昵称不能为空。")
            return
        sign = self.userinfoPage.signEdit.toPlainText()
        if not sign:  # Check if plugins are empty
            QMessageBox.warning(self, "警告", "自我介绍不能为空。")
            return
        status = self.generalPage.statusCombo.currentText()

        """
               当QComboBox的选项变化时调用此方法
               :param index: 当前选中项的索引
               """
        # 获取当前选中的选项文本
        cur_nick_name = self.generalPage.cur_nick_name
        selected_name = self.generalPage.serverCombo.currentText()
        if selected_name=="N/A" and self.generalPage.humantakeoverYesRadio.isChecked()==False:
            QMessageBox.warning(self, "警告", "必须指定该帐号属于哪个Agent或设置为人类接管帐号。")
            return

        if self.generalPage.humantakeoverYesRadio.isChecked() == True:
            humantakeover=1
        else:
            humantakeover=0


        if self.generalPage.ai_chat_cfg:
            agent_belonged=query_AgentCfg(snsaccount= self.generalPage.ai_chat_cfg.account)
        else:
            agent_belonged=None

        if agent_belonged:
            update_AgentCfg(agent_belonged.id, snsaccount="N/A", snsnickname="N/A")
        if selected_name != "N/A":
            new_agent_belonged = query_AgentCfg(name=selected_name)
            self.generalPage.agent_belonged=new_agent_belonged
            if self.generalPage.ai_chat_cfg:
                snsaccount = self.generalPage.ai_chat_cfg.account
                snsnickname = self.generalPage.ai_chat_cfg.nickname
                update_AgentCfg(new_agent_belonged.id, snsaccount=snsaccount, snsnickname=snsnickname)

        # userinfopage

        nickname=self.userinfoPage.nicknameEdit.text()

        sign=self.userinfoPage.signEdit.toPlainText()

        sns_url=self.userinfoPage.snsUrlEdit.text()

        # 获取头像文件名（只保存文件名，不含路径）
        avatar = self.generalPage.avatar

        # update_AiChatCfg(1, name, memo, borndate, borncontry, language, gender, joinfederation, syncfederation, specialization, plugins, kms, prompt, snsaccount, islimittotalmessage, islimitmessagepp, totalmessages, ppmessages, readfile, writefile, deletefile, execfile, autorunrounds)
        if self.ai_chat_cfg == None:
            print("ai chat cfg not found")
            return False

        else:
            idstr = self.ai_chat_cfg.user_id
            update_AiChatCfg(self.ai_chat_cfg.id, account = account, password = password, nickname = nickname, sign = sign, status = status,humantakeover=humantakeover, sns_url=sns_url,nationid=nationid,nationpassword=userpassword, avatar=avatar)
            tool_box_item = self.app.toolBox_AiChat.findChild(QWidget, idstr)
            self.app.toolBox_AiChat.setItemText(self.app.toolBox_AiChat.indexOf(tool_box_item),lt("Explore the Earth", "漫游地球", "漫游地球") + "-" +nickname)

        if status=="离线":
            status ="0"
        elif humantakeover==1:
            status = "2"
        else:#在线
            status = "1"

        # 上传地图标记图片（avatar_map）到服务器
        if self.generalPage.avatar_map and os.path.exists(self.generalPage.avatar_map):
            try:
                from urllib.parse import urljoin
                import requests
                api_base_url = "http://www.ai-sns.org"
                avatar_upload_url = urljoin(api_base_url, "/api/upload_avatar/")

                # 上传地图标记图片（带_map后缀的compressed_image）
                avatar_map_file_path = self.generalPage.avatar_map
                print(f"Uploading avatar map: {avatar_map_file_path}")
                with open(avatar_map_file_path, "rb") as avatar_file:
                    files = {"avatar_file": avatar_file}
                    data = {"nation_id": self.ai_chat_cfg.nationid}
                    response = requests.post(avatar_upload_url, files=files, data=data)
                    if response.status_code != 200:
                        print(f"Failed to upload avatar: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"Error uploading avatar: {str(e)}")

        # 提交数据到服务器
        try:
            import requests
            from urllib.parse import urljoin

            # 准备提交到服务器的数据
            api_base_url = "http://www.ai-sns.org"
            update_user_url = urljoin(api_base_url, "/api/update-user/")

            # 构造更新用户数据
            update_data = {
                "nation_id": nationid,
                "password": userpassword,
                "account": account,
                "nick_name": nickname,
                "avatar_3d": self.userinfoPage.avatar3d if self.userinfoPage.avatar3d else "imcbot.glb",
                "profile": sign,
                "sns_url": sns_url
            }

            # 发送数据到服务器
            response = requests.post(update_user_url, data=update_data)

            if response.status_code not in [200, 201]:
                print(f"Failed to update user: {response.status_code} - {response.text}")
                title = lt("Fail", "失败")
                content = f"Submit fail: {response.status_code} - {response.text}"
                QMessageBox.critical(self, title, content, QMessageBox.Ok)
        except Exception as e:
            print(f"Error updating user: {str(e)}")
            title = lt("Error", "错误")
            content = f"Error updating user: {str(e)}"
            QMessageBox.critical(self, title, content, QMessageBox.Ok)

        self.configured.emit(self.ai_chat_cfg.user_id, account, password,status)

        self.app.map_message_box.update_ai_model_display_name()
        self.app.map_message_box.send_python_setting_changed("nick_name",nickname)
        self.app.map_message_box.send_python_setting_changed("profile", sign)

        self.accept()
        self.close()

    def reject_close(self):
        print("reject")
        self.close()

    def showEvent(self, event):
        agent_belonged=None
        if self.ai_chat_cfg is not None:
            agent_belonged = query_AgentCfg(snsaccount=self.ai_chat_cfg.account)

        cur_nick_name = ""

        if agent_belonged:
            cur_nick_name = agent_belonged.name

        if cur_nick_name == "":
            self.generalPage.serverCombo.setCurrentText("N/A")
        else:
            self.generalPage.serverCombo.setCurrentText(cur_nick_name)


        super().showEvent(event)

    def changePage(self, current, previous):
        if not current:
            current = previous

        self.pagesWidget.setCurrentIndex(self.contentsWidget.row(current))

    def createIcons(self):
        configButton = QListWidgetItem(self.contentsWidget)
        configButton.setIcon(QIcon(':/images/config.png'))
        configButton.setText(lt("Account setting","账号配置"))
        configButton.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)
        configButton.setFlags(Qt.ItemFlag.ItemIsSelectable |  Qt.ItemFlag.ItemIsEnabled)

        techButton = QListWidgetItem(self.contentsWidget)
        techButton.setIcon(QIcon('images/technique.png'))
        techButton.setText(lt("User Setting","个人资料"))
        techButton.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)
        techButton.setFlags(Qt.ItemFlag.ItemIsSelectable |  Qt.ItemFlag.ItemIsEnabled)

        queryButton = QListWidgetItem(self.contentsWidget)
        queryButton.setIcon(QIcon(':/images/update.png'))
        queryButton.setText("连接配置")
        queryButton.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)
        queryButton.setFlags(Qt.ItemFlag.ItemIsSelectable |  Qt.ItemFlag.ItemIsEnabled)
        queryButton.setHidden(True)#暂时先隐藏

        updateButton = QListWidgetItem(self.contentsWidget)
        updateButton.setIcon(QIcon(':/images/query.png'))
        updateButton.setText(lt("Security","隐私安全"))
        updateButton.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)
        updateButton.setFlags(Qt.ItemFlag.ItemIsSelectable |  Qt.ItemFlag.ItemIsEnabled)

        self.contentsWidget.adjustSize()
        self.contentsWidget.setFixedHeight(500)
        self.contentsWidget.currentItemChanged.connect(self.changePage)

    def generate_random_id(self):
        # 生成随机字母ID，使用大写字母
        random_id = ''.join(random.choices(string.ascii_uppercase, k=2))
        # 获取当前时间
        current_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        # 生成随机数
        random_number = ''.join(random.choices(string.digits, k=5))
        # 组合生成的ID
        generated_id = random_id + current_time + random_number
        return generated_id

class GeneralPage(QWidget):
    def __init__(self, ai_chat_cfg, parent=None):
        super(GeneralPage, self).__init__(parent)
        self.ai_chat_cfg = ai_chat_cfg
        self.app =parent
        self.avatar = ""  # 只保存文件名，不含路径
        self.avatar_map = ""  # 保存带_map后缀的地图标记图片完整路径

        self.avatar_label = ClickableAvatarLabel()
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar_label.setFixedSize(70, 70)

        # 创建水平布局
        hLayout = QHBoxLayout()
        hLayout.addStretch()  # 在 avatar_label 前面添加伸展因子，将其推到水平中心
        hLayout.addWidget(self.avatar_label)
        hLayout.addStretch()  # 在 avatar_label 后面再添加一个伸展因子 必须前后都有

        self.avatar_label.clicked.connect(self.uploadAvatar)

        packagesGroup = QGroupBox("基本资料")

        self.useridLabel = QLabel("用户ID:")
        self.useridEdit = QLineEdit()
        self.userpasswordLabel = QLabel("用户密码:")
        self.userpasswordEdit = QLineEdit()
        self.userpasswordEdit.setEchoMode(QLineEdit.EchoMode.Password)


        self.accountLabel = QLabel("XMPP账号:")
        self.accountEdit = QLineEdit()
        # self.accountEdit.setReadOnly(True)
        self.passwordLabel = QLabel("XMPP密码:")
        self.passwordEdit = QLineEdit()
        self.passwordEdit.setEchoMode(QLineEdit.EchoMode.Password)


        self.statusLabel = QLabel("在线状态:")
        self.statusCombo = QComboBox()
        self.statusCombo.addItem("在线")
        self.statusCombo.addItem("离线")


        if ai_chat_cfg != None:
            self.useridEdit.setText(ai_chat_cfg.nationid)  # Assuming index 0 represents self.nameEdit text
            self.userpasswordEdit.setText(ai_chat_cfg.nationpassword)  # Assuming index 1 represents memoEdit text
            self.accountEdit.setText(ai_chat_cfg.account)  # Assuming index 0 represents self.nameEdit text
            self.passwordEdit.setText(ai_chat_cfg.password)  # Assuming index 1 represents memoEdit text
            self.statusCombo.setCurrentText(ai_chat_cfg.status)  # Assuming index 4 represents self.self.languageCombo  current text

            # 加载保存的头像
            if ai_chat_cfg.avatar:
                # ai_chat_cfg.avatar 现在只保存文件名，需要拼接完整路径
                # 兼容旧数据：如果包含路径，提取文件名
                avatar_filename = os.path.basename(ai_chat_cfg.avatar)
                avatar_path = os.path.join('images', 'avatars', avatar_filename)

                if os.path.exists(avatar_path):
                    # 设置 avatar 文件名（重要！）
                    self.avatar = avatar_filename

                    pixmap = QPixmap(avatar_path)
                    self.avatar_label.setPixmap(pixmap)

                    # 同时生成 avatar_map 路径
                    name_without_ext, file_extension = os.path.splitext(avatar_filename)
                    map_filename = f"{name_without_ext}_map{file_extension}"
                    self.avatar_map = os.path.abspath(os.path.join('images', 'avatars', map_filename))
                else:
                    # 如果找不到用户头像，则显示默认头像
                    filename = os.path.join('images', 'avatar.png')
                    pixmap = QPixmap(filename)
                    self.avatar_label.setPixmap(pixmap)
            else:
                # 没有用户头像，显示默认头像
                filename = os.path.join('images', 'avatar.png')
                pixmap = QPixmap(filename)
                self.avatar_label.setPixmap(pixmap)
            agent_belonged = query_AgentCfg(snsaccount=ai_chat_cfg.account)
        else:
            agent_belonged = None

        # 根据nationid是否为空设置useridEdit的只读属性
        if ai_chat_cfg and ai_chat_cfg.nationid:
            self.useridEdit.setReadOnly(True)
        else:
            self.useridEdit.setReadOnly(False)

        layout_belong_to_agent = QHBoxLayout()
        belong_to_agent_title = QLabel("还没有帐号?")
        self.belong_to_agent = ClickableLabel(agent_belonged, self)
        self.belong_to_agent.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)  # 设置该标签顶到最左边

        layout_belong_to_agent.addWidget(belong_to_agent_title)
        layout_belong_to_agent.addWidget(self.belong_to_agent)


        self.agent_belonged=agent_belonged


        cur_nick_name = ""
        if agent_belonged:
            cur_nick_name = agent_belonged.name
        else:
            cur_nick_name = ""

        self.sns_nick_name_list = []

        configGroup = QGroupBox(lt("Powered by the Agent below:","由以下Agent驱动"))

        self.serverLabel = QLabel("Agent:")
        self.serverCombo = QComboBox()
        ai_chat_records = query_AgentCfg_All()
        self.serverCombo.addItem("N/A")
        self.sns_nick_name_list.append("N/A")
        for ai_chat_record in ai_chat_records:
            ai_chat_nick_name = ai_chat_record.name
            self.serverCombo.addItem(ai_chat_nick_name)
            self.sns_nick_name_list.append(ai_chat_nick_name)


        if cur_nick_name == "":
            self.serverCombo.setCurrentText("N/A")
        else:
            self.serverCombo.setCurrentText(cur_nick_name)

        self.cur_nick_name=cur_nick_name

        serverLayout = QGridLayout()
        serverLayout.addWidget(self.serverLabel, 0, 0)
        serverLayout.addWidget(self.serverCombo, 0, 1,1,2)

        # 创建人类接管聊天的标签
        self.humantakeoverLabel = QLabel("人类接管帐号:")

        # 创建单选框选项：是
        self.humantakeoverYesRadio = QRadioButton("是")
        self.humantakeoverYesRadio.setObjectName("humantakeoverYesRadio")

        # 创建单选框选项：否
        self.humantakeoverNoRadio = QRadioButton("否")
        self.humantakeoverNoRadio.setObjectName("humantakeoverNoRadio")


        if ai_chat_cfg != None:
            if ai_chat_cfg.humantakeover==1:  # Assuming index 0 represents self.nameEdit text
                self.humantakeoverYesRadio.setChecked(True)
                self.humantakeoverNoRadio.setChecked(False)
            else:  # Assuming index 0 represents self.nameEdit text
                self.humantakeoverYesRadio.setChecked(False)
                self.humantakeoverNoRadio.setChecked(True)
        else:
            self.humantakeoverYesRadio.setChecked(False)
            self.humantakeoverNoRadio.setChecked(True)




        # 将标签和单选框添加到布局中
        self.humantakeoverLabel.setVisible(False)
        self.humantakeoverYesRadio.setVisible(False)
        self.humantakeoverNoRadio.setVisible(False)
        # serverLayout.addWidget(self.humantakeoverLabel, 1, 0)
        # serverLayout.addWidget(self.humantakeoverYesRadio, 1, 1)  # 添加“是”选项
        # serverLayout.addWidget(self.humantakeoverNoRadio, 1, 2)  # 添加“否”选项

        configLayout = QVBoxLayout()
        configLayout.addLayout(serverLayout)
        configGroup.setLayout(configLayout)
        self.serverCombo.currentIndexChanged.connect(self.on_combobox_changed)








        # startQueryButton = QPushButton("确认更改状态")

        packagesLayout = QGridLayout()
        packagesLayout.addWidget(self.useridLabel, 0, 0)
        packagesLayout.addWidget(self.useridEdit, 0, 1)
        packagesLayout.addWidget(self.userpasswordLabel, 1, 0)
        packagesLayout.addWidget(self.userpasswordEdit, 1, 1)

        packagesLayout.addWidget(self.accountLabel, 2, 0)
        packagesLayout.addWidget(self.accountEdit, 2, 1)
        packagesLayout.addWidget(self.passwordLabel, 3,0)
        packagesLayout.addWidget(self.passwordEdit, 3, 1)



        packagesLayout.addWidget(self.statusLabel, 4, 0)
        packagesLayout.addWidget(self.statusCombo, 4, 1)


        packagesGroup.setLayout(packagesLayout)

        mainLayout = QVBoxLayout()

        mainLayout.addLayout(hLayout)

        mainLayout.addWidget(packagesGroup)
        mainLayout.addSpacing(6)
        mainLayout.addLayout(layout_belong_to_agent)
        mainLayout.addSpacing(40)
        mainLayout.addWidget(configGroup)
        mainLayout.addSpacing(12)
        # mainLayout.addWidget(startQueryButton)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)
        # 只有在没有成功加载用户头像时才设置默认头像
        if not (ai_chat_cfg and ai_chat_cfg.avatar):
            # 直接显示默认头像，不保存文件
            default_pixmap = QPixmap("images/avatar.png")
            self.avatar_label.setPixmap(default_pixmap)

    def on_combobox_changed(self, index):
        """
        当QComboBox的选项变化时调用此方法
        :param index: 当前选中项的索引
        """
        # 获取当前选中的选项文本
        cur_nick_name=self.cur_nick_name
        selected_name = self.serverCombo.currentText()
        if selected_name !="N/A" and selected_name!=cur_nick_name:
            agent_belonged = query_AgentCfg(name=selected_name)
            if self.ai_chat_cfg:
                if agent_belonged.snsaccount != "N/A" and agent_belonged.snsaccount != self.accountEdit.text():
                    QMessageBox.information(self, '提示', '该Agent已经分配了其他社交帐号，请选择别的Agent!')
                    self.serverCombo.setCurrentText(cur_nick_name)
            else:
                if agent_belonged.snsaccount != "N/A":
                    QMessageBox.information(self, '提示', '该Agent已经分配了其他社交帐号，请选择别的Agent!')
                    self.serverCombo.setCurrentText(cur_nick_name)
            # else:
            #     self.serverCombo.setCurrentText(selected_name)
            #     snsaccount=self.ai_chat_cfg.account
            #     snsnickname = self.ai_chat_cfg.nickname
            #     update_AgentCfg(agent_belonged.id,snsaccount=snsaccount,snsnickname=snsnickname)

    def uploadAvatar(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Open File', '.', 'Image Files (*.png *.jpg *.jpeg *.bmp)')
        if filename:
            # 创建avatars目录（如果不存在）
            avatars_dir = os.path.join('images', 'avatars')
            if not os.path.exists(avatars_dir):
                os.makedirs(avatars_dir)

            # 生成唯一的文件名
            import uuid
            file_extension = os.path.splitext(filename)[1]
            new_filename = f"{uuid.uuid4()}{file_extension}"
            new_filepath = os.path.join(avatars_dir, new_filename)

            # 复制文件到avatars目录
            from shutil import copyfile
            copyfile(filename, new_filepath)

            # 先设置文件名（重要：必须在 setAvatar 之前）
            self.avatar = new_filename

            # 加载图片并处理
            pixmap = QPixmap(new_filepath)
            self.setAvatar(pixmap)

    def setAvatar(self, pixmap):
        size = QSize(70, 70)
        target = QPixmap(size)
        target.fill(Qt.GlobalColor.transparent)

        painter = QPainter(target)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen = QPen(Qt.GlobalColor.white)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawEllipse(1, 1, size.width() - 2, size.height() - 2)

        clip_path = QPainterPath()
        clip_path.addEllipse(2, 2, size.width() - 4, size.height() - 4)
        painter.setClipPath(clip_path)

        diameter = min(size.width(), size.height())
        scaled_pixmap = pixmap.scaledToWidth(diameter, Qt.TransformationMode.SmoothTransformation) if pixmap.width() < pixmap.height() else pixmap.scaledToHeight(diameter, Qt.TransformationMode.SmoothTransformation)
        target_rect = QRect((size.width() - scaled_pixmap.width()) // 2, (size.height() - scaled_pixmap.height()) // 2, scaled_pixmap.width(), scaled_pixmap.height())
        painter.drawPixmap(target_rect, scaled_pixmap)

        painter.end()

        # 创建avatars目录（如果不存在）
        avatars_dir = os.path.join('images', 'avatars')
        if not os.path.exists(avatars_dir):
            os.makedirs(avatars_dir)

        # self.avatar 应该在调用 setAvatar 之前就被设置好
        # 如果没有设置，生成一个默认文件名
        if not self.avatar:
            import uuid
            self.avatar = f"{uuid.uuid4()}.png"
            print("Warning: avatar filename was not set before calling setAvatar()")

        image_file_path = os.path.join(avatars_dir, self.avatar)
        target.save(image_file_path, "PNG")

        # 生成地图标记图片，并保存其完整路径
        self.avatar_map = self.compositeAndSave(target)
        self.avatar_label.setPixmap(target)

    def compositeAndSave(self, avatar_pixmap):
        """
        将头像与地图标记图标合成，并保存为地图标记图片

        Returns:
            str: 生成的地图标记图片的完整路径（用于上传到服务器）
        """
        pin_pixmap = QPixmap("pin.png")
        if pin_pixmap.isNull():
            print("Failed to load pin.png")
            return None

        composite_pixmap = QPixmap(pin_pixmap.size())
        composite_pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(composite_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.drawPixmap(0, 0, pin_pixmap)
        avatar_position = PyQt6.QtCore.QPoint(1, 2)
        painter.drawPixmap(avatar_position, avatar_pixmap)
        painter.end()

        scaled_composite_pixmap = composite_pixmap.scaled(
            composite_pixmap.width() // 2,
            composite_pixmap.height() // 2,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        scaled_composite_pixmap = scaled_composite_pixmap.toImage()
        quality = 25

        # 创建avatars目录（如果不存在）
        avatars_dir = os.path.join('images', 'avatars')
        if not os.path.exists(avatars_dir):
            os.makedirs(avatars_dir)

        # 基于当前avatar文件名生成带_map后缀的文件名
        # 例如: NG2025052719071718435.png -> NG2025052719071718435_map.png
        if self.avatar:
            # self.avatar 应该只是文件名（不含路径）
            # 但为了兼容性，使用 os.path.basename 确保只获取文件名
            avatar_filename = os.path.basename(self.avatar)
            # 分离文件名和扩展名
            name_without_ext, file_extension = os.path.splitext(avatar_filename)
            # 添加_map后缀
            map_filename = f"{name_without_ext}_map{file_extension}"
            # 组合完整路径
            compressed_image = os.path.join(avatars_dir, map_filename)
        else:
            # 如果没有avatar，使用默认文件名
            import uuid
            map_filename = f"{uuid.uuid4()}_map.png"
            compressed_image = os.path.join(avatars_dir, map_filename)

        # 保存地图标记图片
        scaled_composite_pixmap.save(compressed_image, "PNG", quality)
        print(f"Composite image saved as {compressed_image}")

        # 返回完整路径，用于上传到服务器
        return os.path.abspath(compressed_image)


class UserInfoPage(QWidget):
    def __init__(self, agent, parent=None):
        super(UserInfoPage, self).__init__(parent)
        self.agent = agent

        self.avatar3d = ""

        self.avatar3d_selector = ImageSelector()
        self.avatar3d_selector.selected.connect(self.set_avatar3d)
        self.avatar3d_selector.show_image(6)






        packagesGroup = QGroupBox("个人资料")

        self.nicknameLabel = QLabel("昵称:")
        self.nicknameEdit = QLineEdit()
        self.signLabel = QLabel("自我介绍:")
        self.signEdit = QPlainTextEdit()
        line_height = self.signEdit.fontMetrics().height()  # 获取当前字体的一行高度
        self.signEdit.setFixedHeight(line_height * 3)


        self.snsUrlLabel = QLabel("SNS Profile:")
        self.snsUrlEdit = QLineEdit()
        self.snsUrlEdit.setPlaceholderText("Your main page url of X,Meta,Weibo,Tiktok")





        if agent != None:
            # self.nameEdit.setText(agent.name)  # Assuming index 0 represents self.nameEdit text
            # self.borndateEdit.setDateTime(agent.borndate)  # Assuming index 2 represents self.dateEdit value
            # self.tokenEdit.setText(str(agent.tokens))

            self.nicknameEdit.setText(agent.nickname)  # Assuming index 2 represents self.dateEdit value
            self.signEdit.setPlainText(agent.sign)  # Assuming index 3 represents self.bornareaCombo current text
            self.avatar3d = agent.avatar3d


        packagesLayout = QGridLayout()

        packagesLayout.addWidget(self.nicknameLabel, 0, 0)
        packagesLayout.addWidget(self.nicknameEdit, 0, 1)
        packagesLayout.addWidget(self.signLabel, 1, 0)
        packagesLayout.addWidget(self.signEdit, 1, 1)

        packagesLayout.addWidget(self.snsUrlLabel, 2, 0)
        packagesLayout.addWidget(self.snsUrlEdit, 2, 1)



        packagesGroup.setLayout(packagesLayout)

        mainLayout = QVBoxLayout()

        # mainLayout.addWidget(packagesGroup)
        # mainLayout.addSpacing(12)
        # mainLayout.addStretch(1)

        # 在主布局中添加提示信息并设置居中对齐
        self.instructionLabel = QLabel("* 请选择您的3D头像:")
        self.instructionLabel.setAlignment(Qt.AlignCenter)  # 设置文本居中对齐
        mainLayout.addWidget(self.instructionLabel)  # 将提示信息添加到主布局中
        mainLayout.addWidget(self.avatar3d_selector)
        mainLayout.addSpacing(10)
        mainLayout.addWidget(packagesGroup)

        mainLayout.addStretch(1)

        self.setLayout(mainLayout)

    def set_avatar3d(self, avatar3d):
        avatar3d = avatar3d.replace(".png", ".glb")
        avatar3d = 'http://www.ai-sns.org/' + avatar3d
        self.avatar3d = avatar3d


class ConnectionPage(QWidget):
    def __init__(self, agent, parent=None):
        super(ConnectionPage, self).__init__(parent)
        self.agent = agent

        configGroup = QGroupBox("服务器设置:")

        self.serveraddressLabel = QLabel("地址:")
        self.serveraddressEdit = QLineEdit()
        self.portLabel = QLabel("端口:")
        self.portEdit = QLineEdit()
        intValidator = QIntValidator()
        self.portEdit.setValidator(intValidator)
        self.sslLabel = QLabel("ssl:")
        self.sslCheckBox = QCheckBox("启用")
        self.resourceLabel = QLabel("资源:")
        self.resourceEdit = QLineEdit()

        packagesLayout = QGridLayout()
        packagesLayout.addWidget(self.serveraddressLabel, 0, 0)
        packagesLayout.addWidget(self.serveraddressEdit, 0, 1)
        packagesLayout.addWidget(self.portLabel, 1, 0)
        packagesLayout.addWidget(self.portEdit, 1, 1)
        packagesLayout.addWidget(self.sslLabel, 2, 0)
        packagesLayout.addWidget(self.sslCheckBox, 2, 1)
        packagesLayout.addWidget(self.resourceLabel, 3, 0)
        packagesLayout.addWidget(self.resourceEdit, 3, 1)

        configGroup.setLayout(packagesLayout)

        updateGroup = QGroupBox("代理设置:")
        self.proxyusedLabel = QLabel("代理服务器:")
        self.proxyusedCheckBox = QCheckBox("启用")
        self.proxyaddressLabel = QLabel("地址:")
        self.proxyaddressEdit = QLineEdit()
        self.proxyportLabel = QLabel("端口:")
        self.proxyportEdit = QLineEdit()
        intValidator = QIntValidator()
        self.proxyportEdit.setValidator(intValidator)
        self.proxysslLabel = QLabel("ssl:")
        self.proxysslCheckBox = QCheckBox("启用")

        updateLayout = QGridLayout()
        updateLayout.addWidget(self.proxyusedLabel, 0, 0)
        updateLayout.addWidget(self.proxyusedCheckBox, 0, 1)
        updateLayout.addWidget(self.proxyaddressLabel, 1, 0)
        updateLayout.addWidget(self.proxyaddressEdit, 1, 1)
        updateLayout.addWidget(self.proxyportLabel, 2, 0)
        updateLayout.addWidget(self.proxyportEdit, 2, 1)
        updateLayout.addWidget(self.proxysslLabel, 3, 0)
        updateLayout.addWidget(self.proxysslCheckBox, 3, 1)


        updateGroup.setLayout(updateLayout)

        if agent != None:
            self.serveraddressEdit.setText(agent.serveraddress)
            self.portEdit.setText(str(agent.port))
            self.sslCheckBox.setChecked(agent.ssl)
            self.resourceEdit.setText(agent.resource)

            self.proxyusedCheckBox.setChecked(agent.proxyused)
            self.proxyaddressEdit.setText(agent.proxyaddress)
            self.proxyportEdit.setText(str(agent.proxyport))
            self.proxysslCheckBox.setChecked(agent.proxyssl)




        mainLayout = QVBoxLayout()
        mainLayout.addWidget(configGroup)
        mainLayout.addWidget(updateGroup)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)


class SecurityPage(QWidget):
    def __init__(self, agent, parent=None):
        super(SecurityPage, self).__init__(parent)
        self.agent = agent

        updateGroup = QGroupBox("隐私与安全:")
        self.savepasswordlocalCheckBox = QCheckBox("本地保存密码")
        self.autoconnectCheckBox = QCheckBox("启动时自动连接")
        self.sendreceiptCheckBox = QCheckBox("发送消息回执")
        self.sendreadflagCheckBox = QCheckBox("发送已读标志")
        self.sendchatstatusCheckBox = QCheckBox("发送聊天状态")
        self.sendgroupchatstatusCheckBox = QCheckBox("群聊中发送聊天状态")
        self.agreeallfriendrequestCheckBox = QCheckBox("同意所有联系人请求")

        packagesGroup = QGroupBox("修改密码")

        self.oldpasswordLabel = QLabel("老密码:")
        self.oldpasswordEdit = QLineEdit()
        self.oldpasswordEdit.setEchoMode(QLineEdit.EchoMode.Password)
        self.newpasswordLabel = QLabel("新密码:")
        self.newpasswordEdit = QLineEdit()
        self.newpasswordEdit.setEchoMode(QLineEdit.EchoMode.Password)
        self.confrimpasswordLabel = QLabel("确认密码:")
        self.confirmpasswordEdit = QLineEdit()
        self.confirmpasswordEdit.setEchoMode(QLineEdit.EchoMode.Password)

        if agent != None:
            self.savepasswordlocalCheckBox.setChecked(agent.savepasswordlocal)
            self.autoconnectCheckBox.setChecked(agent.autoconnect)
            self.sendreceiptCheckBox.setChecked(agent.sendreceipt)
            self.sendreadflagCheckBox.setChecked(agent.sendreadflag)
            self.sendchatstatusCheckBox.setChecked(agent.sendchatstatus)
            self.sendgroupchatstatusCheckBox.setChecked(agent.sendgroupchatstatus)
            self.agreeallfriendrequestCheckBox.setChecked(agent.agreeallfriendrequest)


        startUpdateButton = QPushButton("修改密码")
        startUpdateButton.clicked.connect(self.change_password)

        updateLayout = QGridLayout()
        updateLayout.addWidget(self.savepasswordlocalCheckBox, 0, 0)
        updateLayout.addWidget(self.autoconnectCheckBox, 0, 1)
        updateLayout.addWidget(self.sendreceiptCheckBox, 1, 0)
        updateLayout.addWidget(self.sendreadflagCheckBox, 1, 1)
        updateLayout.addWidget(self.sendchatstatusCheckBox, 2, 0)
        updateLayout.addWidget(self.sendgroupchatstatusCheckBox, 2, 1)
        updateLayout.addWidget(self.agreeallfriendrequestCheckBox, 3, 0)
        updateGroup.setLayout(updateLayout)
        updateGroup.setHidden(True)#暂时隐藏

        passwordLayout = QGridLayout()
        passwordLayout.addWidget(self.oldpasswordLabel, 0, 0)
        passwordLayout.addWidget(self.oldpasswordEdit, 0, 1)
        passwordLayout.addWidget(self.newpasswordLabel, 1, 0)
        passwordLayout.addWidget(self.newpasswordEdit, 1, 1)
        passwordLayout.addWidget(self.confrimpasswordLabel, 2, 0)
        passwordLayout.addWidget(self.confirmpasswordEdit, 2, 1)
        packagesGroup.setLayout(passwordLayout)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(updateGroup)
        mainLayout.addWidget(packagesGroup)

        mainLayout.addSpacing(12)
        mainLayout.addWidget(startUpdateButton)

        mainLayout.addSpacing(5)
        layout_link = QHBoxLayout()
        sns_link_title = QLabel("修改XMPP账号密码?")
        layout_link.addWidget(sns_link_title)
        sns_apply_label_link = ClickableLabelV2("前往修改", "https://compliance.conversations.im/")
        layout_link.addWidget(sns_apply_label_link)
        layout_link.addStretch(1)
        mainLayout.addLayout(layout_link)
        mainLayout.addSpacing(15)


        mainLayout.addStretch(1)

        self.setLayout(mainLayout)

    def change_password(self):
        # 获取顶层对话框引用
        dialog = self
        while dialog and not isinstance(dialog, ConfigDialog):
            dialog = dialog.parent()

        if not dialog:
            QMessageBox.critical(self, "错误", "无法找到配置对话框")
            return

        # 获取输入的密码
        old_password = self.oldpasswordEdit.text()
        new_password = self.newpasswordEdit.text()
        confirm_password = self.confirmpasswordEdit.text()

        # 验证输入
        if not old_password:
            QMessageBox.warning(self, "警告", "请输入旧密码")
            return

        if not new_password:
            QMessageBox.warning(self, "警告", "请输入新密码")
            return

        if not confirm_password:
            QMessageBox.warning(self, "警告", "请确认新密码")
            return

        if new_password != confirm_password:
            QMessageBox.warning(self, "警告", "新密码和确认密码不一致")
            return

        if len(new_password) < 8:
            QMessageBox.warning(self, "警告", "密码长度至少8位")
            return

        # 获取用户ID
        userid = dialog.generalPage.useridEdit.text()
        if not userid:
            QMessageBox.warning(self, "警告", "用户ID不能为空")
            return

        # 调用后端API修改密码
        try:
            import requests
            from urllib.parse import urljoin

            api_base_url = "http://www.ai-sns.org"
            change_password_url = urljoin(api_base_url, "/api/change-password/")

            # 构造请求数据
            data = {
                "nation_id": userid,
                "old_password": old_password,
                "new_password": new_password
            }

            # 发送请求
            response = requests.post(change_password_url, data=data)

            if response.status_code == 200:
                QMessageBox.information(self, "成功", "密码修改成功")

                # 更新界面中的密码输入框
                dialog.generalPage.userpasswordEdit.setText(new_password)


                # 更新数据库中的用户密码
                if dialog.ai_chat_cfg:
                    from db.DBFactory import update_AiChatCfg
                    update_AiChatCfg(dialog.ai_chat_cfg.id, nationpassword=new_password)

                # 清空密码修改界面的输入框
                self.oldpasswordEdit.clear()
                self.newpasswordEdit.clear()
                self.confirmpasswordEdit.clear()
            else:
                try:
                    error_msg = response.json().get("detail", "密码修改失败")
                except:
                    error_msg = "密码修改失败"
                QMessageBox.critical(self, "错误", f"密码修改失败: {error_msg}")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"请求失败: {str(e)}")

class ClickableAvatarLabel(QLabel):
    clicked = PyQt6.QtCore.pyqtSignal()

    def mousePressEvent(self, event):
        self.clicked.emit()


class ClickableLabel(QLabel):
    clicknum=0
    def __init__(self, agent,parent=None):
        self.agent=agent
        self.app = parent.app
        self.parent = parent
        text="注册"
        super().__init__(text)
        self.setTextInteractionFlags( Qt.TextInteractionFlag.TextSelectableByMouse)
        self.setStyleSheet("QLabel { color: blue; text-decoration: underline;font-family:微软雅黑;font-size:8pt;cursor: pointer;} QLabel:hover { color: red; text-decoration: underline;font-family:微软雅黑;font-size:8pt;cursor: pointer;}")

    def changeEvent(self, event):
        print(self.text())


    def mousePressEvent(self, event):
        webbrowser.open("https://compliance.conversations.im/")

class ClickableLabelV2(QLabel):
    clicknum = 0

    def __init__(self, text, url):
        self.text = text
        self.url = url
        super().__init__(text)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.setStyleSheet("QLabel { color: blue; text-decoration: underline;font-family:微软雅黑;font-size:8pt;cursor: pointer;} QLabel:hover { color: red; text-decoration: underline;font-family:微软雅黑;font-size:8pt;cursor: pointer;}")

    def changeEvent(self, event):
        print(self.text)

    def mousePressEvent(self, event):
        webbrowser.open(self.url)



if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    dialog = ConfigDialog()
    sys.exit(dialog.exec())
