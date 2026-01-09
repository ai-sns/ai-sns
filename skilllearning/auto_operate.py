import os
import io
import subprocess
import time
import json
import threading
from pynput import mouse, keyboard
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController

from PyQt6.QtWidgets import QGraphicsScene, QInputDialog, QGraphicsTextItem, QGraphicsRectItem, QGraphicsEllipseItem, \
    QGraphicsPathItem, QDialog
from PyQt6.QtGui import QCursor, QGuiApplication
from PyQt6.QtCore import Qt, QRectF, QThread

from PyQt6 import QtGui
from PyQt6.QtWidgets import  QToolBar, QGraphicsView, QTextEdit, QTabWidget, QFormLayout, QComboBox, \
    QGraphicsPixmapItem
from PyQt6 import QtCore
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtGui import QBrush, QShortcut,QIcon,  QAction,QFont, QPixmap, QPainterPath
from PyQt6.QtWidgets import QPushButton, QHBoxLayout, QLabel, QVBoxLayout, QMessageBox, QFileDialog, QWidget
import shutil
from db.DBFactory import query_skill_mng
# Import custom modules
from .base import Base
from .utils import *

import sys
import pyautogui
from PyQt6.QtWidgets import QApplication, QRubberBand, QMainWindow
from PyQt6.QtCore import Qt, QRect, QSize
from PyQt6.QtGui import QPainter, QPen, QColor

from .learn_operation import AnnotationDialog
sys.path.append("../..")
sys.path.append("../../..")
from i18n import lt

from PyQt6.QtCore import QTimer

# Initialize global variables
def initialize_globals():
    global storage, is_operating, esc_count, last_esc_time, record_all, name_of_recording, keyboard_listener, mouse_listener, number_of_plays, gstatus, gvalue,skill_name
    storage = []
    is_operating = True
    esc_count = 0
    last_esc_time = 0
    record_all = "record-all"
    name_of_recording = "test008"
    number_of_plays = 1
    gstatus = ""
    gvalue = ""
    skill_name=""


class KeyboardMouseWorkerThread(QWidget):
    # Signal to notify when the work is doneabcd
    finished = pyqtSignal(str)
    show_dialog_signal = pyqtSignal(int, int)
    storage_sent = pyqtSignal(list)
    wait_for_input_signal = pyqtSignal(str, str)


    def __init__(self):
        super().__init__()
        global storage
        self.process = subprocess.Popen([sys.executable, "autooperate.py"])


        self._running = False

        self.screen_bar = None

        self.receive_storage = False
        self.storage = []
        self.is_operating = False
        self.esc_count = 0
        self.last_esc_time = 0

        self.is_operating=True
        self.number_of_plays=1
        self.gstatus=""
        self.gvalue=""
        self.skill_name=""
        self.clear_command_both()

        # Set up a timer to periodically check for incoming messages
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_for_events)
        self.timer.start(100)  # Check every 100 ms

    def set_screen_bar(self, screen_bar):
        self.screen_bar = screen_bar

    def re_init(self):

        self.storage = []
        self.is_operating = False
        self.esc_count = 0
        self.last_esc_time = 0


    def start(self):
        self.write_command("START__system_seperate__"+self.screen_bar.skill_id)

    def set_gstatus(self,status):
        self.write_command("gstatus__system_seperate__" + status)


    def set_gvalue(self,v):
        self.write_command("gvalue__system_seperate__" + v)

    def terminate_process(self):
        """Terminate the subprocess if it's still running."""
        if self.process and self.process.poll() is None:  # Check if the process is still running
            self.process.terminate()  # Send a termination signal
            self.process.wait()  # Wait for the process to terminate
            print("Process terminated.")

    def stop(self):
        self.write_command("STOP__system_seperate__000")
        time.sleep(2)
        self.terminate_process()


    def stop_operating(self):
        # Stop the listener if it is running
        self.write_command("STOP__system_seperate__000")
        time.sleep(2)
        self.terminate_process()

    def pause_operating(self):
        # Pause the listener
        self.is_operating = False
        self.write_command("PAUSE__system_seperate__000")

    def resume_operating(self):
        # Resume the listener
        self.is_operating = True
        self.write_command("RESUME__system_seperate__000")

    def start_operating(self):
        # Resume the listener
        self.re_init()
        self.is_operating = True
        self.write_command("START__system_seperate__"+self.screen_bar.skill_id)

    def get_is_operating(self):
        return self.is_operating

    def set_is_operating(self, is_operating):
        self.is_operating = is_operating

    def get_storage_to_end(self):
        self.write_command("STORAGE__system_seperate__000")
        # storage=[]
        # time.sleep(0.1)
        # self.check_for_events()
        # if self.receive_storage:
        #     self.receive_storage =False
        #     storage= self.storage
        #
        # return storage

    def check_for_events(self):
        global storage
        command = self.read_command()
        self.clear_command()
        if command:
            if command.startswith("MOUSE_CLICK"):
                params = command.split()
                x, y, button = float(params[1]), float(params[2]), params[3]
                if not self.is_screen_bar_under_cursor():
                    self.write_command("RECORD__system_seperate__000")
                else:
                    self.write_command("IGNORE__system_seperate__000")
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

            elif command.startswith("WAIT_INPUT"):
                params = command.split("__system_seperate__")
                self.wait_for_input_signal.emit(params[1], params[2])
            elif command.startswith("END"):
                self.finished.emit("")


    def is_screen_bar_under_cursor(self):
        # Check if the mouse cursor is over the main window
        screen_bar = self.screen_bar
        if screen_bar:
            pos = screen_bar.mapFromGlobal(screen_bar.cursor().pos())
            return screen_bar.rect().contains(pos)
        else:
            return False

    def read_command(self):
        try:
            with open("command_to_main_process.txt", "r") as file:
                command = file.read().strip()
            return command
        except FileNotFoundError:
            return ""

    def write_command(self, command):
        with open("command_to_sub_process.txt", "w") as file:
            file.write(command)

    def clear_command(self):
        with open("command_to_main_process.txt", "w") as file:
            file.write("")

    def clear_command_both(self):
        with open("command_to_main_process.txt", "w") as file:
            file.write("")

        with open("command_to_sub_process.txt", "w") as file:
            file.write("")
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

# 圆形倒计时窗口类
class CircularCountdown(QWidget):
    # 定义一个信号，用于在窗口关闭时发射
    countdown_finished = pyqtSignal()

    def __init__(self, count_down_number, end_text):
        super().__init__()

        # 设置窗口无边框且形状为圆形，并置于最前
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 设置窗口大小
        self.resize(300, 300)

        # 设置倒计时初始值
        self.countdown_from = count_down_number
        self.end_text = end_text

        # 创建一个定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000)  # 每秒触发一次

        # 显示窗口
        self.show()

    def update_countdown(self):
        """更新倒计时显示"""
        if self.countdown_from > 0:
            self.countdown_from -= 1
            self.update()  # 触发重绘
        else:
            # 倒计时结束，关闭窗口
            self.timer.stop()
            self.close()  # 关闭窗口时发射信号
            self.countdown_finished.emit()  # 发射信号，通知窗口已关闭

    def paintEvent(self, event):
        """自定义绘制窗口"""
        painter = QPainter(self)

        # 设置画刷为半透明背景
        painter.setBrush(QBrush(QColor(0, 0, 0, 0)))
        painter.setPen(Qt.NoPen)

        # 绘制一个半透明黑色的圆形
        painter.setBrush(QBrush(QColor(0, 0, 0, 150)))  # 设置黑色且透明度为150
        painter.drawEllipse(0, 0, self.width(), self.height())

        # 设置字体并绘制文本
        painter.setFont(QFont("Helvetica", 80))
        painter.setPen(QColor(255, 255, 255))

        if self.countdown_from > 0:
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, str(self.countdown_from))
        else:
            painter.setFont(QFont("Helvetica", 60))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.end_text)

# 屏幕工具栏类
class AutoOperateBar(Base):
    wait_for_input_from_ai_signal = pyqtSignal(str, str)

    def __init__(self,application):
        super(AutoOperateBar, self).__init__()
        self.skill_id = ""
        self.pre_status = ""
        self.cur_status = "ready"
        self.to_status = ""
        self.auto_start_flag = True
        self.count_down_number = 1
        self.box = QVBoxLayout()
        self.tip_box = QHBoxLayout()
        self.btn_box = QHBoxLayout()
        self.tip_label = QLabel(self)
        self.timer_label = QLabel(self)
        self.annotation_btn = QPushButton()
        self.annotation_btn.setVisible(False)
        self.start_btn = QPushButton()
        self.end_btn = QPushButton()
        self.close_btn = QPushButton()

        self.application = application

        self.operate_thread = None
        # self.operate_thread.storage_sent.connect(self.end_record_execute)

        self.dialog = None

        self.bind()
        self.set_style()
        initialize_globals()

    def set_skill_id(self, skill_id):
        self.skill_id = skill_id

    def auto_start(self):
        if self.auto_start_flag == True:
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
        # self.tip_label.setIcon(QIcon('operationlearning/res/full.png'))
        pixmap = QPixmap('images/arrowalldirect.png')  # 请将 'path_to_your_icon.png' 替换为你的图标路径
        icon_size = (22, 22)  # 指定图标的宽和高
        scaled_pixmap = pixmap.scaled(icon_size[0], icon_size[1], Qt.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        self.tip_label.setPixmap(scaled_pixmap)
        self.annotation_btn.setEnabled(False)
        self.annotation_btn.setIcon(QIcon('images/annotation.png'))
        self.annotation_btn.setToolTip("对操作进行描述和说明，让AI大模型了解")
        self.tip_label.setToolTip("鼠标按此，移动工具条")
        self.btn_box.addWidget(self.tip_label)
        self.btn_box.addWidget(self.annotation_btn, 0)
        self.btn_box.addWidget(self.end_btn, 0)
        self.btn_box.addWidget(self.start_btn, 0)

        # 初始化计时变量
        self.seconds = 0
        self.is_running = False

        self.timer_label.setFont(QFont("Arial", 12))
        self.timer_label.setStyleSheet(
            "QLabel { background-color: pink; border-radius: 5px; padding-left:5px;padding-right:5px}")
        self.timer_label.setText("00:00:00")
        self.timer_label.setToolTip("记录时长")

        # 初始化计时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)

        self.btn_box.addWidget(self.timer_label)

        self.btn_box.addWidget(self.close_btn, 0)

        # self.box.addLayout(self.tip_box)
        self.box.addLayout(self.btn_box)
        self.box.setContentsMargins(5, 5, 5, 5)
        self.setWindowOpacity(0.7)
        self.frameGeometry()
        screen_geometry = QGuiApplication.primaryScreen().geometry()

        # 计算窗口的初始位置，使其位于屏幕右下角，宽度为300
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

        self.skill_id = ""
        storage = []
        esc_count = 0
        last_esc_time = 0

    def toggle_timer(self):
        """切换计时状态（开始/暂停）"""
        print("before togggle self.is_running:", self.is_running)
        if self.is_running:
            self.timer.stop()
        else:
            self.timer.start(1000)  # 每秒更新一次
        self.is_running = not self.is_running
        print("after togggle self.is_running:", self.is_running)

    def start_timer(self):
        """切换计时状态（开始/暂停）"""
        self.is_running = True
        self.timer.start(1000)

    def stop_timer(self):
        """切换计时状态（开始/暂停）"""
        self.is_running = False
        self.timer.stop()

    def update_time(self):
        """更新显示时间"""
        self.seconds += 1
        h = self.seconds // 3600
        m = (self.seconds % 3600) // 60
        s = self.seconds % 60
        self.timer_label.setText(f"{h:02}:{m:02}:{s:02}")

    def start_auto_operate(self):
        self.operate_thread.finished.connect(self.on_auto_operation_finished)
        self.operate_thread.set_screen_bar(self)
        self.operate_thread.start()

    def on_auto_operation_finished(self, result):
        print(result)
        self.end_btn.click()

    def on_countdown_finished(self):
        print("in countdown finished")
        global is_operating

        if self.cur_status == "ready" and self.to_status == "started":
            self.operate_thread.resume_operating()
            self.cur_status = "started"
            # go_record()
            self.start_auto_operate()
        elif self.cur_status == "paused" and self.to_status == "started":
            self.record_thread.resume_operating()
            self.cur_status = "started"
        elif self.cur_status == "ended":
            self.end_operate()
            self.re_init()
            self.close()

    def bind(self):
        global is_operating

        def annotation_signal():
            global is_operating
            mouse_position = mouse.Controller().position
            # Emit signal to show dialog in the main thread
            # signal_emitter.show_dialog_signal.emit(mouse_position[0], mouse_position[1])
            # self.show_dialog(mouse_position[0], mouse_position[1])
            # 设置按钮状态
            self.pre_status = self.cur_status
            if self.cur_status == "started":
                # self.start_btn.click()
                # time.sleep(1)
                is_operating = False
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

            global is_operating
            self.toggle_timer()
            self.end_btn.setEnabled(True)
            self.annotation_btn.setEnabled(True)
            if not self.operate_thread:
                self.operate_thread = KeyboardMouseWorkerThread()

            if self.cur_status == "ready":
                # Connect the signal to the slot function
                self.operate_thread.show_dialog_signal.connect(self.annotation_btn.click)
                self.operate_thread.wait_for_input_signal.connect(self.get_value_for_auto_operation)
                self.to_status = "started"
                self.start_btn.setIcon(QIcon("images/pause.png"))
                self.start_btn.setToolTip("暂停")
                # self.annotation_btn.setEnabled(False)
                self.countdown_window = CircularCountdown(self.count_down_number, lt("Start","开始"))
                self.countdown_window.countdown_finished.connect(self.on_countdown_finished)
                self.countdown_window.show()

            elif self.cur_status == "started":
                is_operating = False
                self.to_status = "paused"
                self.cur_status = "paused"
                self.start_btn.setIcon(QIcon("images/startcircle.png"))
                self.start_btn.setToolTip("开始记录")
                # self.annotation_btn.setEnabled(True)

                QMessageBox.information(self, '提醒', f'如果暂停时自动操作正在输入内容，请在恢复自动操作前为其补全输入的完整内容，包括回车确认等特殊按键。')

                self.countdown_window = CircularCountdown(0, lt("Pause","暂停"))
                self.countdown_window.countdown_finished.connect(self.on_countdown_finished)
                self.countdown_window.show()

            elif self.cur_status == "paused":
                self.to_status = "started"
                self.start_btn.setIcon(QIcon("images/pause.png"))
                self.start_btn.setToolTip("暂停记录")

                # self.annotation_btn.setEnabled(False)
                self.countdown_window = CircularCountdown(self.count_down_number, lt("Resume","继续"))
                self.countdown_window.countdown_finished.connect(self.on_countdown_finished)
                self.countdown_window.show()

        def end_signal():
            global is_operating
            is_operating = False
            self.cur_status = "ended"
            self.countdown_window = CircularCountdown(0, lt("End","结束"))
            self.countdown_window.countdown_finished.connect(self.on_countdown_finished)
            self.countdown_window.show()

        def close_signal():
            global is_operating
            pre_is_operating = is_operating
            pre_time_is_running = self.is_running
            is_operating = False
            if pre_time_is_running:
                self.toggle_timer()

            if self.cur_status != "ready":

                reply = QMessageBox.question(self, '提醒',
                                             f"您已经开始自动操作，该操作将放弃所有运行数据结果。如需数据结果请改为点击结束按钮。是否继续?",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if reply == QMessageBox.No:
                    is_operating = pre_is_operating
                    if pre_time_is_running:
                        self.toggle_timer()
                    return

            is_operating = False
            self.cur_status = "ended"
            if self.operate_thread is not None:
                self.operate_thread.stop()
                # time.sleep(1)
                self.operate_thread.quit()
                # time.sleep(1)
                # record_thread.terminate()
                self.operate_thread.wait()
                # time.sleep(1)
                self.operate_thread = None

            self.re_init()
            self.close()

        self.annotation_btn.clicked.connect(annotation_signal)
        self.start_btn.clicked.connect(start_signal)
        self.end_btn.clicked.connect(end_signal)
        self.close_btn.clicked.connect(close_signal)

    def end_operate(self):
        if self.operate_thread is not None:
            self.operate_thread.stop()

            self.operate_thread = None

    # Show dialog
    def show_dialog(self, x, y):
        if self.dialog is None:
            self.dialog = AnnotationDialog(self.skill_id)
            self.dialog.annotation_finished.connect(self.annotation_finished_handle)
        if x > 0 and y > 0:
            self.dialog.move(x, y)

        # 确保对话框在最上层并获得焦点
        self.dialog.show()
        self.dialog.raise_()  # 将对话框置于最上层
        self.dialog.activateWindow()  # 激活对话框窗口

    def annotation_finished_handle(self):
        print("return in annotation_finished_handle")
        self.annotation_btn.setEnabled(True)
        self.end_btn.setEnabled(True)
        self.start_btn.setEnabled(True)
        self.close_btn.setEnabled(True)

        if self.pre_status == "started":
            self.start_btn.click()

    def capture_finished_handle(self):
        self.annotation_btn.setEnabled(True)
        self.start_btn.setEnabled(True)
        self.start_btn.setIcon(QIcon("images/pause.png"))
        self.start_btn.setToolTip("暂停记录")
        self.toggle_timer()
        self.end_btn.setEnabled(True)
        self.countdown_window = CircularCountdown()
        self.countdown_window.show()

    def get_value_for_auto_operation(self, question, img_path):
        print("get get_value_for_auto_operation signal")
        self.wait_for_input_from_ai_signal.emit(question, img_path)

    def feed_bak_from_ai(self, value):
        global gstatus, gvalue
        gstatus = ""
        gvalue = value

        self.operate_thread.set_gvalue(value)
        # self.operate_thread.set_gstatus("")

