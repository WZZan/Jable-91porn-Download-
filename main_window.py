from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLineEdit, QLabel, QScrollArea, 
                            QMessageBox, QComboBox)
from download_item import DownloadItem

class MainWindow(QMainWindow):
    """主应用窗口"""
    def __init__(self):
        super().__init__()
        self.download_items = []
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("视频下载器")
        self.setMinimumSize(800, 600)
        
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # URL输入部分
        url_layout = QHBoxLayout()
        
        url_label = QLabel("视频URL:")
        self.url_input = QLineEdit()
        
        # 添加平台选择下拉框
        self.platform_selector = QComboBox()
        self.platform_selector.addItem("Jable")
        self.platform_selector.addItem("91视频")
        
        add_button = QPushButton("添加")
        
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.platform_selector)
        url_layout.addWidget(add_button)
        
        main_layout.addLayout(url_layout)
        
        # 下载区域
        downloads_label = QLabel("下载列表:")
        main_layout.addWidget(downloads_label)
        
        # 下载列表的滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        self.downloads_widget = QWidget()
        self.downloads_layout = QVBoxLayout(self.downloads_widget)
        self.downloads_layout.addStretch()
        
        scroll_area.setWidget(self.downloads_widget)
        main_layout.addWidget(scroll_area)
        
        # 控制按钮
        control_layout = QHBoxLayout()
        
        start_all_button = QPushButton("全部开始")
        stop_all_button = QPushButton("全部停止")
        remove_all_button = QPushButton("全部移除")
        
        control_layout.addWidget(start_all_button)
        control_layout.addWidget(stop_all_button)
        control_layout.addWidget(remove_all_button)
        
        main_layout.addLayout(control_layout)
        
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # 连接信号
        add_button.clicked.connect(self.add_download)
        self.url_input.returnPressed.connect(self.add_download)
        start_all_button.clicked.connect(self.start_all_downloads)
        stop_all_button.clicked.connect(self.stop_all_downloads)
        remove_all_button.clicked.connect(self.remove_all_downloads)
        
    def add_download(self):
        """添加新的下载到列表"""
        url = self.url_input.text().strip()
        platform = self.platform_selector.currentText()
        
        if not url:
            QMessageBox.warning(self, "无效URL", "请输入有效的URL。")
            return
        
        # 创建并添加新的下载项
        download_item = DownloadItem(url, platform)
        self.download_items.append(download_item)
        
        # 在末尾伸展前插入新项目
        self.downloads_layout.insertWidget(self.downloads_layout.count() - 1, download_item)
        
        # 连接信号
        download_item.start_button.clicked.connect(lambda: download_item.start_download())
        download_item.stop_button.clicked.connect(lambda: download_item.stop_download())
        download_item.remove_button.clicked.connect(lambda: self.remove_download(download_item))
        
        # 清除输入
        self.url_input.clear()
        
    def remove_download(self, download_item):
        """从列表中移除下载"""
        download_item.stop_download()
        self.downloads_layout.removeWidget(download_item)
        self.download_items.remove(download_item)
        download_item.deleteLater()
            
    def start_all_downloads(self):
        """开始所有下载"""
        for item in self.download_items:
            if not item.is_running:
                item.start_download()
                
    def stop_all_downloads(self):
        """停止所有下载"""
        for item in self.download_items:
            if item.is_running:
                item.stop_download()
                
    def remove_all_downloads(self):
        """移除所有下载"""
        # 先停止所有下载
        self.stop_all_downloads()
        
        # 移除所有项目
        while self.download_items:
            item = self.download_items[0]
            self.remove_download(item)
            
    def closeEvent(self, event):
        """处理窗口关闭事件"""
        # 关闭前停止所有下载
        running_downloads = any(item.is_running for item in self.download_items)
        
        if running_downloads:
            reply = QMessageBox.question(self, "确认退出",
                                         "下载仍在进行中。确定要退出吗？",
                                         QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                self.stop_all_downloads()
                event.accept()
            else:
                event.ignore()
