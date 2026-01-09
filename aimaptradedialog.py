import webbrowser
import random
import string
import datetime
from PyQt6 import QtWidgets
from PyQt6.QtCore import QSize, Qt, QRect, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QPen, QPainterPath
from PyQt6.QtWidgets import (QApplication, QComboBox, QDialog, QGridLayout,
                             QGroupBox, QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QStackedWidget, QVBoxLayout, QWidget, QDialogButtonBox,
                             QRadioButton, QMessageBox, QTextEdit, QPlainTextEdit,
                             QSizePolicy)
from PyQt6.QtWidgets import (QApplication, QCheckBox, QColorDialog, QDialog,
                             QErrorMessage, QFileDialog, QFontDialog, QFrame, QGridLayout,
                             QInputDialog, QLabel, QLineEdit, QMessageBox, QPushButton, QStatusBar)
from PyQt6.QtGui import QDoubleValidator
from db.DBFactory import add_AgentCfg,query_AgentCfg,query_AgentCfg_All,update_AgentCfg,delete_AgentCfg,add_map_task,update_map_task,query_single_map_task,update_map_trade,add_map_trade
from i18n import lt


class ConfigDialog(QDialog):
    configured = pyqtSignal(str, str, str, str)
    connectcancel = pyqtSignal(str)

    def __init__(self, parent=None, trade_record=None):
        super(ConfigDialog, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.resize(800, 600)  # 扩大窗口以适应更多字段

        self.trade_record = trade_record
        self.app = parent

        self.generalPage = TradeGeneralPage(self.trade_record, parent=self.app)
        self.pagesWidget = QStackedWidget()
        self.pagesWidget.addWidget(self.generalPage)

        horizontalLayout = QHBoxLayout()
        horizontalLayout.addWidget(self.pagesWidget, 1)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(horizontalLayout)
        mainLayout.addStretch(1)
        mainLayout.addSpacing(12)

        # 添加确定和取消按钮
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setText(lt("OK", "确定"))
        cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_button.setText(lt("Cancel", "取消"))
        button_box.accepted.connect(self.accept_close)
        button_box.rejected.connect(self.reject_close)

        mainLayout.addWidget(button_box)
        self.setLayout(mainLayout)
        self.setWindowTitle(lt("Trade Record", "交易记录"))

    def accept_close(self):
        # 获取通用页面数据
        trade_id = self.generalPage.tradeIdEdit.text()
        if not trade_id:
            QMessageBox.warning(self, "警告", "交易ID不能为空。")
            return

        title = self.generalPage.titleEdit.text()
        if not title:
            QMessageBox.warning(self, "警告", "标题不能为空。")
            return

        detail = self.generalPage.detailEdit.toPlainText()
        trade_type = self.generalPage.typeCombo.currentText()
        link = self.generalPage.linkEdit.text()
        trade_with_name = self.generalPage.tradeWithNameEdit.text()
        trade_with_account = self.generalPage.tradeWithAccountEdit.text()
        trade_with_company = self.generalPage.companyCheck.isChecked()
        pay = float(self.generalPage.payEdit.text()) if self.generalPage.payEdit.text() else 0.0
        pay_method = self.generalPage.payMethodEdit.text()
        status = self.generalPage.statusCombo.currentText()

        # 更新或创建交易记录
        if self.trade_record is None:
            record_id = add_map_trade(
                trade_id=trade_id,
                title=title,
                detail=detail,
                trade_type=trade_type,
                link=link,
                trade_with_name=trade_with_name,
                trade_with_account=trade_with_account,
                trade_with_company=trade_with_company,
                pay=pay,
                pay_method=pay_method,
                status=status
            )
            # 这里可以添加对新记录的处理逻辑
        else:
            update_map_trade(
                self.trade_record.trade_id,
                title=title,
                detail=detail,
                trade_type=trade_type,
                link=link,
                trade_with_name=trade_with_name,
                trade_with_account=trade_with_account,
                trade_with_company=trade_with_company,
                pay=pay,
                pay_method=pay_method,
                status=status
            )
            # 这里可以添加对更新记录的处理逻辑

        self.accept()
        self.close()

    def reject_close(self):
        self.close()

    def generate_random_id(self):
        """生成随机交易ID"""
        random_id = ''.join(random.choices(string.ascii_uppercase, k=2))
        current_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        random_number = ''.join(random.choices(string.digits, k=5))
        return f"{random_id}{current_time}{random_number}"


class TradeGeneralPage(QWidget):
    def __init__(self, trade_record, parent=None):
        super(TradeGeneralPage, self).__init__(parent)
        self.trade_record = trade_record
        self.app = parent

        # 基本信息组
        basicGroup = QGroupBox(lt("Basic Information", "基本信息"))

        # 交易ID
        self.tradeIdLabel = QLabel(lt("Trade ID:", "交易ID:"))
        self.tradeIdEdit = QLineEdit()
        self.tradeIdEdit.setText(self.generate_random_id() if trade_record is None else trade_record.trade_id)

        # 交易类型
        self.typeLabel = QLabel(lt("Trade Type:", "交易类型:"))
        self.typeCombo = QComboBox()
        self.typeCombo.addItems(["Buy", "Sell"])

        # 标题
        self.titleLabel = QLabel(lt("Title:", "标题:"))
        self.titleEdit = QLineEdit()


        # 详情
        self.detailLabel = QLabel(lt("Detail:", "详情:"))
        self.detailEdit = QPlainTextEdit()
        self.detailEdit.setFixedHeight(100)

        # 链接
        self.linkLabel = QLabel(lt("Link:", "链接:"))
        self.linkEdit = QLineEdit()
        self.linkLabel.setVisible(False)
        self.linkEdit.setVisible(False)

        # 基本信息布局
        basicLayout = QGridLayout()
        basicLayout.addWidget(self.tradeIdLabel, 0, 0)
        basicLayout.addWidget(self.tradeIdEdit, 0, 1)
        basicLayout.addWidget(self.typeLabel, 1, 0)
        basicLayout.addWidget(self.typeCombo, 1, 1)
        basicLayout.addWidget(self.titleLabel, 2, 0)
        basicLayout.addWidget(self.titleEdit, 2, 1)
        basicLayout.addWidget(self.detailLabel, 3, 0)
        basicLayout.addWidget(self.detailEdit, 3, 1)
        # basicLayout.addWidget(self.linkLabel, 4, 0)
        # basicLayout.addWidget(self.linkEdit, 4, 1)
        basicGroup.setLayout(basicLayout)

        # 交易对象组
        tradeWithGroup = QGroupBox(lt("Trade With", "交易对象"))

        # 交易对象名称
        self.tradeWithNameLabel = QLabel(lt("Name:", "名称:"))
        self.tradeWithNameEdit = QLineEdit()

        # 交易对象账号
        self.tradeWithAccountLabel = QLabel(lt("Account:", "账号:"))
        self.tradeWithAccountEdit = QLineEdit()

        # 是否公司交易
        self.companyCheck = QCheckBox(lt("Is Company", "公司交易"))
        self.companyCheck.setVisible(False)

        # 交易对象布局
        tradeWithLayout = QGridLayout()
        tradeWithLayout.addWidget(self.tradeWithNameLabel, 0, 0)
        tradeWithLayout.addWidget(self.tradeWithNameEdit, 0, 1)
        tradeWithLayout.addWidget(self.tradeWithAccountLabel, 1, 0)
        tradeWithLayout.addWidget(self.tradeWithAccountEdit, 1, 1)
        # tradeWithLayout.addWidget(self.companyCheck, 2, 0, 1, 2)
        tradeWithGroup.setLayout(tradeWithLayout)

        # 支付信息组
        paymentGroup = QGroupBox(lt("Payment Information", "支付信息"))

        # 付款金额
        self.payLabel = QLabel(lt("Amount:", "金额:"))
        self.payEdit = QLineEdit()
        self.payEdit.setValidator(QDoubleValidator(0, 9999999, 2, self))

        # 付款方式
        self.payMethodLabel = QLabel(lt("Method:", "方式:"))
        self.payMethodEdit = QLineEdit()
        self.payMethodLabel.setVisible(False)
        self.payMethodEdit.setVisible(False)

        # 状态
        self.statusLabel = QLabel(lt("Status:", "状态:"))
        self.statusCombo = QComboBox()
        self.statusCombo.addItems(["Paid", "Completed"])

        # 支付信息布局
        paymentLayout = QGridLayout()
        paymentLayout.addWidget(self.payLabel, 0, 0)
        paymentLayout.addWidget(self.payEdit, 0, 1)
        # paymentLayout.addWidget(self.payMethodLabel, 1, 0)
        # paymentLayout.addWidget(self.payMethodEdit, 1, 1)
        paymentLayout.addWidget(self.statusLabel, 2, 0)
        paymentLayout.addWidget(self.statusCombo, 2, 1)
        paymentGroup.setLayout(paymentLayout)

        # 主布局
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(basicGroup)
        mainLayout.addSpacing(12)
        mainLayout.addWidget(tradeWithGroup)
        mainLayout.addSpacing(12)
        mainLayout.addWidget(paymentGroup)
        mainLayout.addSpacing(12)
        self.setLayout(mainLayout)

        # 如果提供了交易记录，填充表单
        if trade_record is not None:
            self.fill_form_with_record(trade_record)

    def fill_form_with_record(self, record):
        """用交易记录数据填充表单"""
        self.tradeIdEdit.setText(record.trade_id)
        self.typeCombo.setCurrentText(record.trade_type)
        self.titleEdit.setText(record.title)
        self.detailEdit.setPlainText(record.detail)
        self.linkEdit.setText(record.link)
        self.tradeWithNameEdit.setText(record.trade_with_name)
        self.tradeWithAccountEdit.setText(record.trade_with_account)
        self.companyCheck.setChecked(record.trade_with_company)
        self.payEdit.setText(str(record.pay))
        self.payMethodEdit.setText(record.pay_method)
        self.statusCombo.setCurrentText(str(record.status))

    def generate_random_id(self):
        """生成随机交易ID"""
        random_id = ''.join(random.choices(string.ascii_uppercase, k=2))
        current_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        random_number = ''.join(random.choices(string.digits, k=5))
        return f"{random_id}{current_time}{random_number}"


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    dialog = ConfigDialog()
    sys.exit(dialog.exec())
