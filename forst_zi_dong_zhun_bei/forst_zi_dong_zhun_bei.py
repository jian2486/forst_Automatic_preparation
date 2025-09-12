import os
import random
import time
import sys

import cv2
# 检查CUDA支持
try:
    cuda_enabled = cv2.cuda.getCudaEnabledDeviceCount() > 0
except:
    cuda_enabled = False

if cuda_enabled:
    print("检测到CUDA支持，将使用GPU加速图像处理")
else:
    print("未检测到CUDA支持，将使用CPU进行图像处理")

import numpy as np
import pyautogui
import win32api
import win32con
import win32gui

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel, QMessageBox, QHBoxLayout  # 添加QHBoxLayout导入
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QIcon, QKeySequence


# 日志更新信号类
class LogSignal(QThread):
    log_updated = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.logs = []
    
    def output_log(self, message):
        self.log_updated.emit(message)
        # 同时输出到控制台
        print(message)

# 主窗口类
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.log_signal = LogSignal()
        self.init_ui()
        self.setup_logger()

    def init_ui(self):
        self.setWindowTitle('自动点击程序')
        self.setGeometry(100, 100, 500, 300)  # 缩小窗口高度

        layout = QVBoxLayout()

        # 日志显示区域（扩大）
        log_layout = QVBoxLayout()
        log_label = QLabel('日志')
        log_layout.addWidget(log_label)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(200)  # 增加高度
        log_layout.addWidget(self.log_text)
        layout.addLayout(log_layout)

        # 运行间隔输入框
        interval_layout = QHBoxLayout()  # 使用QHBoxLayout
        interval_label = QLabel('运行间隔')
        self.interval_input = QLineEdit()  # 使用QLineEdit代替QTextEdit
        self.interval_input.setMaximumWidth(50)
        self.interval_input.setText("5")  # 默认值为5秒
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.interval_input)
        
        # GPU加速开关按钮
        self.gpu_button = QPushButton('GUP加速 开')  # 修改按钮文本
        self.gpu_button.clicked.connect(self.toggle_gpu_acceleration)
        interval_layout.addWidget(self.gpu_button)
        
        # 时钟图标
        clock_icon = QLabel()
        clock_icon.setPixmap(QPixmap("clock_icon.png").scaled(20, 20))
        interval_layout.addWidget(clock_icon)
        
        # 添加叹号图标作为信息提示
        info_icon = QLabel()
        info_icon.setPixmap(QPixmap("info_icon.png").scaled(16, 16))  # 假设info_icon.png存在
        info_icon.setToolTip("此程序由哔哩哔哩up简朴无谓制作")
        interval_layout.addWidget(info_icon)
        
        layout.addLayout(interval_layout)

        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 开始挂机按钮
        self.start_button = QPushButton('开始挂机')
        self.start_button.clicked.connect(self.start_clicker)
        button_layout.addWidget(self.start_button)
        
        # 暂停按钮
        self.pause_button = QPushButton('暂停')
        self.pause_button.clicked.connect(self.toggle_pause)
        button_layout.addWidget(self.pause_button)
        
        # 退出按钮
        self.close_button = QPushButton('退出')
        self.close_button.clicked.connect(self.stop_program)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # 添加状态变量
        self.is_paused = False

        # 设置快捷键
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
