from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QProgressBar, 
                            QMessageBox)
from PyQt5.QtCore import Qt
from worker import DownloadWorker, Download91Worker, DownloadM3u8Worker

class DownloadItem(QFrame):
    """表示单个下载项目的小部件"""
    def __init__(self, url, platform="Jable", custom_filename="", path_type="jav", parent=None):
        super().__init__(parent)
        self.url = url
        self.platform = platform
        self.custom_filename = custom_filename  # 添加自定义文件名属性
        self.path_type = path_type  # 添加路径类型属性 (jav 或 91)
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
        
        # 如果是M3U8平台且有自定义文件名，显示文件名和路径类型
        if self.platform == "M3U8" and self.custom_filename:
            filename_layout = QHBoxLayout()
            filename_label = QLabel("文件名:")
            filename_label.setStyleSheet("font-weight: bold; color: #2d7d2d;")
            filename_display = QLabel(self.custom_filename)
            filename_display.setStyleSheet("color: #2d7d2d;")
            
            filename_layout.addWidget(filename_label)
            filename_layout.addWidget(filename_display, 1)
            layout.addLayout(filename_layout)
            
            # 显示路径类型
            path_layout = QHBoxLayout()
            path_label = QLabel("保存到:")
            path_label.setStyleSheet("font-weight: bold; color: #7d4d2d;")
            path_type_text = "JAV文件夹" if self.path_type == "jav" else "91视频文件夹"
            path_display = QLabel(path_type_text)
            path_display.setStyleSheet("color: #7d4d2d;")
            
            path_layout.addWidget(path_label)
            path_layout.addWidget(path_display, 1)
            layout.addLayout(path_layout)
        
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
        elif self.platform == "M3U8":
            # 使用自定义文件名，如果没有则从URL中提取
            video_name = self.custom_filename if self.custom_filename else (
                self.url.split('/')[-1].split('.')[0] if '/' in self.url else "m3u8_video"
            )
            # 传递路径类型给M3U8Worker
            self.worker = DownloadM3u8Worker(self.url, video_name, self.path_type)
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
