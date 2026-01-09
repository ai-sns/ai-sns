import subprocess
import sys
import time
import json
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtWidgets import QWidget
from pynput import keyboard, mouse
import os
import io
import subprocess
import time
import json
import threading
from pynput import mouse, keyboard
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController
from skilllearning.utils import *
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


import sys
import pyautogui
from PyQt6.QtWidgets import QApplication, QRubberBand, QMainWindow
from PyQt6.QtCore import Qt, QRect, QSize
from PyQt6.QtGui import QPainter, QPen, QColor


from i18n import lt

from PyQt6.QtCore import QTimer

class AutoKeyboardMouse:
    def __init__(self):
        self.log_file_path = "input_log.txt"

        self.storage_file_path = "storage.txt"
        self.expect_response = False
        self.command= ""
        self.storage = []
        self.gstatus=""
        self.gvalue =""

        self.is_operating = False


        self.running = True

    def read_command(self):
        try:
            with open("command_to_sub_process.txt", "r") as file:
                command = file.read().strip()

            if command=="":
                command="None__system_seperate__None"
            return command
        except FileNotFoundError:
            return ""

    def write_command(self, command):
        with open("command_to_main_process.txt", "w") as file:
            file.write(command)

    def clear_command(self):
        with open("command_to_sub_process.txt", "w") as file:
            file.write("")

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

    def click_by_image_detect(self, img, style: int = 1):
        # time.sleep(1)
        image = pyautogui.locateOnScreen(img, grayscale=True, confidence=0.7)
        time.sleep(0.2)
        if image:  # 确保找到了图片
            center = pyautogui.center(image)
            if style == 1:
                pyautogui.click(center)  # 单击
            elif style == 2:
                pyautogui.doubleClick(center)  # 双击
        else:
            print("Image not found on the screen.")

    def auto_operate(self,skill_id):
        global is_operating, number_of_plays, gstatus, gvalue,skill_name

        # skill_id = self.operate_bar.skill_id
        skill_mng = query_skill_mng(skill_id = skill_id)
        if skill_mng:
            skill_name = skill_mng.name
            print(skill_name)
        directory_path = os.path.join(os.getcwd(), 'skilllearning', 'data', skill_id)
        file_name = "steps.txt"
        file_path = os.path.join(directory_path, file_name)

        with open(file_path, encoding='utf-8') as json_file:
            data = json.load(json_file)
        special_keys = {"Key.shift": Key.shift, "Key.tab": Key.tab, "Key.caps_lock": Key.caps_lock,
                        "Key.ctrl": Key.ctrl, "Key.alt": Key.alt, "Key.cmd": Key.cmd, "Key.cmd_r": Key.cmd_r,
                        "Key.alt_r": Key.alt_r, "Key.ctrl_r": Key.ctrl_r, "Key.shift_r": Key.shift_r,
                        "Key.enter": Key.enter, "Key.backspace": Key.backspace, "Key.f19": Key.f19, "Key.f18": Key.f18,
                        "Key.f17": Key.f17, "Key.f16": Key.f16, "Key.f15": Key.f15, "Key.f14": Key.f14,
                        "Key.f13": Key.f13, "Key.media_volume_up": Key.media_volume_up,
                        "Key.media_volume_down": Key.media_volume_down, "Key.media_volume_mute": Key.media_volume_mute,
                        "Key.media_play_pause": Key.media_play_pause, "Key.f6": Key.f6, "Key.f5": Key.f5,
                        "Key.right": Key.right, "Key.down": Key.down, "Key.left": Key.left, "Key.up": Key.up,
                        "Key.page_up": Key.page_up, "Key.page_down": Key.page_down, "Key.home": Key.home,
                        "Key.end": Key.end, "Key.delete": Key.delete,
                        "Key.space": Key.space, "Key.esc": Key.esc, "Key.ctrl_l": Key.ctrl_l}

        mouse = MouseController()
        keyboard = KeyboardController()
        number_of_plays = 1
        self.is_operating = True

        for loop in range(number_of_plays):
            # 检查是否正在操作
            if not self.is_operating:
                print("操作已暂停")
                while not self.is_operating:  # 如果暂停，等待恢复
                    self.update_state()
                    # 在等待期间检查运行状态
                    if not self.running:
                        print("运行状态为False，退出循环")
                        break  # 退出循环
                    time.sleep(0.5)
                print("操作恢复")

            # 检查运行状态
            if not self.running:
                print("运行状态为False，退出循环")
                break  # 退出循环

            for index, obj in enumerate(data):
                # 检查运行状态
                self.update_state()
                if not self.running:
                    print("运行状态为False，退出循环")
                    break  # 退出循环

                action, _time = obj['action'], obj['_time']
                # # 检查下一个动作，如果存在
                # if index < len(data) - 1:
                #     next_action = data[index + 1]['action']
                # else:
                #     next_action = None  # 没有下一个动作

                # 检查是否暂停
                if not self.is_operating:
                    print("检测暂停状态")
                    # 只有下一个动作是scroll、pressed或released才暂停
                    if action in ["scroll", "pressed", "released"]:
                        print("暂停，等待操作恢复")
                        while not self.is_operating:
                            self.update_state()
                            if not self.running:
                                print("运行状态为False，退出循环")
                                return  # 退出整个方法
                            time.sleep(0.5)
                        print("操作恢复")
                    else:
                        print(f"将要执行的动作为 {action}，继续执行")

                action, _time = obj['action'], obj['_time']
                try:
                    next_movement = data[index + 1]['_time']
                    next_action = data[index +1]['action']
                    if next_action == "annotated":
                        pause_time = 1
                    else:
                        pause_time = next_movement - _time
                except IndexError as e:
                    pause_time = 1

                print("data action:", action)

                if action == "pressed_key" or action == "released_key":
                    if obj['key'] is None:
                        continue
                    key = obj['key'] if 'Key.' not in obj['key'] else special_keys[obj['key']]
                    print("action: {0}, time: {1}, key: {2}".format(action, _time, str(key)))
                    if action == "pressed_key":
                        if key == "\u0001":
                            keyboard.press('a')
                        else:
                            keyboard.press(key)
                    else:
                        if key=="\u0001":
                            keyboard.release('a')
                            time.sleep(0.1)  # 稍微等待一下，确保按键被正确识别
                        else:
                            keyboard.release(key)



                    # 按录制时间播放，不截取
                    # if pause_time>1:
                    #     time.sleep(1)
                    # else:
                    #     time.sleep(pause_time)
                    time.sleep(pause_time)  # --> 使用学习时间

                elif action == "annotated":
                    print("annotated")
                    mode = obj['mode']
                    content = obj['content']
                    sample = obj['sample']
                    image_path = obj['image_path']
                    # delay_time = obj['delay_time']
                    delay_time =0
                    # other_action = obj['other_action']
                    other_action = ""
                    if mode == "set_value":
                        self.gstatus = "waiting_for_input_value"

                        print("set_value")
                        pyautogui.click()  # 鼠标当前位置点击一下
                        # pyautogui.hotkey('ctrl', 'a')  # 或者在macOS上使用 pyautogui.hotkey('command', 'a')                        pyautogui.press('backspace')  # 或者使用 pyautogui.press('delete')
                        time.sleep(0.2)
                        if sample.strip() != '' and content.strip() == sample.strip():  # content 和 sample 值相同
                            keyboard.type(sample)
                            self.gvalue = ""
                            self.gstatus=""

                        else:

                            self.write_command(f"WAIT_INPUT__system_seperate__{content}__system_seperate__{image_path}__system_seperate__None")
                            while self.gstatus == "waiting_for_input_value":
                                self.update_state()
                                time.sleep(0.5)
                                if self.gvalue!= "":
                                    keyboard.type(self.gvalue)
                                    self.gvalue = ""
                                    self.gstatus = ""

                    elif mode == "click_image":
                        mouse_click = obj['mouse_click']
                        self.click_by_image_detect(image_path, int(mouse_click))

                    elif mode == 'other_action':
                        if other_action == "1":  # 新建文档  1
                            action_new_doc()
                        elif other_action == "2":  # 保存文档  2
                            action_save_doc(skill_name)
                        elif other_action == "3":  # 截屏    3
                            crop_rect = obj['crop_rect']
                            action_crop_doc(crop_rect[0], crop_rect[1], crop_rect[2] - crop_rect[0],
                                            crop_rect[3] - crop_rect[1])
                        elif other_action == "4":  # 上周日期  4
                            action_click_last_weekday()
                        elif other_action == "5":  # 昨天日期  5
                            yestoday_text = get_yestoday_text()
                            # self.keyboard_controller.type(yestoday_text)
                            keyboard.type(yestoday_text)
                            time.sleep(0.2)
                            # keyboard.type(yestoday_text)
                    time.sleep(float(delay_time))
                    # if pause_time > 1:
                    #     time.sleep(1)
                    # else:
                    #     time.sleep(pause_time)
                    time.sleep(pause_time)  # --> 使用学习时间

                else:
                    move_for_scroll = True
                    x, y = obj['x'], obj['y']
                    if action == "scroll" and index > 0 and (
                            data[index - 1]['action'] == "pressed" or data[index - 1]['action'] == "released"):
                        if x == data[index - 1]['x'] and y == data[index - 1]['y']:
                            move_for_scroll = False
                    # print("x: {0}, y: {1}, action: {2}, time: {3}".format(x, y, action, _time))
                    mouse.position = (x, y)
                    if action == "pressed" or action == "released" or action == "scroll" and move_for_scroll == True:
                        time.sleep(0.1)
                    if action == "pressed":
                        mouse.press(Button.left if obj['button'] == "Button.left" else Button.right)
                    elif action == "released":
                        mouse.release(Button.left if obj['button'] == "Button.left" else Button.right)
                    elif action == "scroll":
                        horizontal_direction, vertical_direction = obj['horizontal_direction'], obj[
                            'vertical_direction']
                        mouse.scroll(horizontal_direction, vertical_direction)

                    # if pause_time > 1:
                    #     time.sleep(1)
                    # else:
                    #     time.sleep(pause_time)
                    time.sleep(pause_time)  # --> 使用学习时间

        self.write_command(f"END__system_seperate__0__system_seperate__0__system_seperate__0")
        self.running = False


    def update_state(self):
        # return
        command_to_subprocess = self.read_command()
        if command_to_subprocess:
            command, param_1 = command_to_subprocess.split("__system_seperate__")
            self.clear_command()

        try:
            # self.command = command
            # if command == "START":
            #     self.auto_operate(param_1)
            #     self.clear_command()
            # elif command == "STOP":
            #     self.is_operating = False
            #     self.clear_command()
            #     print("stop the auto_operate")
            # elif command == "PAUSE":
            #     self.is_operating = False
            #     self.clear_command()
            # elif command == "RESUME":
            #     self.is_operating = True
            #     self.clear_command()
            # elif command == "STORAGE":
            #     self.send_storage()
            #     self.clear_command()
            if command == "gvalue":
                self.gvalue = param_1
                self.clear_command()
            # elif command == "gstatus":
            #     self.gstatus = param_1
            #     self.clear_command()
            # elif command == "EXIT":
            #     self.clear_command()
        except EOFError:
            print("Error: Control pipe closed unexpectedly.")


    def start(self):
        """Starts the input listeners."""
        # command, param_1 = self.read_command().split("__system_seperate__")
        # self.clear_command()
        # self.auto_operate(param_1)
        # return
        # with open(self.log_file_path, "a") as self.log_file:
        while True:
            time.sleep(0.1)
            command_to_subprocess = self.read_command()
            if command_to_subprocess:
                command, param_1  = command_to_subprocess.split("__system_seperate__")
                self.clear_command()
                try:

                        self.command = command
                        if command == "START":
                            self.auto_operate(param_1)
                            break
                        elif command == "STOP":
                            self.is_operating = False
                            print("stop the auto_operate")
                        elif command == "PAUSE":
                            self.is_operating = False
                        elif command == "RESUME":
                            self.is_operating = True
                        elif command == "STORAGE":
                            self.send_storage()
                        elif command == "gvalue":
                            self.gvalue = param_1
                        elif command == "gstatus":
                            self.gstatus = param_1
                        elif command == "EXIT":
                            break
                except EOFError:
                    print("Error: Control pipe closed unexpectedly.")
                    break

if __name__ == '__main__':
    try:
        auto_keyboard_mouse = AutoKeyboardMouse()
        auto_keyboard_mouse.start()
    except Exception as e:
        print(f"Error in AutoKeyboardMouse: {e}")
