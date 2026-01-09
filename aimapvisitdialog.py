from PyQt6 import QtWidgets
from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QLabel, QTextEdit, QSizePolicy
from db.DBFactory import update_map_tool
from i18n import lt


class ConfigDialog(QDialog):
    configured = pyqtSignal(str)
    connectcancel = pyqtSignal(str)

    def __init__(self, parent=None, record=None,type_str="service"):
        super(ConfigDialog, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.resize(800, 400)

        self.record = record
        self.type_str = type_str
        self.app = parent

        self.generalPage = GeneralPage(self.record, parent=self.app,type_str=type_str)

        # Main layout
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.generalPage)
        mainLayout.addStretch(1)
        mainLayout.addSpacing(12)

        # Button box for OK and Cancel
        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttonBox.button(QDialogButtonBox.StandardButton.Ok).setText(lt("Close", "关闭"))

        buttonBox.accepted.connect(self.accept_close)


        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)
        self.setWindowTitle(lt("Detail", "详情"))

    def accept_close(self):

        self.accept()

    def reject_close(self):
        """Close the dialog without saving."""
        self.close()


class GeneralPage(QtWidgets.QWidget):
    def __init__(self, record, parent=None,type_str="service"):
        super(GeneralPage, self).__init__(parent)

        self.record = record
        self.type_str = type_str
        # Layout for detailed introduction only
        detailLayout = QVBoxLayout()

        # Detail label and text area
        self.detailLabel = QLabel(lt("Detail:", "详情:"))
        self.detailEdit = QTextEdit()
        self.detailEdit.setFixedHeight(370)
        self.detailEdit.setStyleSheet("""
        border:solid 1px #00ff00;
        """)
        self.detailEdit.setReadOnly(True)

        # Adding widgets to the layout
        detailLayout.addWidget(self.detailLabel)
        detailLayout.addWidget(self.detailEdit)

        self.setLayout(detailLayout)

        if record is not None:
            self.fill_form_with_record(record)

    def fill_form_with_record(self, record):
        """Fill the detail text area with the record description."""
        lng = record.lng
        lat = record.lat
        if self.type_str == "service":
            service_list = "service_list"
            self.detailEdit.setPlainText(service_list)
        elif self.type_str == "people":
            service_list = "people_list"
            self.detailEdit.setPlainText(service_list)

        elif self.type_str == "place":
            service_list = "place_list"
            self.detailEdit.setPlainText(service_list)


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    dialog = ConfigDialog()
    sys.exit(dialog.exec())
