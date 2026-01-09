import sys
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QRadioButton,
    QLabel, QLineEdit, QButtonGroup, QScrollArea, QWidget,
    QFrame, QPushButton, QComboBox, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt
from db.DBFactory import query_AiChatCfg_map, update_AiChatCfg_map
import util
import requests

class ProfessionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Fetch the current configuration from the database
        self.record = query_AiChatCfg_map()

        # Initialize with database values
        self.current_funds = getattr(self.record, 'money', 0)
        self.selected_profession = getattr(self.record, 'profession', "") or ""
        self.transaction_method = getattr(self.record, 'handle_after_trade', "") or ""
        self.handle_content = getattr(self.record, 'handle_content', "") or ""

        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("职业选择")
        self.setMinimumWidth(400)

        # Main layout
        main_layout = QVBoxLayout(self)

        # Current funds display
        funds_label = QLabel(f"当前资金: {self.current_funds}元")
        funds_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50; padding: 10px;")
        main_layout.addWidget(funds_label)

        # Create scroll area for profession options
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(300)

        # Profession options group
        professions_widget = QWidget()
        professions_layout = QVBoxLayout(professions_widget)

        # Button group for radio buttons
        self.button_group = QButtonGroup(self)

        # Professions with setup fee
        fee_professions = {
            "医生 (*需要800元开办费)": 800,
            "出租车司机 (*需要1000元开办费)": 1000,
            "食品商贩 (*需要800元开办费)": 800
        }

        # Other professions list
        other_professions = [
            "歌手", "国家", "美工设计", "视频制作", "ppt编写",
            "市场研究员", "程序员", "产品经理", "说书", "MCP销售员",
            "软件销售员", "虚拟商品销售员", "心理咨询师", "占星师",
            "法律顾问", "中介", "发传单", "付费知识博主", "其他职业"
        ]

        # Add fee professions
        fee_group = QGroupBox("需要开办费的职业")
        fee_layout = QVBoxLayout()

        for prof, fee in fee_professions.items():
            radio = QRadioButton(prof)
            radio.fee = fee
            self.button_group.addButton(radio)
            fee_layout.addWidget(radio)
            # Set selection based on database record
            if self.selected_profession == prof:
                radio.setChecked(True)

        fee_group.setLayout(fee_layout)
        professions_layout.addWidget(fee_group)

        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        professions_layout.addWidget(separator)

        # Add other professions
        other_group = QGroupBox("其他职业选项")
        other_layout = QVBoxLayout()

        for prof in other_professions:
            radio = QRadioButton(prof)
            radio.fee = 0  # No setup fee
            self.button_group.addButton(radio)
            other_layout.addWidget(radio)
            # Set selection based on database record
            if self.selected_profession == prof:
                radio.setChecked(True)
            elif prof == "其他职业" and self.selected_profession not in fee_professions and self.selected_profession not in other_professions:
                radio.setChecked(True)

        other_group.setLayout(other_layout)
        professions_layout.addWidget(other_group)

        scroll_area.setWidget(professions_widget)
        main_layout.addWidget(scroll_area)

        # Custom profession input
        self.custom_input = QLineEdit(self.selected_profession if self.selected_profession not in fee_professions and self.selected_profession not in other_professions else "")
        self.custom_input.setPlaceholderText("请输入您的职业...")
        self.custom_input.setVisible(self.selected_profession not in fee_professions and self.selected_profession not in other_professions)  # Visible if custom
        main_layout.addWidget(self.custom_input)

        # Transaction handling options
        transaction_group = QGroupBox("交易时的发货方式")
        transaction_layout = QVBoxLayout()
        self.transaction_button_group = QButtonGroup(self)

        send_message_radio = QRadioButton("发送消息")
        self.transaction_button_group.addButton(send_message_radio)
        transaction_layout.addWidget(send_message_radio)
        if self.transaction_method == "发送消息":
            send_message_radio.setChecked(True)

        call_program_radio = QRadioButton("调用程序")
        self.transaction_button_group.addButton(call_program_radio)
        transaction_layout.addWidget(call_program_radio)
        if self.transaction_method == "调用程序":
            call_program_radio.setChecked(True)

        transaction_group.setLayout(transaction_layout)
        main_layout.addWidget(transaction_group)

        # Messaging input
        self.message_input = QLineEdit(self.handle_content if self.transaction_method == "发送消息" else "")
        self.message_input.setPlaceholderText("请输入要发送的消息...")
        self.message_input.setVisible(self.transaction_method == "发送消息")
        main_layout.addWidget(self.message_input)

        # Program selection combo box
        self.program_combo_box = QComboBox()
        self.programs = ["请选择要调用的程序或工具"] + [tool["name"] for tool in util.get_tool_list()]
        self.program_combo_box.addItems(self.programs)
        if self.transaction_method == "调用程序":
            index = self.programs.index(self.handle_content) if self.handle_content in self.programs else 0
            self.program_combo_box.setCurrentIndex(index)
        self.program_combo_box.setVisible(self.transaction_method == "调用程序")
        main_layout.addWidget(self.program_combo_box)

        # Button layout
        button_layout = QHBoxLayout()

        # Confirm button
        confirm_button = QPushButton("确定")
        confirm_button.clicked.connect(self.on_confirm)
        button_layout.addWidget(confirm_button)

        # Cancel button
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        main_layout.addLayout(button_layout)

        # Connect signals
        self.button_group.buttonClicked.connect(self.on_profession_selected)
        self.transaction_button_group.buttonClicked.connect(self.on_transaction_selected)

        # Set styles
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #34495e;
            }
            QRadioButton {
                padding: 5px;
                font-size: 13px;
            }
            QRadioButton:checked {
                color: #2980b9;
                font-weight: bold;
            }
            QScrollArea {
                border: 1px solid #bdc3c7;
                border-radius: 3px;
            }
            QLineEdit {
                padding: 5px;
                font-size: 13px;
            }
            QComboBox {
                padding: 5px;
                font-size: 13px;
            }
        """)

    def on_profession_selected(self, button):
        """Handle profession selection"""
        profession_text = button.text()

        # Show/hide custom input
        if profession_text == "其他职业":
            self.custom_input.setVisible(True)
            self.custom_input.setFocus()
        else:
            self.custom_input.setVisible(False)

        # Record selection
        self.selected_profession = profession_text
        self.custom_profession = self.custom_input.text().strip() if profession_text == "其他职业" else ""

    def on_transaction_selected(self, button):
        """Handle transaction method selection"""
        transaction_text = button.text()
        self.transaction_method = transaction_text

        # Show/hide corresponding controls
        if transaction_text == "发送消息":
            self.message_input.setVisible(True)
            self.program_combo_box.setVisible(False)
        elif transaction_text == "调用程序":
            self.message_input.setVisible(False)
            self.program_combo_box.setVisible(True)

    def on_confirm(self):
        """Handle the confirm button click event"""
        profession_to_save = self.selected_profession if self.selected_profession != "其他职业" else self.custom_input.text().strip()

        values_to_update = {
            'money': self.current_funds,
            'profession': profession_to_save,
            'handle_after_trade': self.transaction_method,
            'handle_content': self.message_input.text().strip() if self.transaction_method == "发送消息" else self.program_combo_box.currentText().strip()
        }

        update_AiChatCfg_map(**values_to_update)

        try:
            url = "http://www.ai-sns.org/api/update-profession/"
            params={
                "nation_id": "AI123451234567890ABCDEF7890",
                "password": "securePassword123!",
                "profession": profession_to_save
            }
            response = requests.post(url, data=params)

            response.raise_for_status()  # 检查 HTTP 状态码
            print(response.json())

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP错误发生: {http_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"请求错误发生: {req_err}")
        except ValueError as json_err:
            print(f"JSON解析错误: {json_err}")



        QMessageBox.information(self, "保存成功", "信息已成功保存到数据库")
        self.accept()

    def get_selection(self):
        """Get user selection result"""
        profession = self.selected_profession if self.selected_profession != "其他职业" else self.custom_profession
        fee = getattr(self.button_group.checkedButton(), 'fee', 0)
        return profession, fee

# Usage example
if __name__ == "__main__":
    app = QApplication(sys.argv)

    dialog = ProfessionDialog()
    if dialog.exec() == QDialog.DialogCode.Accepted:
        profession, fee = dialog.get_selection()
        print(f"选择的职业: {profession}, 开办费: {fee}元")

    sys.exit(app.exec())
