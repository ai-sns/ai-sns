
import os
import io
import time
import json
import threading
from pynput import mouse, keyboard

from PyQt6.QtWidgets import QGraphicsScene, QInputDialog, QGraphicsTextItem, QGraphicsRectItem, QGraphicsEllipseItem, \
    QGraphicsPathItem, QDialog, QLineEdit
from PyQt6.QtGui import QCursor, QGuiApplication, QPalette
from PyQt6.QtCore import Qt, QRectF, QThread, pyqtSignal

from PyQt6 import QtGui
from PyQt6.QtWidgets import QToolBar,  QGraphicsView, QTextEdit, QTabWidget, QFormLayout, QComboBox, \
    QGraphicsPixmapItem
from PyQt6 import QtCore
from PyQt6.QtCore import QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QShortcut, QAction,QBrush, QIcon, QFont, QPixmap, QPainterPath
from PyQt6.QtWidgets import QPushButton, QHBoxLayout, QLabel, QVBoxLayout, QMessageBox, QFileDialog, QWidget
import shutil

# Import custom modules
from .base import Base
from .utils import *

import sys
import pyautogui
from PyQt6.QtWidgets import QApplication, QRubberBand, QMainWindow
from PyQt6.QtCore import Qt, QRect, QSize
from PyQt6.QtGui import QPainter, QPen, QColor
from util import generate_random_id
from db.DBFactory import add_skill_mng
from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController
sys.path.append("../..")
sys.path.append("../../..")
from i18n import lt
from multiprocessing import Process, Pipe
import subprocess
import sys
import time
import json
from PyQt6.QtCore import QTimer
global storage

# Initialize global variables
def initialize_globals():
    global storage, is_capturing, esc_count, last_esc_time, record_all, name_of_recording, signal_emitter, keyboard_listener, mouse_listener, delay_time,sample
    storage = []
    is_capturing = True
    esc_count = 0
    last_esc_time = 0
    record_all = "record-all"
    name_of_recording = "test008"
    delay_time = 3
    sample = ""


def run_listener():
    """Runs the input listener in a separate process."""
    try:
        listener = InputListener()
        listener.start()
    except Exception as e:
        print(f"Error in listener: {e}")


class InputListener:
    def __init__(self):
        self.log_file_path = "input_log.txt"
        self.command_file_path = "command.txt"
        self.storage_file_path = "storage.txt"
        self.keyboard_listener = None
        self.mouse_listener = None
        self.expect_response = False
        self.command = ""
        self.storage = []
        self.is_capturing = False
        self.esc_count = 0
        self.last_esc_time = 0

    def read_command(self):
        try:
            with open(self.command_file_path, "r") as file:
                command = file.read().strip()
            return command
        except FileNotFoundError:
            return ""

    def write_command(self, command):
        with open(self.command_file_path, "w") as file:
            file.write(command)

    def read_storage(self):
        try:
            with open(self.storage_file_path, "r") as file:
                storage = json.load(file)
            return storage
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def write_storage(self, storage):
        with open(self.storage_file_path, "w") as file:
            json.dump(storage, file)

    def on_press(self, key):
        if key == keyboard.Key.esc:
            if time.time() - self.last_esc_time < 0.5:
                self.esc_count += 1
                if self.esc_count == 2:
                    self.is_capturing = not self.is_capturing
                    self.esc_count = 0
                    if not self.is_capturing:
                        mouse_position = mouse.Controller().position
                        self.write_storage(self.storage)
                        self.write_command(f"SHOW_DIALOG {mouse_position[0]} {mouse_position[1]}")
                    print("State toggled: capturing is now", self.is_capturing)
            else:
                self.esc_count = 1
            self.last_esc_time = time.time()
            return

        if self.is_capturing:
            try:
                char = key.char
            except AttributeError:
                char = str(key)
            json_object = {'action': 'pressed_key', 'key': char, '_time': time.time()}
            print(f"'action': 'pressed_key', 'key': {char}, '_time': {time.time()}")
            self.storage.append(json_object)
            self.write_storage(self.storage)

    def on_release(self, key):
        if key == keyboard.Key.esc:
            return

        if self.is_capturing:
            try:
                char = key.char
            except AttributeError:
                char = str(key)
            mouse_position = mouse.Controller().position
            json_object = {'action': 'released_key', 'x': mouse_position[0], 'y': mouse_position[1], 'key': char,
                           '_time': time.time()}
            self.storage.append(json_object)
            self.write_storage(self.storage)

    def on_move(self, x, y):
        record_all = "record-all"
        if self.is_capturing and record_all:
            json_object = {'action': 'moved', 'x': x, 'y': y, '_time': time.time()}
            print(json_object)
            self.storage.append(json_object)
            self.write_storage(self.storage)

    def on_click(self, x, y, button, pressed):
        print("on_clicking")
        self.write_command(f"MOUSE_CLICK {x} {y} {button}")

        while True:
            time.sleep(0.1)
            command = self.read_command()
            if command:
                if command.startswith("RECORD"):
                    if self.is_capturing:
                        json_object = {'action': 'pressed' if pressed else 'released', 'button': str(button),
                                       'x': x, 'y': y, '_time': time.time()}
                        print(f"'action': {'pressed' if pressed else 'released'}, 'button': {str(button)}, 'x': {x}, 'y': {y}, '_time': {time.time()}")
                        self.storage.append(json_object)
                        self.write_storage(self.storage)
                    break
                elif command.startswith("IGNORE"):
                    break
        self.write_command("")

    def on_scroll(self, x, y, dx, dy):
        if self.is_capturing:
            json_object = {'action': 'scroll', 'vertical_direction': int(dy), 'horizontal_direction': int(dx),
                           'x': x, 'y': y, '_time': time.time()}
            self.storage.append(json_object)
            self.write_storage(self.storage)

    def start(self):
        """Starts the input listeners."""
        with open(self.log_file_path, "a") as self.log_file:
            while True:
                time.sleep(0.1)
                command = self.read_command()
                if command:
                    if command.startswith("START"):
                        if not self.keyboard_listener or not self.keyboard_listener.is_alive():
                            self.keyboard_listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
                            self.keyboard_listener.start()
                        if not self.mouse_listener or not self.mouse_listener.is_alive():
                            self.mouse_listener = mouse.Listener(on_click=self.on_click, on_move=self.on_move,
                                                                 on_scroll=self.on_scroll)
                            self.mouse_listener.start()
                    elif command.startswith("STOP"):
                        if self.keyboard_listener:
                            self.keyboard_listener.stop()
                            self.keyboard_listener = None
                        if self.mouse_listener:
                            self.mouse_listener.stop()
                            self.mouse_listener = None
                    elif command.startswith("PAUSE"):
                        self.is_capturing = False
                    elif command.startswith("RESUME"):
                        self.is_capturing = True
                    elif command.startswith("STORAGE"):
                        self.write_storage(self.storage)
                    elif command.startswith("RETURN_STORAGE"):
                        self.storage = self.read_storage()
                    elif command.startswith("EXIT"):
                        break
                    self.write_command("")


class KeyboardMouseWorkerThread(QWidget):
    finished = pyqtSignal(str)
    show_dialog_signal = pyqtSignal(int, int, list)
    storage_sent = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        global storage
        self.process = subprocess.Popen([sys.executable, "inputoperate.py"])

        self._running = False
        self.screen_bar = None
        self.receive_storage = False
        self.storage = []
        self.is_capturing = False
        self.esc_count = 0
        self.last_esc_time = 0
        self.operate_bar = None
        self.is_operating = True
        self.number_of_plays = 1
        self.gstatus = ""
        self.gvalue = ""
        self.skill_name = ""

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_for_events)
        self.timer.start(100)

    def set_screen_bar(self, screen_bar):
        self.screen_bar = screen_bar

    def set_operate_bar(self, operate_bar):
        self.operate_bar = operate_bar

    def re_init(self):
        self.storage = []
        self.is_capturing = False
        self.esc_count = 0
        self.last_esc_time = 0

    def run(self):
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as keyboard_listener:
            self.keyboard_listener = keyboard_listener
            self._running = True
            keyboard_listener.join()

    def start(self):
        self.write_command("START")

    def stop(self):
        self.write_command("STOP")

    def stop_capturing(self):
        self.write_command("STOP")
        self.read_storage()

    def pause_capturing(self):
        self.is_capturing = False
        self.write_command("PAUSE")

    def resume_capturing(self):
        self.is_capturing = True
        self.write_command("RESUME")

    def start_capturing(self):
        self.re_init()
        self.is_capturing = True
        self.write_command("START")

    def get_is_capturing(self):
        return self.is_capturing

    def set_is_capturing(self, is_capturing):
        self.is_capturing = is_capturing

    def get_storage_to_end(self):
        self.write_command("STORAGE")

    def get_storage(self):
        global storage
        self.storage=self.read_storage()
        storage = self.storage
        return storage

    def update_storage(self):
        global storage
        self.storage = storage
        self.write_storage(storage)
        self.write_command(f"RETURN_STORAGE")

    def check_for_events(self):
        global storage
        command = self.read_command()
        if command:
            if command.startswith("MOUSE_CLICK"):
                params = command.split()
                x, y, button = float(params[1]), float(params[2]), params[3]
                if not self.is_screen_bar_under_cursor():
                    self.write_command("RECORD")
                else:
                    self.write_command("IGNORE")
            elif command.startswith("STORAGE"):
                self.receive_storage = True
                self.storage = self.read_storage()
                storage = self.storage
                self.storage_sent.emit(self.storage)
            elif command.startswith("SHOW_DIALOG"):
                self.read_storage()
                params = command.split()
                x, y = float(params[1]), float(params[2])
                self.show_dialog_signal.emit(x, y, self.read_storage())

    def is_screen_bar_under_cursor(self):
        screen_bar = self.screen_bar
        if screen_bar:
            pos = screen_bar.mapFromGlobal(screen_bar.cursor().pos())
            return screen_bar.rect().contains(pos)
        else:
            return False

    def read_command(self):
        try:
            with open("command.txt", "r") as file:
                command = file.read().strip()
            return command
        except FileNotFoundError:
            return ""

    def write_command(self, command):
        with open("command.txt", "w") as file:
            file.write(command)

    def read_storage(self):
        global storage
        try:
            with open("storage.txt", "r") as file:
                storage = json.load(file)
            return storage
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def write_storage(self, storage):
        with open("storage.txt", "w") as file:
            json.dump(storage, file)


# Custom QGraphicsView to handle drawing and annotations
class CustomGraphicsView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.mode = None
        self.drawing = False
        self.start_point = None
        self.item = None

    def setPixmap(self, pixmap):
        self.scene().clear()
        self.pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene().addItem(self.pixmap_item)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_point = self.mapToScene(event.pos())
            self.drawing = True
            if self.mode == "annotate_free":
                self.path_item = QPainterPath(self.start_point)
            elif self.mode in {"annotate_box", "crop_rect", "crop_circle"}:
                if self.item:
                    self.scene().removeItem(self.item)
                    self.item = None
            elif self.mode == "annotate_text":
                text, ok = QInputDialog.getText(self, 'Text Annotation', 'Enter text:')
                if ok:
                    text_item = QGraphicsTextItem(text)
                    text_item.setPos(self.start_point)
                    text_item.setFlags(QGraphicsTextItem.ItemIsMovable | QGraphicsTextItem.ItemIsSelectable)
                    self.scene().addItem(text_item)

    def mouseMoveEvent(self, event):
        if self.drawing:
            end_point = self.mapToScene(event.pos())
            if self.mode == "annotate_free":
                if self.path_item:
                    self.path_item.lineTo(end_point)
                    pen = QPen(Qt.GlobalColor.blue, 2, Qt.PenStyle.SolidLine)
                    if self.item:
                        self.scene().removeItem(self.item)
                    self.item = QGraphicsPathItem(self.path_item)
                    self.item.setPen(pen)
                    self.item.setFlags(QGraphicsPathItem.GraphicsItemFlag.ItemIsMovable | QGraphicsPathItem.GraphicsItemFlag.ItemIsSelectable)
                    self.scene().addItem(self.item)
            elif self.mode == "annotate_box" or self.mode == "crop_rect":
                if self.item:
                    self.scene().removeItem(self.item)
                rect = QRectF(self.start_point, end_point)
                pen = QPen(Qt.GlobalColor.red, 2, Qt.PenStyle.SolidLine)
                self.item = QGraphicsRectItem(rect)
                self.item.setPen(pen)
                self.item.setFlags(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable | QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable)
                self.scene().addItem(self.item)
            elif self.mode == "crop_circle":
                if self.item:
                    self.scene().removeItem(self.item)
                rect = QRectF(self.start_point, end_point)
                pen = QPen(Qt.GlobalColor.red, 2, Qt.PenStyle.SolidLine)
                self.item = QGraphicsEllipseItem(rect)
                self.item.setPen(pen)
                self.item.setFlags(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable | QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable)
                self.scene().addItem(self.item)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False
            if self.mode == "crop_rect" and self.item:
                rect = self.item.rect().toRect()
                cropped = self.pixmap_item.pixmap().copy(rect)
                self.scene().clear()
                self.setPixmap(cropped)
            elif self.mode == "crop_circle" and self.item:
                rect = self.item.rect().toRect()
                # Create a circular cropped image
                cropped = self.pixmap_item.pixmap().copy(rect)
                circular_cropped = QPixmap(cropped.size())
                circular_cropped.fill(Qt.GlobalColor.transparent)

                # Create a circular mask and apply it
                painter = QPainter(circular_cropped)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                path = QPainterPath()
                path.addEllipse(0, 0, rect.width(), rect.height())
                painter.setClipPath(path)
                painter.drawPixmap(0, 0, cropped)
                painter.end()

                self.scene().clear()
                self.setPixmap(circular_cropped)

    def enterEvent(self, event):
        self.setCursor(QCursor(Qt.CursorShape.CrossCursor))

    def leaveEvent(self, event):
        self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))


class ScreenCapture(QMainWindow):
    on_captured_finished = pyqtSignal(tuple, QPixmap)

    def __init__(self):
        super().__init__()

        # Set the window to be transparent and fullscreen with no frame
        self.setWindowOpacity(0.3)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        # self.setWindowState(Qt.WindowState.WindowFullScreen)
        self.setWindowState(Qt.WindowState.WindowMaximized)#mac下面不能使用fullscreen，这样会跳到另外一个桌面

        # Initialize the rubber band for selecting the region
        self.rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self)
        self.rubber_band.setStyleSheet("border: 10px solid red;")  # Set red border for the rubber band

        self.origin = None

    def paintEvent(self, event):
        # Create a painter to draw the red border for the entire window
        painter = QPainter(self)
        pen = QPen(QColor(255, 0, 0), 5)  # Red color, 2 pixels thick
        painter.setPen(pen)
        # Draw the border around the window
        painter.drawRect(self.rect())

    def mousePressEvent(self, event):
        # Set the origin point for the rubber band
        if event.button() == Qt.MouseButton.LeftButton:
            self.origin = event.pos()
            self.rubber_band.setGeometry(QRect(self.origin, QSize()))
            self.rubber_band.show()

    def mouseMoveEvent(self, event):
        # Update the rubber band geometry as the mouse moves
        if self.origin is not None:
            self.rubber_band.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        # Capture the selected region
        if event.button() == Qt.MouseButton.LeftButton:
            self.rubber_band.hide()
            selected_rect = self.rubber_band.geometry()

            # Capture the screen and crop to the selected region
            self.setWindowOpacity(0)
            screenshot = pyautogui.screenshot()

            cropped_image = screenshot.crop((selected_rect.left(), selected_rect.top(),
                                             selected_rect.right(), selected_rect.bottom()))
            # cropped_image.show()
            # cropped_image.save()

            # Convert to QPixmap using a QByteArray
            byte_array = io.BytesIO()
            cropped_image.save(byte_array, format='PNG')
            byte_array.seek(0)
            pixmap = QPixmap()
            pixmap.loadFromData(byte_array.read())

            cropped_image.save(os.getcwd() + '/cjrcaptureNew.png', 'png')
            # Close the window after capturing

            self.on_captured_finished.emit((selected_rect.left(), selected_rect.top(),
                                            selected_rect.right(), selected_rect.bottom()), pixmap)

            self.close()


class AnnotationDialog(QWidget):
    annotation_finished = pyqtSignal()  # 自定义信号，表示捕获完成

    def __init__(self):
        super().__init__()

        self.skill_id = ""
        self.storage = None
        self.crop_rect = ()
        self.setWindowTitle("操作标注")

        # 设置窗口带边框，但去掉最大化、最小化和关闭按钮
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Window | Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowMinMaxButtonsHint)

        # 设置对话框的布局
        layout = QVBoxLayout()

        # 创建工具栏并添加到布局中
        self.create_toolbar(layout)

        # 创建标签页
        self.tab_widget = QTabWidget()
        self.setLayout(layout)  # 设置布局

        # 操作模式下拉框
        form_layout = QFormLayout()
        self.mode_combobox = QComboBox()
        self.mode_combobox.addItem("输入内容", "set_value")
        self.mode_combobox.addItem("点击图像", "click_image")
        self.mode_combobox.addItem("其他操作", "other_action")
        self.mouseclick_combobox = QComboBox()
        self.mouseclick_combobox.addItem("单击", "1")
        self.mouseclick_combobox.addItem("双击", "2")
        self.otheraction_combobox = QComboBox()
        self.otheraction_combobox.addItem("新建文档", "1")
        self.otheraction_combobox.addItem("保存文档", "2")
        self.otheraction_combobox.addItem("截屏", "3")
        self.otheraction_combobox.addItem("选择上周日期", "4")
        self.otheraction_combobox.addItem("输入昨天日期", "5")

        # 创建水平布局来包含两个下拉框
        hbox = QHBoxLayout()
        hbox.addWidget(self.mode_combobox)
        hbox.addWidget(self.mouseclick_combobox)
        hbox.addWidget(self.otheraction_combobox)
        # 将水平布局添加到表单布局中
        form_layout.addRow("操作模式:", hbox)
        self.delay_lineEdit = QLineEdit()
        self.delay_lineEdit.setText(str(delay_time))  # 设置默认值为delay_time
        form_layout.addRow("延时(s):", self.delay_lineEdit)

        # 将模式下拉框添加到标签的第一个页面
        layout.addLayout(form_layout)
        self.mouseclick_combobox.hide()
        self.otheraction_combobox.hide()
        self.mode_combobox.currentIndexChanged.connect(self.on_mode_changed)

        # 创建内容编辑框并添加到第一个标签页
        self.content_textEdit = QTextEdit()
        self.content_textEdit.setPlaceholderText("说明：对输入的内容进行说明")
        palette = self.content_textEdit.palette()
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("gray"))  # 可以改为其他颜色
        self.content_textEdit.setPalette(palette)
        self.content_textEdit.setAcceptRichText(False)
        self.sample_textEdit = QTextEdit()
        self.sample_textEdit.setFixedHeight(60)
        self.sample_textEdit.setPlaceholderText("例子：提供一个例子")
        palette = self.sample_textEdit.palette()
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("gray"))  # 可以改为其他颜色
        self.sample_textEdit.setPalette(palette)
        self.sample_textEdit.setAcceptRichText(False)
        first_tab = QWidget()
        first_tab_layout = QVBoxLayout()
        first_tab_layout.addWidget(self.content_textEdit)
        first_tab_layout.addWidget(self.sample_textEdit)
        first_tab.setLayout(first_tab_layout)
        self.tab_widget.addTab(first_tab, "文字")

        # 创建图形视图并添加到第二个标签页
        self.graphics_view = CustomGraphicsView()
        self.graphics_scene = QGraphicsScene(self)
        self.graphics_view.setScene(self.graphics_scene)

        second_tab = QWidget()
        second_tab_layout = QVBoxLayout()
        second_tab_layout.addWidget(self.graphics_view)
        second_tab.setLayout(second_tab_layout)
        self.tab_widget.addTab(second_tab, "图形")

        # 将标签页添加到主布局
        layout.addWidget(self.tab_widget)

        # 确认和取消按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        # 设置快捷键 Ctrl+Enter 绑定到 "确定" 按钮的点击事件
        shortcut = QShortcut(QtGui.QKeySequence("Ctrl+Enter"), ok_button)
        shortcut.activated.connect(ok_button.click)

        layout.addLayout(button_layout)

        # 连接按钮事件
        ok_button.clicked.connect(self.save)
        cancel_button.clicked.connect(self.on_cancel)

    def on_mode_changed(self, index):
        # 检查当前选择的模式，并显示或隐藏mouseclick_combobox
        if self.mode_combobox.currentText() == "点击图像":
            self.mouseclick_combobox.show()
            self.otheraction_combobox.hide()
        elif self.mode_combobox.currentText() == "其他操作":
            self.mouseclick_combobox.hide()
            self.otheraction_combobox.show()
        else:
            self.otheraction_combobox.hide()
            self.mouseclick_combobox.hide()

    def create_toolbar(self, layout):
        """
        创建工具栏并添加图标操作
        """
        toolbar = QToolBar("工具选项")  # 创建工具栏
        toolbar.setMovable(True)  # 设置工具栏可移动
        toolbar.setFixedHeight(40)  # 设置工具栏固定高度
        toolbar.setStyleSheet("""
            QToolBar { 
                border: 1px solid gray; 
                background: #f0f0f0; 
                border-radius: 5px; 
            }
            QToolButton { 
                width: 25px; 
                height: 25px; 
                icon-size: 20px;  /* 设置图标大小 */
                padding: 4px; 
                margin: 2px; 
                border: none; 
                background: transparent; 
                border-radius: 3px; 
            } 
            QToolButton:hover { 
                background: #d9d9d9; 
                opacity: 0.8; 
            }
        """)  # 设置工具栏和按钮的样式

        # 创建操作并设置图标和工具提示
        fullscreen_action = QAction(QtGui.QIcon("images/fullscreen.png"), "全屏截取", self)
        fullscreen_action.setToolTip("全屏截取")  # 设置按钮的工具提示
        crop_action = QAction(QtGui.QIcon("images/crop.png"), "区域截取", self)
        crop_action.setToolTip("区域截取")  # 设置按钮的工具提示
        rect_action = QAction(QtGui.QIcon("images/rectangle.png"), "方形标注框", self)
        rect_action.setToolTip("方形标注框")  # 设置按钮的工具提示
        circle_action = QAction(QtGui.QIcon("images/circle.png"), "圆形标注框", self)
        circle_action.setToolTip("圆形标注框")  # 设置按钮的工具提示
        pen_action = QAction(QtGui.QIcon("images/pen.png"), "自由标注框", self)
        pen_action.setToolTip("自由标注框")  # 设置按钮的工具提示
        text_action = QAction(QtGui.QIcon("images/text.png"), "文本标注", self)
        text_action.setToolTip("文本标注")  # 设置按钮的工具提示

        # 将操作添加到工具栏
        toolbar.addAction(fullscreen_action)
        toolbar.addAction(crop_action)
        toolbar.addAction(rect_action)
        toolbar.addAction(circle_action)
        toolbar.addAction(pen_action)
        toolbar.addAction(text_action)

        # 连接操作的触发事件
        fullscreen_action.triggered.connect(self.capture_screenshot)
        crop_action.triggered.connect(self.capture_crop)
        rect_action.triggered.connect(lambda: self.print_tool("关闭"))

        # 将工具栏添加到布局的最上方
        layout.addWidget(toolbar)

    def print_tool(self, tool_name):
        """
        打印被点击工具的名称
        """
        print(f"选择了工具: {tool_name}")

    def capture_screenshot(self):
        # Capture the entire screen
        screenshot = pyautogui.screenshot()

        # Convert to QPixmap using a QByteArray
        byte_array = io.BytesIO()
        screenshot.save(byte_array, format='PNG')
        byte_array.seek(0)
        pixmap = QPixmap()
        pixmap.loadFromData(byte_array.read())

        # Show in the scene
        self.graphics_scene.clear()
        self.graphics_view.setPixmap(pixmap)

    def capture_crop(self):
        self.screen_capture_win = ScreenCapture()
        self.screen_capture_win.on_captured_finished.connect(self.handle_crop_capture)

        self.screen_capture_win.show()

    def handle_crop_capture(self, pos, pixmap):
        print(pos[0])
        print(pos[1])
        print(pos[2])
        print(pos[3])
        self.crop_rect = (pos[0], pos[1], pos[2], pos[3])
        self.graphics_scene.clear()
        self.graphics_view.setPixmap(pixmap)

    def get_data(self):
        return {
            'mode': self.mode_combobox.currentText(),
            'content': self.content_textEdit.toPlainText().strip(),
            'sample': self.sample_textEdit.toPlainText().strip()
        }

    def on_cancel(self):
        print("annotation canceled")
        self.content_textEdit.setPlainText("")
        self.sample_textEdit.setPlainText("")

        self.graphics_scene.clear()
        self.tab_widget.setCurrentIndex(0)
        self.annotation_finished.emit()  # 发射信号，通知窗口已关闭
        self.close()  # 关闭窗口时发射信号

    def click_by_image_detect(self, img, style: int = 1):
        time.sleep(1)
        try:
            image = pyautogui.locateOnScreen(img, grayscale=True, confidence=0.7)
            time.sleep(1)
            if image:  # 确保找到了图片
                center = pyautogui.center(image)
                if style == 1:
                    pyautogui.click(center)  # 单击
                elif style == 2:
                    pyautogui.doubleClick(center)  # 双击
            else:
                print("Image not found on the screen.")
        except pyautogui.ImageNotFoundException:
            # 如果图像未找到，执行这里的代码
            print("未能在屏幕上找到指定的图像。")

    def save_image(self):
        """Render the scene to a pixmap and save it as an image file."""

        if not self.graphics_scene.items():
            print("Graphics scene is empty. Not saving.")
            return ""

        skill_id = self.skill_id
        directory_path = os.path.join(os.getcwd(), 'skilllearning', 'data', skill_id, "images")
        os.makedirs(directory_path, exist_ok=True)
        img_name = generate_random_id() + ".png"
        file_path = os.path.join(directory_path, img_name)

        scene_rect = self.graphics_scene.sceneRect()
        image = QPixmap(scene_rect.size().toSize())
        image.fill(Qt.GlobalColor.white)

        painter = QPainter(image)
        self.graphics_scene.render(painter)
        painter.end()

        if file_path:
            image.save(file_path)
        return file_path

    def save(self):
        global storage, skill_name,sample
        storage = self.storage
        self.keyboard_controller = KeyboardController()
        self.mouse_controller = MouseController()

        mode = self.mode_combobox.currentData()
        content = self.content_textEdit.toPlainText()
        sample = self.sample_textEdit.toPlainText()
        image_path = self.save_image()
        last_action = storage[-1]
        print("last_action-->", last_action)
        mouse_click = self.mouseclick_combobox.currentData()
        other_action = self.otheraction_combobox.currentData()
        delay_time = self.delay_lineEdit.text()
        crop_rect = self.crop_rect
        if mode == "other_action":  # 其他操作
            mouse_click = ""
        elif mode == 'click_image':  # 点击图片
            other_action = ''
        else:
            mouse_click = ""
            other_action = ''

        json_object = {'action': 'annotated', 'mode': mode, 'content': content, 'sample': sample,
                       'image_path': image_path,
                       'mouse_click': mouse_click, 'other_action': other_action, 'crop_rect': crop_rect,
                       'delay_time': delay_time,
                       '_time': time.time()}
        print(f"'action': 'annotated', 'mode': {mode},'sample':{sample},'content': {content},'image_path': {image_path}, 'crop_rect':{crop_rect},'_time': {time.time()}")
        storage.append(json_object)
        self.content_textEdit.setPlainText("")
        self.sample_textEdit.setPlainText("")
        self.graphics_scene.clear()
        self.tab_widget.setCurrentIndex(0)
        self.setVisible(False)
        self.close()  # 关闭窗口时发射信号

        if mode == "set_value":
            # x = int(last_action["x"])
            # y = int(last_action["y"])
            # self.mouse_controller.position = (x, y)
            # time.sleep(0.1)
            # self.mouse_controller.press(Button.left)
            # time.sleep(0.1)
            # self.mouse_controller.release(Button.left)
            # time.sleep(0.3)
            # print("set_value-->", sample)
            self.sample =sample
            # pyautogui.hotkey('ctrl', 'a')  # 或者在macOS上使用 pyautogui.hotkey('command', 'a')
            # pyautogui.hotkey('command', 'a')
            # pyautogui.press('backspace')  # 或者使用 pyautogui.press('delete')
            # time.sleep(0.2)
            # self.keyboard_controller.type(sample)
            # time.sleep(1)

        elif mode == "click_image":
            self.click_by_image_detect(image_path, int(mouse_click))
            time.sleep(1)

        elif mode == 'other_action':
            if other_action == "1":  # 新建文档  1
                action_new_doc()
            elif other_action == "2":  # 保存文档  2
                action_save_doc(skill_name)
            elif other_action == "3":  # 截屏    3
                action_crop_doc(crop_rect[0], crop_rect[1], crop_rect[2] - crop_rect[0],
                                crop_rect[3] - crop_rect[1])
            elif other_action == "4":  # 上周日期  4
                action_click_last_weekday()
            elif other_action == "5":  # 昨天日期  4
                yestoday_text = get_yestoday_text()
                self.keyboard_controller.type(yestoday_text)
            time.sleep(1)
        self.annotation_finished.emit()  # 发射信号，通知窗口已关闭



class ConfigDialog(QDialog):
    annotation_finished = pyqtSignal()  # 自定义信号，表示捕获完成

    def __init__(self,title):
        super().__init__()

        self.skill_id = ""
        self.title = title
        self.instruction = ""
        self.desc = ""
        self.detail = ""

        self.setWindowTitle(lt("Setting","配置"))

        # 设置窗口带边框，但去掉最大化、最小化和关闭按钮
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Window | Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowMinMaxButtonsHint)

        # 设置对话框的布局
        layout = QVBoxLayout()
        self.setLayout(layout)  # 设置布局

        # 操作模式下拉框
        form_layout = QFormLayout()

        self.title_lineEdit = QLineEdit()
        self.title_lineEdit.setText(self.title)
        form_layout.addRow(lt("Title:","标题:"), self.title_lineEdit)

        self.instruction_lineEdit = QLineEdit()
        form_layout.addRow(lt("Instruction:","指令:"), self.instruction_lineEdit)

        self.desc_lineEdit = QLineEdit()
        form_layout.addRow(lt("Desc:","简介:"), self.desc_lineEdit)

        self.detail_textEdit = QTextEdit()
        palette = self.detail_textEdit.palette()
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("gray"))  # 可以改为其他颜色
        self.detail_textEdit.setPalette(palette)
        self.detail_textEdit.setAcceptRichText(False)

        form_layout.addRow(lt("Detail:","详细:"), self.detail_textEdit)
        layout.addLayout(form_layout)

        # 确认和取消按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton(lt("OK","确定"))
        cancel_button = QPushButton(lt("Cancel","取消"))
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        # 设置快捷键 Ctrl+Enter 绑定到 "确定" 按钮的点击事件
        shortcut = QShortcut(QtGui.QKeySequence("Ctrl+Enter"), ok_button)
        shortcut.activated.connect(ok_button.click)

        layout.addLayout(button_layout)

        # 连接按钮事件
        ok_button.clicked.connect(self.save)
        cancel_button.clicked.connect(self.on_cancel)


    def on_cancel(self):
        self.title_lineEdit.setText("")
        self.instruction_lineEdit.setText("")
        self.desc_lineEdit.setText("")
        self.detail_textEdit.setPlainText("")
        self.reject()  # 关闭窗口时发射信号

    def save(self):
        self.title = self.title_lineEdit.text()
        self.instruction = self.instruction_lineEdit.text()
        self.desc = self.desc_lineEdit.text()
        self.detail = self.detail_textEdit.toPlainText()

        self.title_lineEdit.setText("")
        self.instruction_lineEdit.setText("")
        self.desc_lineEdit.setText("")
        self.detail_textEdit.setPlainText("")
        self.accept()


# Circular countdown widget for visual countdown
class CircularCountdown(QWidget):
    # Signal to notify when countdown is finished
    countdown_finished = pyqtSignal()

    def __init__(self, count_down_number, end_text):
        super().__init__()

        # Set window as frameless and always on top
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Set window size
        self.resize(300, 300)

        # Countdown initial value
        self.countdown_from = count_down_number
        self.end_text = end_text

        # Timer for countdown
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000)  # Trigger every second

        # Show countdown widget
        self.show()

    def update_countdown(self):
        """Update countdown display"""
        if self.countdown_from > 0:
            self.countdown_from -= 1
            self.update()  # Trigger repaint
        else:
            # Countdown finished, close window
            self.timer.stop()
            self.close()
            self.countdown_finished.emit()  # Emit signal when window is closed

    def paintEvent(self, event):
        """Custom paint event for the countdown"""
        painter = QPainter(self)

        # Draw translucent circle background
        painter.setBrush(QBrush(QColor(0, 0, 0, 0)))
        painter.setPen(Qt.PenStyle.NoPen)

        # Draw a translucent black circle
        painter.setBrush(QBrush(QColor(0, 0, 0, 150)))  # Black color with alpha 150
        painter.drawEllipse(0, 0, self.width(), self.height())

        # Set font and draw text
        painter.setFont(QFont("Helvetica", 80))
        painter.setPen(QColor(255, 255, 255))

        if self.countdown_from > 0:
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, str(self.countdown_from))
        else:
            painter.setFont(QFont("Helvetica", 60))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.end_text)


# Main toolbar widget to control the application
class LearnOperationBar(Base):
    def __init__(self,application,learn_content):
        super(LearnOperationBar, self).__init__()
        self.skill_id_history_list = []
        self.skill_id = generate_random_id()
        self.title = learn_content
        self.instruction = ""
        self.desc = ""
        self.detail = ""
        self.pre_status = ""
        self.cur_status = "ready"
        self.to_status = ""
        self.auto_start_flag = True
        self.count_down_number = 3
        self.box = QVBoxLayout()
        self.tip_box = QHBoxLayout()
        self.btn_box = QHBoxLayout()
        self.tip_label = QLabel(self)
        self.timer_label = QLabel(self)
        self.annotation_btn = QPushButton()
        self.start_btn = QPushButton()
        self.end_btn = QPushButton()
        self.close_btn = QPushButton()
        self.dialog = None
        self.cfg_dialog = None
        self.application = application
        self.return_pos = False
        initialize_globals()
        # self.record_thread = application.keyboardmouse_thread
        self.record_thread = KeyboardMouseWorkerThread()
        # self.record_thread.storage_sent.connect(self.end_record_execute)

        self.bind()
        self.set_style()


    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def auto_start(self):
        if self.cfg_dialog is None:
            self.cfg_dialog = ConfigDialog(self.title)

        if self.cfg_dialog.exec() == QDialog.DialogCode.Accepted:
            self.title = self.cfg_dialog.title
            self.instruction = self.cfg_dialog.instruction
            self.desc = self.cfg_dialog.desc
            self.detail = self.cfg_dialog.detail
            print(self.title)

        if self.auto_start_flag:
            self.start_btn.click()

    def set_style(self):
        self.start_btn.setEnabled(True)
        self.start_btn.setToolTip("开始记录")
        self.end_btn.setEnabled(False)
        self.end_btn.setToolTip("结束并保存关闭")
        self.start_btn.setIcon(QIcon('images/startcircle.png'))
        self.end_btn.setIcon(QIcon('images/stop.png'))
        self.close_btn.setIcon(QIcon('images/closecircle.png'))
        self.close_btn.setToolTip("关闭")

        pixmap = QPixmap('images/arrowalldirect.png')
        icon_size = (22, 22)
        scaled_pixmap = pixmap.scaled(icon_size[0], icon_size[1], Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        self.tip_label.setPixmap(scaled_pixmap)
        self.annotation_btn.setEnabled(False)
        self.annotation_btn.setIcon(QIcon('images/annotation.png'))
        self.annotation_btn.setToolTip("对操作进行描述和说明，让AI大模型了解")
        self.tip_label.setToolTip("鼠标按此，移动工具条")
        self.btn_box.addWidget(self.tip_label)
        self.btn_box.addWidget(self.annotation_btn, 0)
        self.btn_box.addWidget(self.end_btn, 0)
        self.btn_box.addWidget(self.start_btn, 0)

        # Initialize timer variables
        self.seconds = 0
        self.is_running = False

        self.timer_label.setFont(QFont("Arial", 12))
        self.timer_label.setStyleSheet(
            "QLabel { background-color: pink; border-radius: 5px; padding-left:5px;padding-right:5px}")
        self.timer_label.setText("00:00:00")
        self.timer_label.setToolTip("记录时长")

        # Initialize timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)

        self.btn_box.addWidget(self.timer_label)

        self.btn_box.addWidget(self.close_btn, 0)

        self.box.addLayout(self.btn_box)
        self.box.setContentsMargins(5, 5, 5, 5)
        self.setWindowOpacity(0.7)
        self.frameGeometry()

        screen_geometry = QGuiApplication.primaryScreen().geometry()

        # Calculate initial position of the window at bottom right corner, width 300
        self.move(screen_geometry.width() - 300,
                  screen_geometry.height() - self.height())
        self.setLayout(self.box)

    def re_init(self):
        global storage, esc_count, last_esc_time
        self.stop_timer()
        self.seconds = 0
        self.timer_label.setText("00:00:00")

        self.cur_status = "ready"
        self.start_btn.setIcon(QIcon("images/startcircle.png"))
        self.start_btn.setToolTip("开始记录")
        self.annotation_btn.setEnabled(False)
        self.end_btn.setEnabled(False)
        self.start_btn.setEnabled(True)
        self.close_btn.setEnabled(True)

        self.skill_id_history_list.append(self.skill_id)
        self.skill_id = generate_random_id()
        self.title = ""
        self.instruction = ""
        self.desc = ""
        self.detail = ""
        storage = []
        esc_count = 0
        last_esc_time = 0

    def toggle_timer(self):
        """Toggle timer state (start/pause)"""
        if self.is_running:
            self.timer.stop()
        else:
            self.timer.start(1000)  # Update every second
        self.is_running = not self.is_running

    def start_timer(self):
        """Start the timer"""
        self.is_running = True
        self.timer.start(1000)

    def stop_timer(self):
        """Stop the timer"""
        self.is_running = False
        self.timer.stop()

    def update_time(self):
        """Update displayed time"""
        self.seconds += 1
        h = self.seconds // 3600
        m = (self.seconds % 3600) // 60
        s = self.seconds % 60
        self.timer_label.setText(f"{h:02}:{m:02}:{s:02}")

    def start_record(self):

        self.record_thread.set_screen_bar(self)
        self.record_thread.start_capturing()


    def on_countdown_finished(self):
        print("in countdown finished")
        global is_capturing,sample

        if self.return_pos:
            time.sleep(2)

            self.keyboard_controller = KeyboardController()
            self.mouse_controller = MouseController()

            last_action = storage[-2]

            x = int(last_action["x"])
            y = int(last_action["y"])
            self.mouse_controller.position = (x, y)
            time.sleep(0.1)
            self.mouse_controller.press(Button.left)
            time.sleep(0.1)
            self.mouse_controller.release(Button.left)
            time.sleep(0.3)
            print("set_value-->", "self.sample")
            # pyautogui.hotkey('ctrl', 'a')  # 或者在macOS上使用 pyautogui.hotkey('command', 'a')
            pyautogui.hotkey('command', 'a')
            pyautogui.press('backspace')  # 或者使用 pyautogui.press('delete')
            time.sleep(0.2)
            self.keyboard_controller.type(sample)
            time.sleep(1)
            self.return_pos = False
        if self.cur_status == "ready" and self.to_status == "started":
            self.record_thread.resume_capturing()
            self.cur_status = "started"
            self.start_record()
        elif self.cur_status == "paused" and self.to_status == "started":
            self.record_thread.resume_capturing()
            self.cur_status = "started"
        elif self.cur_status == "ended":
            self.end_record()


    def bind(self):
        global is_capturing

        def annotation_signal():
            global is_capturing
            mouse_position = mouse.Controller().position

            self.pre_status = self.cur_status
            if self.cur_status == "started":
                self.record_thread.pause_capturing()
                self.toggle_timer()
                self.to_status = "paused"
                self.cur_status = "paused"
                self.start_btn.setIcon(QIcon("images/startcircle.png"))
                self.start_btn.setToolTip("开始记录")

            self.annotation_btn.setEnabled(False)
            self.start_btn.setEnabled(False)
            self.end_btn.setEnabled(False)
            self.close_btn.setEnabled(False)
            self.show_dialog(-1, -1)

        def start_signal():
            global is_capturing
            self.toggle_timer()
            self.end_btn.setEnabled(True)
            self.annotation_btn.setEnabled(True)

            if self.cur_status == "ready":
                self.record_thread.show_dialog_signal.connect(self.annotation_btn.click)
                self.to_status = "started"
                self.start_btn.setIcon(QIcon("images/pause.png"))
                self.start_btn.setToolTip("暂停记录")
                self.countdown_window = CircularCountdown(self.count_down_number, lt("Start","开始"))
                self.countdown_window.countdown_finished.connect(self.on_countdown_finished)
                self.countdown_window.show()

            elif self.cur_status == "started":
                self.record_thread.pause_capturing()
                self.to_status = "paused"
                self.cur_status = "paused"
                self.start_btn.setIcon(QIcon("images/startcircle.png"))
                self.start_btn.setToolTip("开始记录")
                self.countdown_window = CircularCountdown(0, lt("Pause","暂停"))
                self.countdown_window.countdown_finished.connect(self.on_countdown_finished)
                self.countdown_window.show()

            elif self.cur_status == "paused":
                self.to_status = "started"
                self.start_btn.setIcon(QIcon("images/pause.png"))
                self.start_btn.setToolTip("暂停记录")
                self.countdown_window = CircularCountdown(self.count_down_number, lt("Resume","继续"))
                self.countdown_window.countdown_finished.connect(self.on_countdown_finished)
                self.countdown_window.show()

        def end_signal():
            global is_capturing
            self.record_thread.stop_capturing()
            self.cur_status = "ended"
            self.countdown_window = CircularCountdown(0, lt("End","结束"))
            self.countdown_window.countdown_finished.connect(self.on_countdown_finished)
            self.countdown_window.show()

        def close_signal():
            pre_is_capturing = self.record_thread.get_is_capturing()
            pre_time_is_running = self.is_running
            self.record_thread.stop_capturing()
            if pre_time_is_running:
                self.toggle_timer()

            if self.cur_status != "ready":
                reply = QMessageBox.question(self, '提醒',
                                             f"您已经开始录制，该操作将放弃保存。如需保存请改为点击结束按钮。是否继续?",
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)
                if reply == QMessageBox.StandardButton.No:
                    self.record_thread.set_is_capturing(pre_is_capturing)
                    if pre_time_is_running:
                        self.toggle_timer()
                    return

            self.record_thread.pause_capturing()
            self.cur_status = "ended"

            self.re_init()
            self.close()

        self.annotation_btn.clicked.connect(annotation_signal)
        self.start_btn.clicked.connect(start_signal)
        self.end_btn.clicked.connect(end_signal)
        self.close_btn.clicked.connect(close_signal)

    def end_record(self):
        global storage
        # self.record_thread.get_storage_to_end()
        skill_id = self.skill_id
        directory_path = os.path.join(os.getcwd(), 'skilllearning', 'data', skill_id)
        os.makedirs(directory_path, exist_ok=True)
        file_name = "steps.txt"
        file_path = os.path.join(directory_path, file_name)

        if len(storage) > 1:
            with open(file_path, 'w', encoding='utf-8') as outfile:
                json.dump(storage, outfile, indent=4, ensure_ascii=False)

        skill_id = self.skill_id
        title = self.title if self.title else "未命名"
        instruction =  self.instruction if self.instruction else ""
        desc = self.desc if self.desc else "未说明"
        detail = self.detail if self.detail else "未说明"
        requirement = ""
        parameter = ""
        skill_type = 0
        skill_event = ""
        creator = ""

        add_skill_mng(skill_id, title,instruction, file_path, requirement, parameter, desc, detail, skill_type, skill_event,
                      creator)

        self.re_init()
        self.close()


    def end_record_execute(self,storage):
        # storage = self.record_thread.get_storage()
        skill_id = self.skill_id
        directory_path = os.path.join(os.getcwd(), 'skilllearning', 'data', skill_id)
        os.makedirs(directory_path, exist_ok=True)
        file_name = "steps.txt"
        file_path = os.path.join(directory_path, file_name)

        if len(storage) > 1:
            with open(file_path, 'w', encoding='utf-8') as outfile:
                json.dump(storage, outfile, indent=4, ensure_ascii=False)


        skill_id = self.skill_id
        title = self.title if self.title else "未命名"
        instruction = self.instruction if self.instruction else ""
        desc = self.desc if self.desc else "未说明"
        detail = self.detail if self.detail else "未说明"
        requirement = ""
        parameter = ""
        skill_type = 0
        skill_event = ""
        creator = ""

        add_skill_mng(skill_id, title,instruction, file_path, requirement, parameter, desc, detail, skill_type, skill_event,
                      creator)

        self.re_init()
        self.close()


    # Show dialog
    def show_dialog(self, x, y):
        if self.dialog is None:
            self.dialog = AnnotationDialog()
            self.dialog.annotation_finished.connect(self.annotation_finished_handle)

        storage = self.record_thread.get_storage()

        self.dialog.skill_id = self.skill_id  # 更新skill_id
        self.dialog.storage = storage

        if x > 0 and y > 0:
            self.dialog.move(x, y)

        # Ensure the dialog is on top and gets focus
        self.dialog.show()
        self.dialog.raise_()
        self.dialog.activateWindow()

    def annotation_finished_handle(self):
        global storage, skill_name
        print("return in annotation_finished_handle")
        self.annotation_btn.setEnabled(True)
        self.end_btn.setEnabled(True)
        self.start_btn.setEnabled(True)
        self.close_btn.setEnabled(True)
        # self.dialog.set_value_click()
        self.record_thread.update_storage()
        self.return_pos = True



        if self.pre_status == "started":
            self.start_btn.click()

