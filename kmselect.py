from PyQt6.QtCore import QFile, QFileInfo, Qt
from PyQt6.QtGui import QStandardItem, QStandardItemModel, QIcon, QAction
from PyQt6.QtWidgets import QApplication, QDialog, QMenu, QTableView, QVBoxLayout, QAbstractItemView, QDialogButtonBox, QMessageBox, QCheckBox, QHeaderView
from i18n import lt

class FreezeTableDialog(QDialog):
    def __init__(self, model):
        super(FreezeTableDialog, self).__init__()
        self.model = model
        self.tableView = QTableView(self)
        self.tableView.setModel(self.model)
        self.tableView.setColumnHidden(1, True)
        self.tableView.setColumnWidth(0, 10)#设置这一列否则第二列长度过长
        self.checkbox_states_and_values=[]
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.addWidget(self.tableView)

        # Add "Select All" checkbox
        select_all_checkbox = QCheckBox(lt("All","全选"), self)
        select_all_checkbox.stateChanged.connect(self.toggle_select_all)
        layout.addWidget(select_all_checkbox)

        # Add OK and Cancel buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept_close)
        button_box.rejected.connect(self.reject_close)

        layout.addWidget(button_box)

        self.setLayout(layout)
        self.setWindowTitle(lt("Select a KB","请选择知识库"))
        self.setWindowIcon(QIcon("images/aisns.png"))
        self.resize(560, 680)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        # 使表格铺满窗口
        self.tableView.horizontalHeader().setStretchLastSection(True)
        # 允许用户手动调整列宽
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        # 调整列宽
        self.adjust_column_widths()

    def adjust_column_widths(self):
        """调整列宽，确保列宽为整数"""
        total_width = self.width() - 100
        if total_width <= 0:
            return

        # 设置列宽，确保使用整数
        self.tableView.setColumnWidth(0, 10)  # 选择列宽
        # self.tableView.setColumnWidth(1, int(total_width * 0.4))  # 隐藏
        self.tableView.setColumnWidth(2, int(total_width * 0.3))  # 说明列宽
        self.tableView.setColumnWidth(3, int(total_width * 0.4))  # 类型列宽
        self.tableView.setColumnWidth(4, int(total_width * 0.15))  # 编辑时间列宽
        self.tableView.setColumnWidth(5, int(total_width * 0.15))  # 编辑时间列宽



    def toggle_select_all(self, state):
        for row in range(self.model.rowCount()):
            checkbox_item = self.model.item(row, 0)
            if checkbox_item:
                checkbox_item.setCheckState(Qt.CheckState.Checked if state == Qt.CheckState.Checked.value else Qt.CheckState.Unchecked)


    def accept_close(self):
        checkbox_states_and_values = []
        for row in range(self.model.rowCount()):
            checkbox_item = self.model.item(row, 0)
            if checkbox_item and checkbox_item.checkState() == Qt.CheckState.Checked:
                second_column_data = self.model.index(row, 1).data()
                name = self.model.index(row, 2).data()
                vector_path= self.model.index(row, 5).data()
                # self.checkbox_states_and_values.append((row, second_column_data,vector_path))
                self.checkbox_states_and_values.append(name)

        # if not self.checkbox_states_and_values:
        #     QMessageBox.warning(self, "No Selection", "Please select at least one row.")
        #     return

        print('OK, I accept')
        # for row, value,para in self.checkbox_states_and_values:
        #     print(f'Row {row + 1}, Content of the second column: {value}')

        self.accept()

    def getResult(self):
        """返回用户输入的文本"""
        return self.checkbox_states_and_values

    def reject_close(self):
        print("reject")
        self.reject()#这是系统函数

    def showContextMenu(self, pos):
            selected_rows = self.tableView.selectionModel().selectedRows()

            if selected_rows:
                menu = QMenu(self)
                actions = [("删除", self.deleteSelectedRows),
                           ("上移", self.moveSelectedRowsUp),
                           ("下移", self.moveSelectedRowsDown)]

                for action_text, action_method in actions:
                    action = QAction(action_text, self)
                    action.triggered.connect(action_method)
                    menu.addAction(action)

                menu.exec(self.mapToGlobal(pos))

    def deleteSelectedRows(self):
        selected_indexes = self.tableView.selectionModel().selectedRows()
        if selected_indexes:
            rows_to_delete = [index.row() for index in selected_indexes]
            for row in reversed(rows_to_delete):
                self.model.removeRow(row)
            self.model.layoutChanged.emit()

    def moveSelectedRowsUp(self):
        selected_indexes = self.tableView.selectionModel().selectedRows()
        if selected_indexes:
            rows_to_move = [index.row() for index in selected_indexes]
            for row in rows_to_move:
                if row > 0:
                    self.model.insertRow(row - 1, self.model.takeRow(row))
            self.model.layoutChanged.emit()

    def moveSelectedRowsDown(self):
        selected_indexes = self.tableView.selectionModel().selectedRows()
        if selected_indexes:
            rows_to_move = [index.row() for index in selected_indexes]
            for row in reversed(rows_to_move):
                if row < self.model.rowCount() - 1:
                    self.model.insertRow(row + 1, self.model.takeRow(row))
            self.model.layoutChanged.emit()


def main(args):
    def split_and_strip(s, splitter):
        return [s.strip() for s in line.split(splitter)]

    app = QApplication(args)
    model = QStandardItemModel()
    file = QFile(QFileInfo(__file__).absolutePath() + '/grades.txt')
    if file.open(QFile.ReadOnly):
        line = file.readLine(200).decode('utf-8')
        header = split_and_strip(line, ',')
        model.setHorizontalHeaderLabels(header)
        row = 0
        while file.canReadLine():
            line = file.readLine(200).decode('utf-8')
            if not line.startswith('#') and ',' in line:
                fields = split_and_strip(line, ',')
                # Create a checkbox in the first column
                checkbox_item = QStandardItem()
                checkbox_item.setCheckable(True)
                model.setItem(row, 0, checkbox_item)
                for col, field in enumerate(fields):
                    newItem = QStandardItem(field)
                    newItem.setFlags(newItem.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    model.setItem(row, col+1, newItem)
                row += 1
    file.close()

    dialog = FreezeTableDialog(model)
    dialog.exec()

if __name__ == '__main__':
    import sys
    main(sys.argv)
