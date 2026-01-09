import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QFormLayout, QFrame, QApplication
)
from db.DBFactory import query_AiChatCfg_map, update_AiChatCfg_map
import util
from i18n import lt

class EventProgramDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(lt("Select a tool to help AI making decision","选择工具辅助AI决策"))
        self.setMinimumWidth(500)
        self.setWindowIcon(QIcon("images/aisns.png"))
        # Fetch the current configuration from the database
        self.record = query_AiChatCfg_map()

        # Event-to-database-field mapping
        self.event_field_mapping = {
            "审核调整行动决策因素": "event_before_decistion",
            "审核调整行动决策结果": "event_after_decistion",
            "预处理收到的消息": "event_receive_msg",
            "审核调整对话内容": "event_before_send_msg",
            # "移动前": "event_before_move",
            # "移动后": "event_after_move",
            # "工具使用前": "event_before_use_tool",
            # "工具使用后": "event_after_use_tool",
        }

        # Events and programs
        self.events = list(self.event_field_mapping.keys())

        self.programs = ["N/A"] + [
            tool["name"] for tool in util.get_tool_list()
        ]

        # Combo boxes to field name mapping
        self.combo_boxes = {}

        # Build UI components
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Create combo boxes for each event and initialize with database values
        for event in self.events:
            label = QLabel(event)
            label.setStyleSheet("font-weight: bold;")

            combo = QComboBox()
            combo.addItems(self.programs)

            # Set current index based on existing record
            field_name = self.event_field_mapping[event]
            current_value = getattr(self.record, field_name, None)  # Use getattr to access ORM fields safely
            current_index = self.programs.index(current_value) if current_value in self.programs else 0
            combo.setCurrentIndex(current_index)

            self.combo_boxes[event] = combo
            form_layout.addRow(label, combo)

        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)

        # Button layout
        button_layout = QHBoxLayout()
        confirm_button = QPushButton("确定")
        confirm_button.clicked.connect(self.on_confirm)
        button_layout.addWidget(confirm_button)

        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        # Add layouts to main layout
        main_layout.addLayout(form_layout)
        main_layout.addWidget(separator)
        main_layout.addLayout(button_layout)

        # Set style
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
        """Handle the confirm button click event"""
        updated_values = {}
        for event, combo in self.combo_boxes.items():
            selected_program = combo.currentText()
            if selected_program != "":
                field_name = self.event_field_mapping[event]
                updated_values[field_name] = selected_program

        if updated_values:
            update_AiChatCfg_map(**updated_values)
            print("Database updated with:", updated_values)
        else:
            print("No changes made.")

        self.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = EventProgramDialog()
    dialog.exec()
    sys.exit(app.exec())
