import sys
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QFormLayout, QFrame, QApplication
)
from db.DBFactory import query_AiChatCfg_map, update_AiChatCfg_map
import util

class EventProgramDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("事件接口设置")
        self.setMinimumWidth(500)
        record = query_AiChatCfg_map()

        # 事件列表
        self.events = [
            "行动决策前", "行动决策后", "沟通前", "沟通后",
            "移动前", "移动后", "工具使用前", "工具使用后"
        ]

        provided_tool_list = util.get_tool_list()

        # 程序列表

        self.programs = [
                            "请选择要调用的程序或工具"
                        ] + [tool["name"] for tool in provided_tool_list]  # 使用列表推导式遍历并提取名称


        # 存储所有组合框的字典
        self.combo_boxes = {}

        self.setup_ui()

    def setup_ui(self):
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)

        # 表单布局
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(20)

        # 为每个事件创建组合框
        for event in self.events:
            label = QLabel(event)
            label.setStyleSheet("font-weight: bold;")

            combo = QComboBox()
            combo.addItems(self.programs)
            combo.setCurrentIndex(0)  # 默认选择"请选择"

            # 将组合框存储在字典中
            self.combo_boxes[event] = combo

            form_layout.addRow(label, combo)

        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)

        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # 确定按钮
        confirm_button = QPushButton("确定")
        confirm_button.clicked.connect(self.on_confirm)
        button_layout.addWidget(confirm_button)

        # 取消按钮
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        # 添加到主布局
        main_layout.addLayout(form_layout)
        main_layout.addWidget(separator)
        main_layout.addLayout(button_layout)

        # 设置样式
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                font-size: 13px;
                min-width: 80px;
            }
            QComboBox {
                min-width: 150px;
                padding: 5px;
                font-size: 13px;
            }
            QPushButton {
                min-width: 80px;
                padding: 6px;
            }
            QFrame {
                margin: 10px 0;
            }
        """)

    def on_confirm(self):
        """处理确认按钮点击事件"""
        selections = {}

        for event, combo in self.combo_boxes.items():
            selected_program = combo.currentText()
            if selected_program != "请选择":
                selections[event] = selected_program

        # 打印选择结果
        print("选择的程序设置:")
        for event, program in selections.items():
            print(f"{event}: {program}")

        if not selections:
            print("没有选择任何程序")

        self.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    dialog = EventProgramDialog()
    dialog.exec()

    sys.exit(app.exec())
