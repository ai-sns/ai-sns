import subprocess
import sys
import time
import json
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtWidgets import QWidget
from pynput import keyboard, mouse
global storage

# Initialize global variables
def initialize_globals():
    global storage, is_capturing, esc_count, last_esc_time, record_all, name_of_recording, signal_emitter, keyboard_listener, mouse_listener, delay_time
    storage = []
    is_capturing = True
    esc_count = 0
    last_esc_time = 0
    record_all = "record-all"
    name_of_recording = "test008"
    delay_time = 3


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
        self.is_capturing = True
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
        if not self.is_capturing:
            return

        self.write_command(f"MOUSE_CLICK {x} {y} {button}")

        while True:
            # time.sleep(0.05)
            command = self.command
            # print("command:",command)

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
        # self.write_command("")

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
                self.command = command
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
                    # self.write_command("")




if __name__ == '__main__':
    initialize_globals()
    run_listener()
