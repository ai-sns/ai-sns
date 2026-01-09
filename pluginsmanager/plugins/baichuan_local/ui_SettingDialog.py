import os
import yaml
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QGroupBox, QGridLayout,
    QLabel, QLineEdit, QCheckBox, QSlider, QTextEdit,
    QDialogButtonBox, QComboBox, QHBoxLayout, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal, QSettings
from PyQt6.QtGui import QIcon
from PyQt6 import QtCore, QtGui, QtWidgets
import json
import sys
sys.path.append("../..")
sys.path.append("../../..")
sys.path.append("../../../..")
import llm_manager as llmmgr
from i18n import lt
class ui_SettingDialog(object):
    def setupUi(self, ConnectionDialog):
        llm_connector_name = ConnectionDialog.parent.meta.name
        self.llm_connector_name = llm_connector_name
        ConnectionDialog.setObjectName("ConnectionDialog")
        ConnectionDialog.resize(400, 400)

        self.vboxlayout = QVBoxLayout(ConnectionDialog)
        self.vboxlayout.setObjectName("vboxlayout")

        # Group box for API configuration
        self.groupBox = QGroupBox(ConnectionDialog)
        self.groupBox.setObjectName("groupBox")
        self.gridlayout = QGridLayout(self.groupBox)
        self.gridlayout.setObjectName("gridlayout")
        self.vboxlayout.addWidget(self.groupBox)

        # URL
        self.url_label = QLabel("URL:")
        self.gridlayout.addWidget(self.url_label, 0, 0)
        self.url_edit = QLineEdit()
        self.gridlayout.addWidget(self.url_edit, 0, 1, 1, 2)

        # API key
        self.api_key_label = QLabel("API Key:")
        self.gridlayout.addWidget(self.api_key_label, 1, 0)
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEnabled(True)  # Make it editable by default
        self.gridlayout.addWidget(self.api_key_edit, 1, 1, 1, 2)

        # Model selection
        vlayout = QHBoxLayout()
        self.model_label = QLabel("Model:")
        self.set_model_label = ClickableLabel(lt("Set list", "设置模型"))
        self.set_model_label.clicked.connect(self.set_model_list)
        vlayout.addWidget(self.model_label)
        vlayout.addWidget(self.set_model_label)
        # self.gridlayout.addWidget(self.model_label, 2, 0)
        self.gridlayout.addLayout(vlayout, 2, 0)
        self.model_combobox = QComboBox()
        self.model_combobox.addItems(llmmgr.get_model_type_list_by_connector_name(llm_connector_name))
        self.model_combobox.setEnabled(True)  # Make it editable by default
        # self.model_combobox.setEditable(True)
        self.gridlayout.addWidget(self.model_combobox, 2, 1, 1, 2)

        # Max tokens
        self.max_tokens_label = QLabel("Max Tokens:")
        self.gridlayout.addWidget(self.max_tokens_label, 3, 0)
        self.max_tokens_edit = QLineEdit()
        self.max_tokens_edit.setEnabled(True)  # Make it editable by default
        self.gridlayout.addWidget(self.max_tokens_edit, 3, 1, 1, 2)

        # Temperature slider
        self.temperature_label = QLabel("Temperature:")
        self.gridlayout.addWidget(self.temperature_label, 4, 0)
        self.temperature_slider = QSlider(Qt.Orientation.Horizontal)
        self.temperature_slider.setMinimum(0)
        self.temperature_slider.setMaximum(100)
        self.temperature_slider.setEnabled(True)  # Make it editable by default
        self.gridlayout.addWidget(self.temperature_slider, 4, 1)
        self.temperature_slider_value_label = QLabel("0.0")
        self.gridlayout.addWidget(self.temperature_slider_value_label, 4, 2)

        # Top P slider
        self.top_p_label = QLabel("Top P:")
        self.gridlayout.addWidget(self.top_p_label, 5, 0)
        self.top_p_slider = QSlider(Qt.Orientation.Horizontal)
        self.top_p_slider.setMinimum(0)
        self.top_p_slider.setMaximum(100)
        self.top_p_slider.setEnabled(True)  # Make it editable by default
        self.gridlayout.addWidget(self.top_p_slider, 5, 1)
        self.top_p_slider_value_label = QLabel("0.0")
        self.gridlayout.addWidget(self.top_p_slider_value_label, 5, 2)

        # Stream checkbox
        self.stream_label = QLabel("Stream:")
        self.gridlayout.addWidget(self.stream_label, 6, 0)
        self.stream_checkbox = QCheckBox()
        self.gridlayout.addWidget(self.stream_checkbox, 6, 1, 1, 2)
        self.stream_checkbox.setEnabled(True)  # Make it editable by default

        # Description
        self.description_label = QLabel("Description:")
        self.gridlayout.addWidget(self.description_label, 7, 0)
        self.description_textedit = QTextEdit()
        self.gridlayout.addWidget(self.description_textedit, 7, 1, 1, 2)
        self.description_textedit.setEnabled(True)

        # Custom parameters checkbox
        self.custom_params_label = QLabel("Custom Parameters:")
        self.gridlayout.addWidget(self.custom_params_label, 8, 0)
        self.custom_params_checkbox = QCheckBox()
        self.gridlayout.addWidget(self.custom_params_checkbox, 8, 1, 1, 2)
        self.custom_params_checkbox.setEnabled(True)  # Enable by default

        # Parameters text edit
        self.parameters_textedit = QTextEdit()
        self.gridlayout.addWidget(self.parameters_textedit, 9, 0, 1, 3)
        self.parameters_textedit.setEnabled(False)  # Disable by default

        # Set column stretch
        self.gridlayout.setColumnStretch(0, 1)
        self.gridlayout.setColumnStretch(1, 2)
        self.gridlayout.setColumnStretch(2, 1)

        # Connect signals
        self.custom_params_checkbox.stateChanged.connect(self.toggle_parameters_edit)
        self.temperature_slider.valueChanged.connect(self.update_temperature_label)
        self.top_p_slider.valueChanged.connect(self.update_top_p_label)

        # Button box
        self.buttonBox = QDialogButtonBox(ConnectionDialog)
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")
        ok_button = self.buttonBox.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setText("确定")
        cancel_button = self.buttonBox.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_button.setText("取消")
        self.vboxlayout.addWidget(self.buttonBox)

        self.retranslateUi(ConnectionDialog)
        self.buttonBox.accepted.connect(ConnectionDialog.accept)
        self.buttonBox.rejected.connect(ConnectionDialog.reject)
        ConnectionDialog.setWindowTitle("连接配置")
        ConnectionDialog.setWindowIcon(QIcon("images/aisns.png"))
        QtCore.QMetaObject.connectSlotsByName(ConnectionDialog)

    def retranslateUi(self, ConnectionDialog):
        self.groupBox.setTitle("大模型连接配置")
        self.url_label.setText("URL:")
        self.api_key_label.setText("API Key:")
        self.model_label.setText("Model:")
        self.max_tokens_label.setText("Max Tokens:")
        self.temperature_label.setText("Temperature:")
        self.top_p_label.setText("Top P:")
        self.stream_label.setText("Stream:")
        self.custom_params_label.setText("Custom Parameters:")
        self.description_label.setText("Description:")

    def toggle_parameters_edit(self, state):
        enabled = state == Qt.CheckState.Checked.value
        # self.api_key_edit.setEnabled(not enabled)
        self.model_combobox.setEnabled(not enabled)
        self.max_tokens_edit.setEnabled(not enabled)
        self.temperature_slider.setEnabled(not enabled)
        self.top_p_slider.setEnabled(not enabled)
        self.stream_checkbox.setEnabled(not enabled)


        if enabled:
            # Convert configuration to JSON format and set it as default text
            config = {
                "model": self.model_combobox.currentText(),
                "max_tokens": int(self.max_tokens_edit.text()),
                "temperature": round(self.temperature_slider.value() / 100, 1),
                "top_p": round(self.top_p_slider.value() / 100, 1),
                "stream": self.stream_checkbox.isChecked(),
                "n": 1,
                "stop": None,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.6
            }
            self.parameters_textedit.setPlainText(json.dumps(config, indent=4))
        self.parameters_textedit.setEnabled(enabled)

    def update_temperature_label(self, value):
        self.temperature_slider_value_label.setText(f"{value / 100:.1f}")

    def update_top_p_label(self, value):
        self.top_p_slider_value_label.setText(f"{value / 100:.1f}")


    def set_model_list(self):
        cfg = self.get_plugin_cfg()
        model_list = cfg["model_type"]
        dialog = TextEditDialog(model_list)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            print("Dialog accepted")
            print("Text content:")
            print(dialog.text_edit.toPlainText())
            model_list = dialog.text_edit.toPlainText()
            cfg["model_type"] = model_list
            self.set_config(cfg)
            current_text = self.model_combobox.currentText()
            self.model_combobox.clear()
            self.model_combobox.addItems(llmmgr.get_model_type_list_by_connector_name(self.llm_connector_name))
            self.model_combobox.setCurrentText(current_text)

    def get_plugin_cfg(self):
        """
        获取插件配置文件 plugin.yaml 的内容。

        :return: 返回读取的配置字典，如果文件不存在或读取失败则返回 None。
        """
        file_path = os.path.join(os.path.dirname(__file__), 'plugin.yaml')  # 构造配置文件路径

        try:
            # 以 UTF-8 编码打开文件，避免编码错误
            with open(file_path, "r", encoding='utf-8') as f:
                config = yaml.safe_load(f)  # 解析 YAML 文件
        except FileNotFoundError:
            print(f"配置文件未找到: {file_path}")  # 文件未找到时输出提示
        except yaml.YAMLError as e:
            print(f"YAML 解析错误: {e}")  # 解析 YAML 文件时的错误处理
        except UnicodeDecodeError as e:
            print(f"文件解码错误: {e}")  # 处理解码错误

        return config  # 返回配置字典

    def set_config(self, new_config):
        try:
            file_path = os.path.join(os.path.dirname(__file__), 'plugin.yaml')
            with open(file_path, "w") as f:
                yaml.safe_dump(new_config, f)
        except Exception as e:
            print(f"Error while saving YAML file: {e}")

class ClickableLabel(QLabel):

    clicked = pyqtSignal()
    def __init__(self, text):
        super().__init__(text)
        self.setTextInteractionFlags( Qt.TextInteractionFlag.TextSelectableByMouse)
        self.setStyleSheet("QLabel { color: blue; text-decoration: underline;font-family:微软雅黑;font-size:8pt;cursor: pointer;} QLabel:hover { color: red; text-decoration: underline;font-family:微软雅黑;font-size:8pt;cursor: pointer;}")

    def changeEvent(self, event):
        print(self.text())


    def mousePressEvent(self, event):
        self.clicked.emit()

class TextEditDialog(QDialog):
    def __init__(self,text):
        super().__init__()

        self.setWindowTitle(lt("Setting","设置"))

        # 创建一个 QVBoxLayout 布局
        layout = QVBoxLayout()

        # 创建一个 QTextEdit 小部件
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(text)
        layout.addWidget(self.text_edit)

        # 创建一个按钮
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)

        # 设置对话框的布局
        self.setLayout(layout)

