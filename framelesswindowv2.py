import sys
import time

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import Qt, QUrl, QObject, Signal, QThread
from PySide6.QtWebEngineCore import QWebEnginePage


class StatusMonitor(QObject):
    statusChanged = Signal(str)

    def __init__(self):
        super().__init__()
        self._running = True
        self.cur_status = ""

    def read_status(self):
        """
        读取文件中的字符串数据并返回。

        :return: 文件中的字符串数据
        """
        try:
            with open('C:\\tmp\\data.txt', 'r') as file:
                data = file.read().strip()  # 去掉首尾空白字符
                print(f"从文件中读取的数据: {data}")
                return data
        except FileNotFoundError:
            print("文件未找到，请确保文件路径正确。")
            return None

    def run(self):
        """
        监控文件中状态的变化，并发射相应的信号。
        """
        while self._running:
            status = self.read_status()
            if self.cur_status!=status:
                self.statusChanged.emit(status)
                self.cur_status =status
            time.sleep(0.3)  # 每秒检查一次

    def stop(self):
        """
        停止监控。
        """
        self._running = False


class ModelViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置无边框窗口和透明背景
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnBottomHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 创建 QWebEngineView
        self.browser = QWebEngineView()

        # 创建一个按钮
        self.button = QPushButton("Run JavaScript")

        # 设置按钮点击事件
        self.button.clicked.connect(self.on_button_clicked)

        # 创建一个布局
        layout = QVBoxLayout()
        layout.addWidget(self.browser)
        layout.addWidget(self.button)
        self.button.setHidden(True)

        # 创建主widget并设置布局
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # 加载网页
        # self.browser.page().load(QUrl("http://localhost:63342/Stocks_RPA_Python/model_viewer.html?_ijt=ftmfhu0iaovqkemuvk4rscm292"))
        self.browser.page().load(QUrl("http://www.ai-sns.org/model_viewer.html"))
        # 设置背景颜色为透明
        self.browser.page().setBackgroundColor(QColor(0, 0, 0, 0))
        self.browser.setStyleSheet("background: transparent; border: none;")

        # 连接信号
        self.browser.page().featurePermissionRequested.connect(self.on_permission_requested)

        # 初始化监控线程
        self.monitor = StatusMonitor()
        self.thread = QThread()
        self.monitor.moveToThread(self.thread)

        # 连接信号槽
        self.monitor.statusChanged.connect(self.handle_status_change)
        self.thread.started.connect(self.monitor.run)

        # 启动监控线程
        self.thread.start()

    def on_permission_requested(self, url, feature):
        """
        处理网页的权限请求。
        """
        print(f"Permission requested for {feature} on {url.toString()}")
        if feature in (QWebEnginePage.MediaAudioCapture, QWebEnginePage.MediaVideoCapture, 6):
            self.browser.page().setFeaturePermission(
                url,
                feature,
                QWebEnginePage.PermissionGrantedByUser
            )
        else:
            self.browser.page().setFeaturePermission(
                url,
                feature,
                QWebEnginePage.PermissionDeniedByUser
            )

    def on_button_clicked(self):
        """
        按钮点击事件处理器，运行JavaScript代码。
        """
        self.run_js("alert(1)")

    def run_js(self, script):
        """
        运行JavaScript代码。
        """
        self.browser.page().runJavaScript(script)

    def handle_status_change(self, status):
        """
        处理状态变化，根据状态运行相应的JavaScript代码。
        """
        if status == "talk":
            self.run_js("talk()")
        elif status == "idle":
            self.run_js("idle()")
        elif status == "walk":
            self.run_js("walk()")
        elif status == "waitsay":
            self.run_js("waitsay()")
        elif status == "stopsay":
            self.run_js("stopsay()")
        else:
            self.run_js(f"showmessage('{status}')")

    def closeEvent(self, event):
        """
        窗口关闭事件，停止监控线程。
        """
        self.monitor.stop()
        self.thread.quit()
        self.thread.wait()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ModelViewer()
    # viewer.showFullScreen()  # 全屏显示
    viewer.showMaximized()
    sys.exit(app.exec())
