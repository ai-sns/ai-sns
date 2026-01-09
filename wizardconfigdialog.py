import os
import platform
import subprocess
import webbrowser
from globals import global_plugin_list
import PyQt6
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QPen, QPainterPath, QColor, QPalette
from PyQt6.QtWidgets import (QApplication, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
                             QListWidget, QPushButton, QStackedWidget, QVBoxLayout, QWidget, QDialogButtonBox,
                             QTextEdit, QComboBox)
from PyQt6.QtCore import QDate, QSize, Qt, QRect, QPoint
from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
                             QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
                             QListView, QListWidget, QListWidgetItem, QPushButton, QSpinBox,
                             QStackedWidget, QVBoxLayout, QWidget, QDialogButtonBox, QRadioButton, QFileDialog, QMessageBox, QFormLayout)

import re
from db.DBFactory import add_AgentCfg, update_AgentCfg
from i18n import lt
from pydantic import BaseModel
from pydantic import BaseModel, EmailStr, validator
import datetime
from util import generate_random_id
from globals import global_agent_list
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QGridLayout, QFrame, QSizePolicy)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import sys
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QPushButton
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QByteArray, QBuffer
import requests
from io import BytesIO
from typing import Dict, Optional
from db.DBFactory import query_SystemInit_All, update_SystemInit_ById, add_SystemInit,query_AiChatCfg,update_AiChatCfg
from util import generate_random_id
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QFrame, QWidget, QSizePolicy
from PyQt6.QtGui import QPixmap, QMouseEvent
import subprocess
import platform

class ConfigDialog(QDialog):
    def __init__(self, parent=None, agent=None):
        super(ConfigDialog, self).__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint)
        self.contentsWidget = QListWidget()
        self.contentsWidget.setViewMode(QListWidget.ViewMode.IconMode)
        self.contentsWidget.setIconSize(QSize(96, 84))
        self.contentsWidget.setMovement(QListWidget.Movement.Static)
        self.contentsWidget.setMaximumWidth(128)
        self.contentsWidget.setSpacing(12)

        self.record = None
        self.agent_cfg = agent.agent_cfg if agent else None
        self.app = parent

        self.generalPage = GeneralPage(agent)
        self.llmPage = LLMPage(agent)
        self.snsPage = SNSPage(agent)

        self.pagesWidget = QStackedWidget()
        self.pagesWidget.addWidget(self.generalPage)
        self.pagesWidget.addWidget(self.llmPage)
        self.pagesWidget.addWidget(self.snsPage)

        closeButton = QPushButton("关闭")
        self.createIcons()
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

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setText("提交")
        cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_button.setText("暂存")
        button_box.accepted.connect(self.accept_close)
        button_box.rejected.connect(self.reject_close)
        mainLayout.addWidget(button_box)

        mainLayout.addLayout(buttonsLayout)  # 添加这行，将buttonsLayout添加到主布局中

        self.button_box = button_box  # 保存button_box引用以便后续操作
        self.ok_button = ok_button    # 保存ok_button引用
        self.cancel_button = cancel_button  # 保存cancel_button引用
        self.close_button = closeButton     # 保存close_button引用

        self.init_data()
        self.setLayout(mainLayout)
        self.setWindowTitle(lt("Initialization Wizard", "初始化向导"))
        self.resize(600, 500)

    def init_data(self):
        records = query_SystemInit_All()
        if records:
            record = records[0]
            self.record = record
            self.generalPage.nameEdit.setText(record.name)
            self.generalPage.avatar = record.avatar
            self.generalPage.passwordEdit.setText(record.password)
            self.generalPage.confirmPasswordEdit.setText(record.confirm_password)
            self.generalPage.memoEdit.setPlainText(record.profile)

            # 加载保存的头像
            if record.avatar:
                # record.avatar 现在只保存文件名，需要拼接完整路径
                # 兼容旧数据：如果包含路径，提取文件名
                avatar_filename = os.path.basename(record.avatar)
                avatar_path = os.path.join('images', 'avatars', avatar_filename)

                if os.path.exists(avatar_path):
                    # 设置 avatar 文件名（重要！）
                    self.generalPage.avatar = avatar_filename

                    pixmap = QPixmap(avatar_path)
                    self.generalPage.avatar_label.setPixmap(pixmap)

                    # 同时生成 avatar_map 路径
                    name_without_ext, file_extension = os.path.splitext(avatar_filename)
                    map_filename = f"{name_without_ext}_map{file_extension}"
                    self.generalPage.avatar_map = os.path.abspath(os.path.join('images', 'avatars', map_filename))
                else:
                    # 如果找不到用户头像，则显示默认头像
                    filename = os.path.join('images', 'avatar.png')
                    pixmap = QPixmap(filename)
                    self.generalPage.avatar_label.setPixmap(pixmap)
            else:
                # 没有用户头像，显示默认头像
                filename = os.path.join('images', 'avatar.png')
                pixmap = QPixmap(filename)
                self.generalPage.avatar_label.setPixmap(pixmap)

            self.llmPage.llmCombo.setCurrentText(record.llm)
            self.llmPage.llmServerEdit.setText(record.llm_server)
            self.llmPage.apiKeyEdit.setText(record.api_key)

            self.snsPage.avatar3d = record.avatar3d
            self.snsPage.accountEdit.setText(record.account)
            self.snsPage.accountPasswordEdit.setText(record.account_password)
            self.snsPage.snsUrlEdit.setText(record.sns_url)
            self.snsPage.mapTypeCombo.setCurrentText(record.map)

            # 解析组合的地图API Key和Map ID
            # SystemInit表中存储格式: "google_value,baidu_value"
            if record.map_api_key:
                api_keys = record.map_api_key.split(',')
                if record.map == "Google" and len(api_keys) >= 1:
                    # Google地图使用第一个值
                    self.snsPage.mapApiKeyEdit.setText(api_keys[0] if api_keys[0] != "N/A" else "")
                elif record.map == "Baidu" and len(api_keys) >= 2:
                    # Baidu地图使用第二个值
                    self.snsPage.mapApiKeyEdit.setText(api_keys[1] if api_keys[1] != "N/A" else "")

            if record.map_id:
                map_ids = record.map_id.split(',')
                if record.map == "Google" and len(map_ids) >= 1:
                    # Google地图使用第一个值
                    self.snsPage.mapIdEdit.setText(map_ids[0] if map_ids[0] != "N/A" else "")
                elif record.map == "Baidu" and len(map_ids) >= 2:
                    # Baidu地图使用第二个值
                    map_id_value = map_ids[1] if map_ids[1] != "N/A" and map_ids[1] != "do_not_need_map_id" else "do_not_need_map_id"
                    self.snsPage.mapIdEdit.setText(map_id_value)

            # 如果status为1，则隐藏提交和暂存按钮，只显示关闭按钮
            if record.status == 1:
                self.button_box.setVisible(False)
                self.close_button.setVisible(True)
            else:
                self.button_box.setVisible(True)
                self.close_button.setVisible(False)

            self.snsPage.avatar3d_selector.show_image(6)

    def accept_close(self):
        # 添加提醒信息
        reply = QMessageBox.question(
            self,
            lt("Confirm Submit", "确认提交"),
            lt("If you have set the information on the interface elsewhere, this information will be overwritten. Do you want to continue?",
               "如果您在别的地方设置了界面上这些信息，这些信息将被覆盖。是否继续？"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.No:
            return False

        is_validated=self.validate_fields()
        if not is_validated:
            return False

        self.captcha_viewer = CaptchaViewer()  # 保存CaptchaViewer的实例
        self.captcha_viewer.exec()

        # 检查CaptchaViewer是否被确认
        if self.captcha_viewer.result() == QDialog.Accepted:
            print(self.captcha_viewer.captcha_input.text())
            self.captcha_id = self.captcha_viewer.captcha_id
            self.captcha_code = self.captcha_viewer.captcha_code
            result = self.save()
            if not result:
                return False
            else:
                nationid = result
                sns_record = query_AiChatCfg()
                if sns_record:
                    sns_record_id = sns_record.id

                    # 获取地图相关数据
                    map_type_text = self.snsPage.mapTypeCombo.currentText()
                    map_api_key = self.snsPage.mapApiKeyEdit.text().strip()
                    map_id = self.snsPage.mapIdEdit.text().strip()

                    # 将地图类型转换为数值: Google=0, Baidu=1
                    map_type_value = 0 if map_type_text == "Google" else 1

                    # 生成组合格式的地图API Key和Map ID (与SystemInit表一致)
                    if map_type_text == "Google":
                        combined_map_api_key = f"{map_api_key},N/A"
                        combined_map_id = f"{map_id},N/A"
                    else:  # Baidu
                        combined_map_api_key = f"N/A,{map_api_key}"
                        combined_map_id = f"N/A,do_not_need_map_id"

                    update_params = {
                        'nationid': nationid,
                        'avatar': self.generalPage.avatar,
                        'name': self.generalPage.nameEdit.text(),
                        'nationpassword': self.generalPage.passwordEdit.text(),
                        'sign': self.generalPage.memoEdit.toPlainText(),
                        'avatar3d': self.snsPage.avatar3d,
                        'account': self.snsPage.accountEdit.text(),
                        'password': self.snsPage.accountPasswordEdit.text(),
                        'sns_url': self.snsPage.snsUrlEdit.text(),
                        'map_type': map_type_value,                # 存储数值 0或1
                        'map_api_key': combined_map_api_key,       # 组合格式
                        'map_id': combined_map_id,                 # 组合格式
                    }
                    update_AiChatCfg(sns_record_id, **update_params)

                llm_name = self.llmPage.llmCombo.currentText()
                llm_server = self.llmPage.llmServerEdit.text()
                api_key = self.llmPage.apiKeyEdit.text()

                llm = global_plugin_list[llm_name]
                config = llm.get_config()
                config['url'] = llm_server
                config['api_key'] = api_key
                llm.set_config(config)



            self.accept()
            self.close()

    def validate_fields(self):

        # 首先获取当前界面上所有需要保存的数据
        name = self.generalPage.nameEdit.text().strip()
        avatar = self.generalPage.avatar
        password = self.generalPage.passwordEdit.text()
        confirm_password = self.generalPage.confirmPasswordEdit.text()
        profile = self.generalPage.memoEdit.toPlainText().strip()

        llm = self.llmPage.llmCombo.currentText()
        llm_server = self.llmPage.llmServerEdit.text().strip()
        api_key = self.llmPage.apiKeyEdit.text().strip()

        avatar3d = self.snsPage.avatar3d
        account = self.snsPage.accountEdit.text().strip()
        account_password = self.snsPage.accountPasswordEdit.text()
        map_type = self.snsPage.mapTypeCombo.currentText()
        map_api_key = self.snsPage.mapApiKeyEdit.text().strip()
        map_id = self.snsPage.mapIdEdit.text().strip()

        # 校验所有字段是否必填
        required_fields = [name, avatar, password, confirm_password, profile,
                           llm,llm_server, api_key, avatar3d, account, account_password,
                           map_type, map_api_key, map_id]


            # 检查必填字段是否为空
        if any(not field for field in required_fields):
            title = lt("Error","错误")
            content = lt("All information required, except SNS Profile.","除了社交主页，其他字段都是必填的。")
            QMessageBox.critical(self, title, content, QMessageBox.Ok)
            return False  # 直接返回，表示校验未通过

        # 校验密码和确认密码
        if password != confirm_password:
            print("密码和确认密码不匹配。")
            title = lt("Error", "错误")
            content = lt("The password and confirmation password do not match.", "密码和确认密码不匹配。")
            QMessageBox.critical(self, title, content, QMessageBox.Ok)
            return False

        # 检查密码复杂性
        if not self.is_password_valid(password):
            print("密码必须包含大小写字母、数字和特殊字符，并且至少8位。")
            title = lt("Error", "错误")
            content = lt("Passwords should be at least 8 characters long and include uppercase letters, lowercase letters, digits, and special characters.", "密码必须包含大小写字母、数字和特殊字符，并且至少8位。")
            QMessageBox.critical(self, title, content, QMessageBox.Ok)
            return False

        return True

    def save(self, submit_flag=True):
        result=True
        # 首先获取当前界面上所有需要保存的数据
        name = self.generalPage.nameEdit.text().strip()
        avatar = self.generalPage.avatar
        password = self.generalPage.passwordEdit.text()
        confirm_password = self.generalPage.confirmPasswordEdit.text()
        profile = self.generalPage.memoEdit.toPlainText().strip()

        llm = self.llmPage.llmCombo.currentText()
        llm_server = self.llmPage.llmServerEdit.text().strip()
        api_key = self.llmPage.apiKeyEdit.text().strip()

        avatar3d = self.snsPage.avatar3d
        account = self.snsPage.accountEdit.text().strip()
        account_password = self.snsPage.accountPasswordEdit.text()
        sns_url = self.snsPage.snsUrlEdit.text().strip()
        map_type = self.snsPage.mapTypeCombo.currentText()
        map_api_key = self.snsPage.mapApiKeyEdit.text().strip()
        map_id = self.snsPage.mapIdEdit.text().strip()

        # 处理地图API Key和Map ID的组合
        # 根据选择的地图类型，将两个字段组合成一个以逗号分隔的字符串
        if map_type == "Google":
            combined_map_api_key = f"{map_api_key},N/A"
            combined_map_id = f"{map_id},N/A"
        else:  # Baidu
            combined_map_api_key = f"N/A,{map_api_key}"
            # 对于百度地图，Map ID固定为do_not_need_map_id
            combined_map_id = f"N/A,do_not_need_map_id"

        # 设置状态值
        status = 1 if submit_flag else 0

        # 创建一个字典来存储需要更新的字段
        record_data = {
            "name": name,
            "avatar": avatar,
            "password": password,
            "confirm_password": confirm_password,
            "profile": profile,
            "llm": llm,
            "llm_server": llm_server,
            "api_key": api_key,
            "avatar3d": avatar3d,
            "account": account,
            "account_password": account_password,
            "sns_url": sns_url,
            "map": map_type,
            "map_api_key": combined_map_api_key,
            "map_id": combined_map_id,
            "status": status
        }

        # 如果所有校验通过，进行用户注册或其他业务逻辑
        if submit_flag:
            response_result = self.register_user(account=account)
            if not response_result:
                return False
            else:
                nation_id = response_result.get("nation_id",None)
                if nation_id:
                   result = nation_id


        # 如果记录存在，则更新操作；否则执行添加操作
        if self.record:
            # 使用 unpacking 将字典传递给更新函数
            update_SystemInit_ById(self.record.id, **record_data)
        else:
            # 添加新记录
            add_SystemInit(**record_data)



        return result


    def is_password_valid(self, password):
        """
        检查密码复杂性：至少8位，包含大小写字母、数字和特殊字符。
        """
        length_valid = len(password) >= 8
        uppercase_valid = re.search(r'[A-Z]', password) is not None
        lowercase_valid = re.search(r'[a-z]', password) is not None
        digit_valid = re.search(r'[0-9]', password) is not None
        special_char_valid = re.search(r'[!@#$%^&*(),.?":{}|<>]', password) is not None

        return length_valid and uppercase_valid and lowercase_valid and digit_valid and special_char_valid

    def register_user(self,
                      api_base_url: str = "http://www.ai-sns.org",
                      nation_id: str = "",
                      password: str = "securePassword123!",
                      account: str = "userqqq@example.com",
                      longitude: float = 116.27882,
                      latitude: float = 39.71164,
                      nick_name: str = "PythonUser",
                      avatar: str = "imcbot.png",
                      avatar_3d: str = "imcbot.glb",
                      profile: str = "hello me",
                      sns_url: str = "www.baidu.com",
                      status: int = 1,
                      ) -> Dict:
        """
        完整的用户注册流程
        1. 获取验证码
        2. 显示验证码让用户输入（这里简化自动读取）
        3. 提交注册请求
        """

        register_data = {
            "nation_id": nation_id,
            "password": password,
            "account": account,
            "longitude": longitude,
            "latitude": latitude,
            "captcha_id": self.captcha_id,
            "captcha_code": self.captcha_code,
            "nick_name": nick_name,
            "avatar": avatar,
            "avatar_3d": avatar_3d,
            "profile": profile,
            "sns_url": sns_url,
            "status": status
        }

        # 第四步：发送注册请求

        register_url = f"{api_base_url}/api/register/"

        # 上传地图标记图片（带_map后缀的compressed_image）
        # self.generalPage.avatar_map 已经是绝对路径
        if not self.generalPage.avatar_map:
            raise ValueError("地图标记图片尚未生成，请先设置头像")

        avatar_map_file_path = self.generalPage.avatar_map
        print(avatar_map_file_path)
        with open(avatar_map_file_path, "rb") as avatar_file:
            response = requests.post(
                register_url,
                data=register_data,
                files={"avatar_file": avatar_file}  # 上传文件
            )

        if response.status_code == 201:
            print("用户注册成功！")
            title = lt("Success", "成功")
            content = lt("Configurated successfully.", "配置成功。")
            QMessageBox.information(self, title, content, QMessageBox.Ok)
            return response.json()

        elif response.status_code == 200:
            print("用户更新成功！")
            title = lt("Success", "成功")
            content = lt("Updated successfully.", "更新成功。")
            QMessageBox.information(self, title, content, QMessageBox.Ok)
            return response.json()
        else:
            title = lt("Fail", "失败")
            content = f"Submit fail: {response.status_code} - {response.text}"
            QMessageBox.critical(self, title, content, QMessageBox.Ok)
            # raise Exception(f"注册失败: {response.status_code} - {response.text}")
            return False


    def reject_close(self):
        self.save(submit_flag=False)
        self.reject()
        self.close()

    def changePage(self, current, previous):
        if not current:
            current = previous
        self.pagesWidget.setCurrentIndex(self.contentsWidget.row(current))

    def createIcons(self):
        configButton = QListWidgetItem(self.contentsWidget)
        configButton.setIcon(QIcon(':/images/config.png'))
        configButton.setText(lt("Basic Setting", "基本配置"))
        configButton.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)
        configButton.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)

        techButton = QListWidgetItem(self.contentsWidget)
        techButton.setIcon(QIcon('images/technique.png'))
        techButton.setText(lt("LLM Setting", "大模型配置"))
        techButton.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)
        techButton.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)

        updateButton = QListWidgetItem(self.contentsWidget)
        updateButton.setIcon(QIcon(':/images/update.png'))
        updateButton.setText(lt("SNS Setting", "社交配置"))
        updateButton.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)
        updateButton.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)

        self.contentsWidget.adjustSize()
        self.contentsWidget.setFixedHeight(500)
        self.contentsWidget.currentItemChanged.connect(self.changePage)


class UserRegisterRequest(BaseModel):
    nation_id: str
    password: str
    account: str  # 可以是邮箱或用户名
    longitude: float
    latitude: float
    captcha_id: str
    captcha_code: str
    nick_name: str
    avatar: str
    avatar_3d: str
    profile: str
    sns_url: str
    status: int

    @validator('password')
    def password_length(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

    @validator('account')
    def account_validation(cls, v):
        # 这里可以添加更复杂的账户验证逻辑
        if not v:
            raise ValueError('Account cannot be empty')
        return v


class GeneralPage(QWidget):
    def __init__(self, agent, parent=None):
        super(GeneralPage, self).__init__(parent)
        self.agent_cfg = agent.agent_cfg if agent else None
        self.avatar = ""  # 只保存文件名，不含路径
        self.avatar_map = ""  # 保存带_map后缀的地图标记图片完整路径

        self.avatar_label = ClickableAvatarLabel()
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar_label.setFixedSize(70, 70)

        hLayout = QHBoxLayout()
        hLayout.addStretch()
        hLayout.addWidget(self.avatar_label)
        hLayout.addStretch()

        self.avatar_label.clicked.connect(self.uploadAvatar)

        packagesGroup = QGroupBox("基本资料")

        self.nameLabel = QLabel("* 昵称:")
        self.nameEdit = QLineEdit()

        self.passwordLabel = QLabel("* 密码:")
        self.passwordEdit = QLineEdit()
        self.passwordEdit.setEchoMode(QLineEdit.Password)

        self.confirmPasswordLabel = QLabel("* 确认密码:")
        self.confirmPasswordEdit = QLineEdit()
        self.confirmPasswordEdit.setEchoMode(QLineEdit.Password)

        self.memoLabel = QLabel("* 简介:")
        self.memoEdit = QTextEdit()

        if self.agent_cfg:
            self.nameEdit.setText(self.agent_cfg.name)
            self.memoEdit.setPlainText(self.agent_cfg.memo)

        packagesLayout = QGridLayout()
        packagesLayout.addWidget(self.nameLabel, 0, 0)
        packagesLayout.addWidget(self.nameEdit, 0, 1)
        packagesLayout.addWidget(self.passwordLabel, 1, 0)
        packagesLayout.addWidget(self.passwordEdit, 1, 1)
        packagesLayout.addWidget(self.confirmPasswordLabel, 2, 0)
        packagesLayout.addWidget(self.confirmPasswordEdit, 2, 1)
        packagesLayout.addWidget(self.memoLabel, 3, 0)
        packagesLayout.addWidget(self.memoEdit, 3, 1)

        packagesGroup.setLayout(packagesLayout)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(hLayout)
        mainLayout.addWidget(packagesGroup)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)
        # 只有在没有成功加载用户头像时才设置默认头像
        # if not (self.agent_cfg and self.agent_cfg.avatar):
            # 检查是否存在系统初始化记录中的头像
        records = query_SystemInit_All()
        if not (records and records[0].avatar):
            self.setAvatar(QPixmap("images/avatar.png"))

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
        avatar_position = QPoint(1, 2)
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

class LLMPage(QWidget):
    def __init__(self, agent, parent=None):
        super(LLMPage, self).__init__(parent)
        self.agent_cfg = agent.agent_cfg if agent else None

        # Create a group box for LLM settings
        llmGroup = QGroupBox("LLM 设置")

        # Labels and combo box for LLM selection
        self.llmLabel = QLabel("* LLM:")
        self.llmCombo = QComboBox()
        self.llmCombo.addItems([
            "OpenAI",
            "DeepSeek",
            "Claude",
            "Gemini",
            "OpenAI Compatible Provider",
            "DeepSeek Compatible Provider"
        ])

        # Label and line edit for LLM Server URL
        self.llmServerLabel = QLabel("* LLM Server:")
        self.llmServerEdit = QLineEdit()
        self.llmServerEdit.setPlaceholderText("LLM Server Url")
        self.llmServerEdit.setText("https://api.openai.com/v1/chat/completions")

        # Label and line edit for API Key
        self.apiKeyLabel = QLabel("* API Key:")
        self.apiKeyEdit = QLineEdit()

        # Initialize LLM settings if agent configuration exists
        if self.agent_cfg:
            self.llmCombo.setCurrentText(self.agent_cfg.llm)
            self.llmServerEdit.setText(self.agent_cfg.llm_server)
            self.apiKeyEdit.setText(self.agent_cfg.api_key)

        # Mapping LLM names to their respective server URLs
        self.llm_server_urls = {
            "OpenAI": "https://api.openai.com/v1/chat/completions",
            "DeepSeek": "https://api.deepseek.com/v1/chat/completions",
            "Claude": "https://api.anthropic.com/v1/messages",
            "Gemini": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        }

        # Connect the LLM combo box change event to update the server URL
        self.llmCombo.currentTextChanged.connect(self.update_llm_server_url)

        # Layout for the LLM settings
        llmLayout = QGridLayout()
        llmLayout.addWidget(self.llmLabel, 0, 0)
        llmLayout.addWidget(self.llmCombo, 0, 1)
        llmLayout.addWidget(self.llmServerLabel, 1, 0)
        llmLayout.addWidget(self.llmServerEdit, 1, 1)
        llmLayout.addWidget(self.apiKeyLabel, 2, 0)
        llmLayout.addWidget(self.apiKeyEdit, 2, 1)

        llmGroup.setLayout(llmLayout)

        # Main layout for the entire widget
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(llmGroup)
        mainLayout.addSpacing(5)

        # Link to registration
        layout_link = QHBoxLayout()
        llm_link_title = QLabel("还没有帐号?")
        layout_link.addWidget(llm_link_title)
        llm_apply_label_link = ClickableLabel("前往注册", "https://compliance.conversations.im/")
        layout_link.addWidget(llm_apply_label_link)
        layout_link.addStretch(1)
        mainLayout.addLayout(layout_link)
        mainLayout.addStretch(1)

        self.setLayout(mainLayout)

    def update_llm_server_url(self, selected_llm):
        """Update the LLM server URL based on the selected LLM."""
        url = self.llm_server_urls.get(selected_llm, "")  # Default to empty string if not found
        self.llmServerEdit.setText(url)  # Set the appropriate URL in the line edit


class SNSPage(QWidget):
    def __init__(self, agent, parent=None):
        super(SNSPage, self).__init__(parent)
        self.agent_cfg = agent.agent_cfg if agent else None
        self.avatar3d = ""

        self.avatar3d_selector = ImageSelector()
        self.avatar3d_selector.selected.connect(self.set_avatar3d)

        snsGroup = QGroupBox("XMPP IM (for AI chat)")

        self.accountLabel = QLabel("* 账号:")
        self.accountEdit = QLineEdit()
        self.accountEdit.setPlaceholderText("A XMPP IM account")

        self.accountPasswordLabel = QLabel("* 账号密码:")
        self.accountPasswordEdit = QLineEdit()
        self.accountPasswordEdit.setPlaceholderText("The password for the XMPP IM account")
        self.accountPasswordEdit.setEchoMode(QLineEdit.EchoMode.Password)

        self.snsUrlLabel = QLabel("SNS Profile:")
        self.snsUrlEdit = QLineEdit()
        self.snsUrlEdit.setPlaceholderText("Your main page url of X,Meta,Weibo,Tiktok")

        # 新建地图相关的 QGroupBox
        mapGroup = QGroupBox("地图设置")

        # 新增字段：地图类型
        self.mapTypeLabel = QLabel("* 地图类型:")
        self.mapTypeCombo = QComboBox()
        self.mapTypeCombo.addItems(["Google", "Baidu"])
        self.mapTypeCombo.currentTextChanged.connect(self.on_map_type_changed)

        # 新增字段：API Key
        self.mapApiKeyLabel = QLabel("* 地图 API Key:")
        self.mapApiKeyEdit = QLineEdit()

        # 新增字段：Map ID
        self.mapIdLabel = QLabel("* 地图 ID:")
        self.mapIdEdit = QLineEdit()

        if self.agent_cfg:
            self.accountEdit.setText(self.agent_cfg.account)
            self.accountPasswordEdit.setText(self.agent_cfg.account_password)
            self.snsUrlEdit.setText(self.agent_cfg.sns_url)
            self.mapTypeCombo.setCurrentText(self.agent_cfg.map_type)
            self.mapApiKeyEdit.setText(self.agent_cfg.map_api_key)
            self.mapIdEdit.setText(self.agent_cfg.map_id)

        # 布局设置
        snsLayout = QGridLayout()
        snsLayout.addWidget(self.accountLabel, 0, 0)
        snsLayout.addWidget(self.accountEdit, 0, 1)
        snsLayout.addWidget(self.accountPasswordLabel, 1, 0)
        snsLayout.addWidget(self.accountPasswordEdit, 1, 1)
        snsLayout.addWidget(self.snsUrlLabel, 2, 0)
        snsLayout.addWidget(self.snsUrlEdit, 2, 1)

        snsGroup.setLayout(snsLayout)

        # 地图设置布局
        mapLayout = QGridLayout()
        mapLayout.addWidget(self.mapTypeLabel, 0, 0)
        mapLayout.addWidget(self.mapTypeCombo, 0, 1)
        mapLayout.addWidget(self.mapApiKeyLabel, 1, 0)
        mapLayout.addWidget(self.mapApiKeyEdit, 1, 1)
        mapLayout.addWidget(self.mapIdLabel, 2, 0)
        mapLayout.addWidget(self.mapIdEdit, 2, 1)

        mapGroup.setLayout(mapLayout)

        mainLayout = QVBoxLayout()
        # 在主布局中添加提示信息并设置居中对齐
        self.instructionLabel = QLabel("* 请选择您的3D头像:")
        self.instructionLabel.setAlignment(Qt.AlignCenter)  # 设置文本居中对齐
        mainLayout.addWidget(self.instructionLabel)  # 将提示信息添加到主布局中
        mainLayout.addWidget(self.avatar3d_selector)
        mainLayout.addSpacing(10)
        mainLayout.addWidget(snsGroup)
        mainLayout.addSpacing(5)
        layout_link = QHBoxLayout()
        sns_link_title = QLabel("还没有帐号?")
        layout_link.addWidget(sns_link_title)
        sns_apply_label_link = ClickableLabel("前往注册", "https://compliance.conversations.im/")
        layout_link.addWidget(sns_apply_label_link)
        layout_link.addStretch(1)
        mainLayout.addLayout(layout_link)
        mainLayout.addSpacing(15)

        mainLayout.addWidget(mapGroup)  # 添加地图设置的 QGroupBox

        mainLayout.addSpacing(5)
        layout_link_map = QHBoxLayout()
        map_link_title = QLabel("还没有帐号?")
        layout_link_map.addWidget(map_link_title)
        map_apply_label_link = ClickableLabel("前往注册", "https://compliance.conversations.im/")
        layout_link_map.addWidget(map_apply_label_link)
        layout_link_map.addStretch(1)
        mainLayout.addLayout(layout_link_map)

        mainLayout.addStretch(1)

        self.setLayout(mainLayout)

    def on_map_type_changed(self, map_type):
        """
        当地图类型改变时的处理函数
        """
        # 当选择百度地图时，设置Map ID为固定值且不可编辑
        if map_type == "Baidu":
            self.mapIdEdit.setText("do_not_need_map_id")
            self.mapIdEdit.setReadOnly(True)
        else:
            # 当选择谷歌地图时，恢复Map ID的可编辑性
            self.mapIdEdit.setReadOnly(False)

    def set_avatar3d(self, avatar3d):
        avatar3d = avatar3d.replace(".png", ".glb")
        avatar3d = 'http://www.ai-sns.org/' + avatar3d
        self.avatar3d = avatar3d


class ClickableAvatarLabel(QLabel):
    clicked = PyQt6.QtCore.pyqtSignal()

    def mousePressEvent(self, event):
        self.clicked.emit()


class ClickableLabel(QLabel):
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


class ImageSelectorbak(QWidget):
    selected = PyQt6.QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()

        # Initialize the list of images (assuming these are the paths to your images)
        self.images = [f'images/3davatar/avatar3d_{i}.png' for i in range(11)]
        self.current_index = 0  # Start index for currently displayed images
        self.selected_index = None  # Index of the selected image in the entire list

        # Main layout
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Create navigation buttons
        self.prev_button = QPushButton("◀")  # Changed to arrow symbol
        self.next_button = QPushButton("▶")  # Changed to arrow symbol

        # Style buttons
        for button in [self.prev_button, self.next_button]:
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

        # Connect buttons to respective slots
        self.next_button.clicked.connect(self.show_next_images)
        self.prev_button.clicked.connect(self.show_previous_images)

        # Create image grid with frame
        self.image_grid = QGridLayout()
        self.grid_frame = QFrame()
        self.grid_frame.setLayout(self.image_grid)
        self.grid_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #c0c0c0;  /* Updated border color */
                background: white;
            }
        """)
        self.grid_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Create image labels
        self.labels = [QLabel() for _ in range(5)]
        for i, label in enumerate(self.labels):
            self.image_grid.addWidget(label, i // 5, i % 5)
            label.mousePressEvent = lambda event, i=i: self.select_image(i)
            label.setStyleSheet("border: 2px solid transparent;")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add widgets to main layout
        self.main_layout.addWidget(self.prev_button)
        self.main_layout.addWidget(self.grid_frame)
        self.main_layout.addWidget(self.next_button)

        # Set the main layout for the widget
        self.setLayout(self.main_layout)

        # Display the initial set of images
        self.update_images()

    def update_images(self):
        """Update the displayed images based on current index."""
        for i, label in enumerate(self.labels):
            image_index = self.current_index + i
            if image_index < len(self.images):
                pixmap = QPixmap(self.images[image_index])
                label.setPixmap(pixmap.scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio))
                if self.selected_index == image_index:
                    label.setStyleSheet("border: 2px solid #146ebe;")
                else:
                    label.setStyleSheet("border: 2px solid transparent;")
            else:
                label.clear()
                label.setStyleSheet("border: 2px solid transparent;")

    def select_image(self, label_index):
        """Select the image and highlight with a blue border."""
        image_index = self.current_index + label_index
        if image_index < len(self.images):
            self.selected_index = image_index
            print(self.images[image_index])  # Print the name of the selected image
            self.selected.emit(self.images[image_index])
            self.update_images()  # Refresh images to show selection

    def show_next_images(self):
        """Show the next set of images."""
        if self.current_index + 5 < len(self.images):
            self.current_index += 5
            self.update_images()

    def show_previous_images(self):
        """Show the previous set of images."""
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


class ImageSelectorbak2(QWidget):
    selected = PyQt6.QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_images()
        self.update_images()

    def setup_ui(self):
        """Initialize and configure all UI components."""
        # Main layout configuration
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(5)

        # Navigation buttons
        self.prev_button = QPushButton("◀")
        self.next_button = QPushButton("▶")
        self.setup_navigation_buttons()

        # Image grid configuration
        self.image_grid = QGridLayout()
        self.grid_frame = QFrame()
        self.grid_frame.setLayout(self.image_grid)
        self.setup_image_grid()

        # Add widgets to main layout
        self.main_layout.addWidget(self.prev_button)
        self.main_layout.addWidget(self.grid_frame)
        self.main_layout.addWidget(self.next_button)
        self.setLayout(self.main_layout)

    def setup_navigation_buttons(self):
        """Configure navigation buttons appearance and behavior."""
        button_style = """
            QPushButton {
                font-size: 24px;
                min-width: 20px;
                border: none;
                background: #f0f0f0;
            }
            QPushButton:hover {
                background: #e0e0e0;
            }
        """
        for button in [self.prev_button, self.next_button]:
            button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
            button.setStyleSheet(button_style)
            button.setCursor(Qt.CursorShape.PointingHandCursor)

        # Connect signals
        self.next_button.clicked.connect(self.show_next_images)
        self.prev_button.clicked.connect(self.show_previous_images)

    def setup_image_grid(self):
        """Configure image grid frame and labels."""
        self.grid_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #c0c0c0;
                background: white;
            }
        """)
        self.grid_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Create image labels
        self.labels = []
        for i in range(5):
            label = QLabel()
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("border: 2px solid transparent;")
            label.setCursor(Qt.CursorShape.PointingHandCursor)
            label.mousePressEvent = lambda event, i=i: self.on_image_clicked(i)
            self.image_grid.addWidget(label, 0, i)  # Single row grid
            self.labels.append(label)

    def load_images(self):
        """Initialize image data."""
        self.images = [f'images/3davatar/avatar3d_{i}.png' for i in range(11)]
        self.current_index = 0
        self.selected_index = None
        self.pixmap_cache = {}  # Cache for loaded pixmaps

    def on_image_clicked(self, label_index):
        """Handle image click event."""
        image_index = self.current_index + label_index
        if image_index < len(self.images):
            self.selected_index = image_index
            self.selected.emit(self.images[image_index])
            self.show_fullsize_image(image_index)
            self.update_images()

    def show_fullsize_imagebak(self, image_index):
        """Show a dialog with the full-size version of the selected image."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Image Viewer")

        layout = QVBoxLayout(dialog)
        image_label = QLabel()

        # Load and display original image
        pixmap = QPixmap(self.images[image_index])
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.close)

        layout.addWidget(image_label)
        layout.addWidget(close_button)

        dialog.setLayout(layout)
        dialog.exec()

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

    def update_images(self):
        """Update displayed images based on current index."""
        for i, label in enumerate(self.labels):
            image_index = self.current_index + i
            if image_index < len(self.images):
                # Use cached pixmap if available
                if image_index not in self.pixmap_cache:
                    self.pixmap_cache[image_index] = QPixmap(self.images[image_index]).scaled(
                        60, 60,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                label.setPixmap(self.pixmap_cache[image_index])

                # Update selection highlight
                highlight = image_index == self.selected_index
                label.setStyleSheet(f"border: 2px solid {'#146ebe' if highlight else 'transparent'};")
            else:
                label.clear()
                label.setStyleSheet("border: 2px solid transparent;")

    def show_next_images(self):
        """Navigate to the next set of images."""
        if self.current_index + 5 < len(self.images):
            self.current_index += 5
            self.update_images()

    def show_previous_images(self):
        """Navigate to the previous set of images."""
        if self.current_index - 5 >= 0:
            self.current_index -= 5
            self.update_images()

    def show_image(self, index):
        """
        Show the image at specified index, adjusting the view if needed.

        Args:
            index: The index of the image to display and select.
        """
        if 0 <= index < len(self.images):
            self.current_index = (index // 5) * 5
            self.update_images()
            self.selected_index = index
            self.update_images()  # Force update to show selection

class ImageSelector(QWidget):
    selected = PyQt6.QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()

        # Paths to images
        self.images = [f'images/3davatar/avatar3d_{i}.png' for i in range(35)]
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

class CaptchaViewer(QDialog):
    def __init__(self):
        super().__init__()
        self.captcha_id = ""
        self.captcha_code = ""
        self.init_ui()
        self.load_captcha()

    def init_ui(self):
        """初始化UI界面"""
        self.setWindowTitle('验证码显示')
        # self.setGeometry(100, 100, 300, 150)
        self.resize(300, 100)

        # 创建主布局
        main_layout = QVBoxLayout()

        # 创建验证码输入部分
        captcha_input_layout = QHBoxLayout()

        # 添加“请输入验证码”标签
        captcha_label = QLabel("请输入验证码:")
        captcha_input_layout.addWidget(captcha_label)

        # 添加QLineEdit用于输入验证码
        self.captcha_input = QLineEdit()
        captcha_input_layout.addWidget(self.captcha_input)

        # 添加验证码图片
        self.captcha_image_label = QLabel()
        self.captcha_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        captcha_input_layout.addWidget(self.captcha_image_label)

        # 将验证码输入部分添加到主布局
        main_layout.addLayout(captcha_input_layout)

        # 创建按钮部分
        button_layout = QHBoxLayout()

        # 添加确定按钮
        confirm_button = QPushButton("确定")
        confirm_button.clicked.connect(self.on_confirm)
        button_layout.addWidget(confirm_button)

        # 添加取消按钮
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.on_cancel)
        button_layout.addWidget(cancel_button)

        # 将按钮部分添加到主布局
        main_layout.addLayout(button_layout)

        # 设置主布局
        self.setLayout(main_layout)

    def load_captcha(self):
        """从API加载验证码并显示"""
        try:
            # 发送GET请求获取验证码图片
            response = requests.get("http://www.ai-sns.org/api/captcha/")
            self.captcha_id = response.headers.get("X-Captcha-ID")
            print("Captcha ID:", self.captcha_id)
            response.raise_for_status()  # 检查请求是否成功

            # 将响应内容转换为QPixmap
            image_data = QByteArray(response.content)
            buffer = QBuffer(image_data)
            buffer.open(QBuffer.OpenModeFlag.ReadOnly)

            pixmap = QPixmap()
            if pixmap.loadFromData(image_data, "PNG"):
                self.captcha_image_label.setPixmap(pixmap.scaled(
                    100, 40,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                ))
            else:
                self.captcha_image_label.setText("无法加载验证码图片")

        except requests.exceptions.RequestException as e:
            self.captcha_image_label.setText(f"请求验证码失败: {str(e)}")
        except Exception as e:
            self.captcha_image_label.setText(f"发生错误: {str(e)}")

    def on_confirm(self):
        """确定按钮点击事件"""
        self.captcha_code = self.captcha_input.text()
        print(f"输入的验证码: {self.captcha_code}")
        self.accept()
        # self.close()
        # 这里可以添加验证码验证逻辑

    def on_cancel(self):
        """取消按钮点击事件"""
        self.reject()
        # self.close()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    dialog = ConfigDialog()
    sys.exit(dialog.exec())
