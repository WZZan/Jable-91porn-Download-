from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QProgressBar, 
                            QMessageBox)
from PyQt5.QtCore import Qt
from worker import DownloadWorker, Download91Worker

class DownloadItem(QFrame):
    """表示单个下载项目的小部件"""
    def __init__(self, url, platform="Jable", parent=None):
        super().__init__(parent)
        self.url = url
        self.platform = platform
        self.initUI()
        
    def initUI(self):
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        
        layout = QVBoxLayout()
        
        # 显示平台和URL
        info_layout = QHBoxLayout()
        platform_label = QLabel(f"[{self.platform}]")
        platform_label.setStyleSheet("font-weight: bold; color: #0078d7;")
        
        url_display = QLabel(self.url)
        url_display.setWordWrap(True)
        url_display.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        info_layout.addWidget(platform_label)
        info_layout.addWidget(url_display, 1)
        layout.addLayout(info_layout)
        
        # 进度条和状态
        progress_layout = QHBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        
        self.status_label = QLabel("等待中...")
        self.status_label.setMinimumWidth(100)
        
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.status_label)
        
        layout.addLayout(progress_layout)
        
        # 控制按钮
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("开始")
        self.stop_button = QPushButton("停止")
        self.remove_button = QPushButton("移除")
        
        self.stop_button.setEnabled(False)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.remove_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 初始状态
        self.worker = None
        self.is_running = False
        
    def start_download(self):
        """开始下载流程"""
        # 根据平台选择不同的下载worker
        if self.platform == "91视频":
            self.worker = Download91Worker(self.url)
        else:  # 默认为Jable
            self.worker = DownloadWorker(self.url)
            
        self.worker.signals.progress.connect(self.update_progress)
        self.worker.signals.finished.connect(self.download_finished)
        self.worker.signals.error.connect(self.download_error)
        
        self.worker.start()
        
        self.is_running = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText("下载中...")
        
    def stop_download(self):
        """停止下载流程"""
        if self.worker and self.is_running:
            self.worker.stop()
            self.status_label.setText("已停止")
            self.is_running = False
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            
    def update_progress(self, progress, status_message):
        """更新进度条和状态标签"""
        if progress < 0:  # 错误状态
            self.progress_bar.setValue(0)
            self.status_label.setText(status_message)
            self.is_running = False
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
        else:
            self.progress_bar.setValue(progress)
            self.status_label.setText(status_message)
        
    def download_finished(self, url):
        """处理下载完成"""
        self.progress_bar.setValue(100)
        self.status_label.setText("已完成")
        self.is_running = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
    def download_error(self, url, error_message):
        """处理下载错误"""
        self.status_label.setText("错误")
        self.is_running = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        QMessageBox.critical(self, "下载错误", f"下载 {url} 时出错:\n{error_message}")
