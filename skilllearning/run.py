# _*_ coding:utf-8 _*_
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from app import ScreenBar

__author__ = 'atsushinee@outlook.com'


if __name__ == '__main__':

    app = QApplication(sys.argv)
    bar = ScreenBar()
    bar.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
    bar.show()
    sys.exit(app.exec())
