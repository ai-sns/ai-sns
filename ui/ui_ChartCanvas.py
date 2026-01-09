import sys
import numpy as np

sys.path.append("..")
sys.path.append("../..")

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from PyQt6.QtGui import QCursor
from PyQt6.QtCore import Qt

import platform

# 根据操作系统选择合适的字体
if platform.system() == 'Darwin':  # macOS
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
else:
    plt.rcParams['font.sans-serif'] = ['SimHei']

plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


class RadarChartCanvas(FigureCanvas):
    def __init__(self, data, categories, *args, **kwargs):
        self.figure = Figure(figsize=(2, 2), facecolor='#E1E1E1')
        super().__init__(self.figure)
        self.setFixedSize(125, 100)
        self.setToolTip("请点击")
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        # 初始化数据
        self.data = data
        self.categories = categories

        # 初始化图表
        self.plot_radar_chart()

    def plot_radar_chart(self):
        """更新雷达图数据，先清除旧图表再重新绘制"""
        self.figure.clear()  # 清除旧图表
        ax = self.figure.add_subplot(111, polar=True)
        ax.set_facecolor('#E1E1E1')
        for spine in ax.spines.values():
            spine.set_edgecolor('#ff9d9d')

        ax.tick_params(axis='both', colors='#727272')

        num_vars = len(self.categories)
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

        # 复制数据以闭合雷达图
        data = self.data + self.data[:1]
        angles += angles[:1]

        ax.plot(angles, data, linewidth=1, linestyle='solid')
        ax.fill(angles, data, 'b', alpha=0.1)

        ax.set_yticklabels([])
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(self.categories,fontsize=8)

        # self.figure.subplots_adjust(left=0.25, right=0.90, top=0.75, bottom=0.25)
        self.figure.tight_layout()
        self.figure.subplots_adjust(left=0.2, right=0.8, top=0.75, bottom=0.25)
        self.figure.canvas.draw_idle()  # 刷新画布


    def mousePressEvent(self, event):
        print("hello")


class BarChartCanvas(FigureCanvas):
    def __init__(self, indicators, values, colors, *args, **kwargs):
        # self.figure = Figure(facecolor='#E1E1E1')
        self.figure = Figure(figsize=(2, 2), facecolor='#E1E1E1')
        super().__init__(self.figure)
        self.setFixedSize(125, 100)
        self.setToolTip("请点击")
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        # 初始化数据
        self.indicators = indicators
        self.values = values
        self.colors = colors

        # 初始化图表
        self.plot_bar_chart()

    def plot_bar_chart(self):
        """更新柱状图数据，先清除旧图表再重新绘制"""
        self.figure.clear()  # 清除旧图表
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('#E1E1E1')

        for spine_name, spine in ax.spines.items():
            if spine_name in ['left', 'bottom']:
                spine.set_edgecolor('#727272')
            else:
                spine.set_visible(False)

        ax.tick_params(axis='both', colors='#727272')
        ax.tick_params(axis='x', labelsize=8)  # 设置 x 轴刻度字体大小

        y_pos = np.arange(len(self.indicators))
        bars = ax.barh(y_pos, self.values, color=self.colors, align='center')

        for bar, indicator in zip(bars, self.indicators):
            ax.text(bar.get_width() / 2, bar.get_y() + bar.get_height() / 2, indicator,
                    va='center', ha='center', color='#727272', fontsize=8)

        ax.set_yticks([])
        self.figure.tight_layout()
        self.figure.subplots_adjust(left=0.05, right=0.95, top=1, bottom=0.2)
        self.figure.canvas.draw_idle()  # 刷新画布

    def mousePressEvent(self, event):
        print("hello")
