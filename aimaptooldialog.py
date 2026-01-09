from PyQt6 import QtWidgets
from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QPen, QPainterPath
from PyQt6.QtWidgets import (QApplication, QDialog, QWidget, QGridLayout, QGroupBox,
                             QHBoxLayout, QLabel, QLineEdit, QStackedWidget, QVBoxLayout,
                             QDialogButtonBox, QRadioButton, QTextEdit, QSizePolicy)

from db.DBFactory import update_map_tool, update_function_mng_with_id, update_PluginMng, update_skill_mng_with_id, update_mcp_mng_with_id
from i18n import lt

class ConfigDialog(QDialog):
    configured = pyqtSignal(str)
    connectcancel = pyqtSignal(str)

    def __init__(self, parent=None, record=None):
        super(ConfigDialog, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.resize(800, 400)

        self.record = record
        self.app = parent

        self.generalPage = GeneralPage(self.record, parent=self.app)
        self.pagesWidget = QStackedWidget()
        self.pagesWidget.addWidget(self.generalPage)

        horizontalLayout = QHBoxLayout()
        horizontalLayout.addWidget(self.pagesWidget, 1)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(horizontalLayout)
        mainLayout.addStretch(1)
        mainLayout.addSpacing(12)

        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttonBox.button(QDialogButtonBox.StandardButton.Ok).setText(lt("OK", "确定"))
        buttonBox.button(QDialogButtonBox.StandardButton.Cancel).setText(lt("Cancel", "取消"))
        buttonBox.accepted.connect(self.accept_close)
        buttonBox.rejected.connect(self.reject_close)

        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)
        self.setWindowTitle(lt("Detail", "详情"))

    def accept_close(self):
        record_id = self.record.id
        if record_id.startswith("9"):
            record_id_int = int(record_id[1:])
            update_PluginMng(
                record_id_int,
                confirm_needed=int(self.generalPage.confirmRadioYes.isChecked()),
                can_be_sold=int(self.generalPage.sellRadioYes.isChecked())
            )
        elif record_id.startswith("8"):
            record_id_int = int(record_id[1:])
            update_function_mng_with_id(
                record_id_int,
                confirm_needed=int(self.generalPage.confirmRadioYes.isChecked()),
                can_be_sold=int(self.generalPage.sellRadioYes.isChecked())
            )
        elif record_id.startswith("7"):
            record_id_int = int(record_id[1:])
            update_skill_mng_with_id(
                record_id_int,
                confirm_needed=int(self.generalPage.confirmRadioYes.isChecked()),
                can_be_sold=int(self.generalPage.sellRadioYes.isChecked())
            )
        elif record_id.startswith("6"):
            record_id_int = int(record_id[1:])
            update_mcp_mng_with_id(
                record_id_int,
                confirm_needed=int(self.generalPage.confirmRadioYes.isChecked()),
                can_be_sold=int(self.generalPage.sellRadioYes.isChecked())
            )


        self.accept()
        self.close()

    def reject_close(self):
        self.close()


class GeneralPage(QWidget):
    def __init__(self, record, parent=None):
        super(GeneralPage, self).__init__(parent)
        self.record = record

        basicGroup = QGroupBox(lt("Basic Information", "基本信息"))

        self.nameLabel = QLabel(lt("Name:", "名称:"))
        self.nameEdit = QLabel()  # Changed QLineEdit to QLabel

        self.typeLabel = QLabel(lt("Type:", "类型:"))
        self.typeValueLabel = QLabel(lt("Your Type", "您的类型"))

        self.detailLabel = QLabel(lt("Detailed Introduction:", "详细介绍:"))
        self.detailEdit = QTextEdit()
        self.detailEdit.setReadOnly(True)

        self.confirmLabel = QLabel(lt("Usage Confirmation Required:", "使用是否需要确认:"))
        self.confirmRadioYes = QRadioButton(lt("Yes", "是"))
        self.confirmRadioNo = QRadioButton(lt("No", "否"))

        self.sellLabel = QLabel(lt("Available for Sale:", "是否可用于销售:"))
        self.sellRadioYes = QRadioButton(lt("Yes", "是"))
        self.sellRadioNo = QRadioButton(lt("No", "否"))

        confirmGroup = QtWidgets.QButtonGroup(self)
        confirmGroup.addButton(self.confirmRadioYes)
        confirmGroup.addButton(self.confirmRadioNo)

        sellGroup = QtWidgets.QButtonGroup(self)
        sellGroup.addButton(self.sellRadioYes)
        sellGroup.addButton(self.sellRadioNo)

        basicLayout = QGridLayout()
        basicLayout.addWidget(self.nameLabel, 0, 0, 1, 1, Qt.AlignmentFlag.AlignLeft)  # Align left
        basicLayout.addWidget(self.nameEdit, 0, 1, 1, 2)
        basicLayout.addWidget(self.typeLabel, 1, 0, 1, 1, Qt.AlignmentFlag.AlignLeft)  # Align left
        basicLayout.addWidget(self.typeValueLabel, 1, 1, 1, 2)
        basicLayout.addWidget(self.detailLabel, 2, 0, 1, 1, Qt.AlignmentFlag.AlignLeft)  # Align left
        basicLayout.addWidget(self.detailEdit, 2, 1, 1, 2)
        basicLayout.addWidget(self.confirmLabel, 3, 0, 1, 1, Qt.AlignmentFlag.AlignLeft)  # Align left
        basicLayout.addWidget(self.confirmRadioYes, 3, 1)
        basicLayout.addWidget(self.confirmRadioNo, 3, 2)
        basicLayout.addWidget(self.sellLabel, 4, 0, 1, 1, Qt.AlignmentFlag.AlignLeft)  # Align left
        basicLayout.addWidget(self.sellRadioYes, 4, 1)
        basicLayout.addWidget(self.sellRadioNo, 4, 2)
        basicGroup.setLayout(basicLayout)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(basicGroup)
        mainLayout.addStretch(1)
        self.setLayout(mainLayout)

        if record is not None:
            self.fill_form_with_record(record)

    def fill_form_with_record(self, record):
        """Fill form with record data."""
        self.nameEdit.setText(record.name)
        self.detailEdit.setPlainText(record.description)
        self.typeValueLabel.setText(record.plugin_type)
        self.confirmRadioYes.setChecked(record.confirm_needed == 1)
        self.confirmRadioNo.setChecked(record.confirm_needed == 0)
        self.sellRadioYes.setChecked(record.can_be_sold == 1)
        self.sellRadioNo.setChecked(record.can_be_sold == 0)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    dialog = ConfigDialog()
    sys.exit(dialog.exec())
