import os

from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtCore import pyqtSignal, QObject, QUrl, pyqtProperty
from util import format_string_for_run_javascript
from PyQt6.QtWebChannel import QWebChannel
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QMessageBox
import time
from typing import Any

import re

def remove_ansi_sequences(text):
    # 定义正则表达式模式，匹配 \033[ 开头，m 结尾的部分
    ansi_escape_pattern = re.compile(r'\033\[.*?m')
    # 使用 sub 函数替换匹配的部分为空字符串
    cleaned_text = ansi_escape_pattern.sub('', text)
    return cleaned_text

class Speaker(QObject):
    on_message_ask_for_feedback = pyqtSignal(str)
    on_message_show_group_select_agent_title = pyqtSignal(str)


    def __init__(self, message_handler,web_browser):
        super(Speaker, self).__init__()
        self.message_handler=message_handler
        self.web_browser=web_browser
        self.stop_speaker = False
        self.answer_cache = ""
        self.memo = ""
        self.status = ""
        self.human_feedback = ""
        self.latest_human_feedback = ""

    def speak(self, *objects: Any, sep: str = " ", end: str = "\n", flush: bool = False):
        # web_browser = self.web_browser
        message = sep.join(objects)
        message = remove_ansi_sequences(message)

        if message.startswith("Agent Manager select the next agent:"):
            self.memo = message
            message = ""

        if message == "\n>>>>>>>> NO HUMAN INPUT RECEIVED.":
            print(message)
            message = ""

        if message == "\n>>>>>>>> USING AUTO REPLY...":
            print(message)
            message = ""

        if "to Group_Head" in message:
            print("Musk is selected")

        if message!="":
            message += end
            self.message_handler.pass_message(message)
            self.runJavaScript("window.scrollTo(0, document.body.scrollHeight);")
            # if "它" in message or "她"  in message or "他" in message or "Python" in message:
            #     print("start raising")
            #     raise Exception("它，她，他,Python ")
            #     print("end raising")
            self.answer_cache += message
            print("self.answer_cache",self.answer_cache)
            if self.stop_speaker:
                # self.answer_cache = ""
                self.stop_speaker = False
                raise Exception("用户中断")

    def input(self, prompt: str = "", *, password: bool = False) -> str:
        print("cjr in io:" , prompt)
        
        answer_cache=self.answer_cache
        self.answer_cache=""
        self.on_message_ask_for_feedback.emit(answer_cache)
        self.status = "wait_for_feedback"
        self.commit_and_refresh()
        while True:
            human_feedback = self.human_feedback
            if human_feedback != "":
                self.latest_human_feedback = human_feedback
                if human_feedback == "ok":
                    human_feedback = ""
                if human_feedback == "👨‍💻✔️":
                    human_feedback = ""
                if human_feedback == "🆗":
                    human_feedback = ""
                if human_feedback == "➡️✔️":
                    human_feedback = "exit"
                if human_feedback == "🏁✔️":
                    human_feedback = "exit"


                break
            time.sleep(0.1)#需要sleep，否则界面会被卡死
        self.human_feedback = ""
        self.status = ""
        return human_feedback

    def runJavaScript(self,script_content):
        self.message_handler.runJavaScript(script_content)

    def show_group_select_agent_title(self):
        self.on_message_show_group_select_agent_title.emit(self.answer_cache)
        self.commit_and_refresh()

    def commit_and_refresh(self):
        # web_browser = self.web_browser
        # web_browser.page().runJavaScript('updatemaincontent()')
        self.speak("__end_speak__", sep="", end="")
        self.answer_cache = ""

class Speaker_Log(QObject):
    on_message_ask_for_feedback = pyqtSignal(str)

    def __init__(self):
        super(Speaker_Log, self).__init__()
        self.stop_speaker = False
        self.answer_cache = ""
        self.status = ""
        self.human_feedback = ""

    def speak(self, *objects: Any, sep: str = " ", end: str = "\n", flush: bool = False):
        message = sep.join(objects)
        message = remove_ansi_sequences(message)
        if message!="":
            message += end
            self.answer_cache += message
            if self.stop_speaker:
                self.stop_speaker = False
                raise Exception("用户中断")

    def input(self, prompt: str = "", *, password: bool = False) -> str:
        print("cjr in io:" , prompt)
        self.speak(prompt, sep="", end="")
        answer_cache=self.answer_cache
        self.answer_cache=""
        self.on_message_ask_for_feedback.emit(answer_cache)
        self.status = "wait_for_feedback"
        self.commit_and_refresh()
        while True:
            human_feedback = self.human_feedback
            if human_feedback != "":
                self.latest_human_feedback = human_feedback
                if human_feedback == "ok":
                    human_feedback = ""
                break
            time.sleep(0.1)#需要sleep，否则界面会被卡死
        self.human_feedback = ""
        self.status = ""
        return human_feedback

    def commit_and_refresh(self):

        self.speak("__end_speak__", sep="", end="")
        self.answer_cache = ""
