import sys
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QRadioButton,
    QLabel, QLineEdit, QButtonGroup, QScrollArea, QWidget,
    QFrame, QPushButton, QComboBox, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt
import util

class ProfessionDialog(QDialog):
    def __init__(self, current_funds, parent=None):
        super().__init__(parent)
        self.current_funds = current_funds
        self.selected_profession = None
        self.custom_profession = ""
        self.transaction_method = None
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("职业选择")
        self.setMinimumWidth(400)

        # 主布局
        main_layout = QVBoxLayout(self)

        # 当前资金显示
        funds_label = QLabel(f"当前资金: {self.current_funds}元")
        funds_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50; padding: 10px;")
        main_layout.addWidget(funds_label)

        # 创建滚动区域容纳职业选项
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(300)

        # 职业选项组
        professions_widget = QWidget()
        professions_layout = QVBoxLayout(professions_widget)

        # 创建按钮组管理单选
        self.button_group = QButtonGroup(self)

        # 需要开办费的职业
        fee_professions = {
            "医生 (*需要800元开办费)": 800,
            "出租车司机 (*需要1000元开办费)": 1000,
            "食品商贩 (*需要800元开办费)": 800
        }

        # 其他职业列表
        other_professions = [
            "歌手", "国家", "美工设计", "视频制作", "ppt编写",
            "市场研究员", "程序员", "产品经理", "说书", "MCP销售员",
            "软件销售员", "壶拟商品销售员", "心理咨询师", "占星师",
            "法律顾问", "中介", "发传单", "付费知识博主", "其他职业"
        ]

        # 添加需要开办费的职业
        fee_group = QGroupBox("需要开办费的职业")
        fee_layout = QVBoxLayout()

        for prof, fee in fee_professions.items():
            radio = QRadioButton(prof)
            radio.fee = fee
            self.button_group.addButton(radio)
            fee_layout.addWidget(radio)

        fee_group.setLayout(fee_layout)
        professions_layout.addWidget(fee_group)

        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        professions_layout.addWidget(separator)

        # 添加其他职业
        other_group = QGroupBox("其他职业选项")
        other_layout = QVBoxLayout()

        for prof in other_professions:
            radio = QRadioButton(prof)
            radio.fee = 0  # 无开办费
            self.button_group.addButton(radio)
            other_layout.addWidget(radio)

        other_group.setLayout(other_layout)
        professions_layout.addWidget(other_group)

        scroll_area.setWidget(professions_widget)
        main_layout.addWidget(scroll_area)

        # 自定义职业输入框
        self.custom_input = QLineEdit()
        self.custom_input.setPlaceholderText("请输入您的职业...")
        self.custom_input.setVisible(False)  # 默认隐藏
        main_layout.addWidget(self.custom_input)

        # 交易结束后处理方式选项
        transaction_group = QGroupBox("交易结束后处理方式")
        transaction_layout = QVBoxLayout()
        self.transaction_button_group = QButtonGroup(self)

        send_message_radio = QRadioButton("发送消息")
        self.transaction_button_group.addButton(send_message_radio)
        transaction_layout.addWidget(send_message_radio)

        call_program_radio = QRadioButton("调用程序")
        self.transaction_button_group.addButton(call_program_radio)
        transaction_layout.addWidget(call_program_radio)

        transaction_group.setLayout(transaction_layout)
        main_layout.addWidget(transaction_group)

        # 消息输入框
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("请输入要发送的消息...")
        self.message_input.setVisible(False)  # 默认隐藏
        main_layout.addWidget(self.message_input)

        # 呼叫程序的选项组合框
        self.program_combo_box = QComboBox()

        # 程序列表
        provided_tool_list = util.get_tool_list()

        self.programs = [
                            "请选择要调用的程序或工具"
                        ] + [tool["name"] for tool in provided_tool_list]  # 使用列表推导式遍历并提取名称

        self.program_combo_box.addItems(self.programs)
        self.program_combo_box.setVisible(False)  # 默认隐藏
        main_layout.addWidget(self.program_combo_box)

        # 创建按钮布局
        button_layout = QHBoxLayout()

        # 确认按钮
        confirm_button = QPushButton("确定")
        confirm_button.clicked.connect(self.on_confirm)
        button_layout.addWidget(confirm_button)

        # 取消按钮
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)  # 连接到 QDialog 的 reject()
        button_layout.addWidget(cancel_button)

        main_layout.addLayout(button_layout)

        # 连接信号
        self.button_group.buttonClicked.connect(self.on_profession_selected)
        self.transaction_button_group.buttonClicked.connect(self.on_transaction_selected)

        # 设置样式
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
        """处理职业选择事件"""
        profession_text = button.text()

        # 显示/隐藏自定义输入框
        if profession_text == "其他职业":
            self.custom_input.setVisible(True)
            self.custom_input.setFocus()
        else:
            self.custom_input.setVisible(False)

        # 记录选择
        self.selected_profession = profession_text
        self.custom_profession = self.custom_input.text().strip() if profession_text == "其他职业" else ""

    def on_transaction_selected(self, button):
        """处理交易结束后的方式选择事件"""
        transaction_text = button.text()
        self.transaction_method = transaction_text

        # 显示/隐藏相应控件
        if transaction_text == "发送消息":
            self.message_input.setVisible(True)
            self.program_combo_box.setVisible(False)
        elif transaction_text == "调用程序":
            self.message_input.setVisible(False)
            self.program_combo_box.setVisible(True)

    def on_confirm(self):
        """处理确认按钮点击事件"""
        if self.transaction_method == "发送消息":
            message = self.message_input.text().strip()
            if message:
                QMessageBox.information(self, "消息", f"发送的消息: {message}")
            else:
                QMessageBox.warning(self, "警告", "请输入要发送的消息")
        elif self.transaction_method == "调用程序":
            selected_program = self.program_combo_box.currentText()
            QMessageBox.information(self, "程序调用", f"呼叫程序: {selected_program}")

        self.accept()

    def get_selection(self):
        """获取用户选择结果"""
        if self.selected_profession == "其他职业" and self.custom_profession:
            return self.custom_profession, 0
        elif self.selected_profession:
            button = self.button_group.checkedButton()
            return self.selected_profession, getattr(button, 'fee', 0)
        return None, 0


# 使用示例
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 假设当前资金为5000元
    dialog = ProfessionDialog(current_funds=5000)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        profession, fee = dialog.get_selection()
        print(f"选择的职业: {profession}, 开办费: {fee}元")

    sys.exit(app.exec())
