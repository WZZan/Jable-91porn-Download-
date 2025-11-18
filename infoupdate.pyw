import random
import time
import logging
import re
import sys
import json
import os
from typing import Optional
from curl_cffi import requests as curl_requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTextEdit, QListWidget, QMessageBox, QProgressBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from bs4 import BeautifulSoup

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 用户代理列表
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
]

class AdultWebScraper:
    def __init__(self, timeout: int = 30):
        """
        初始化网页抓取器
        
        Args:
            timeout: 请求超时时间（秒）
        """
        self.timeout = timeout
        
        # 保存cookies状态
        self.cookies = {}
    
    def fetch_html(self, url: str, referer: str = "") -> Optional[str]:
        """
        获取指定URL的HTML内容
        
        Args:
            url: 要请求的URL
            referer: 请求的引用页，默认为空
            
        Returns:
            成功返回HTML文本内容，失败返回None
        """
        try:
            # 构建请求头
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Connection": "keep-alive",
                "Cache-Control": "max-age=0",
                "Upgrade-Insecure-Requests": "1",
                "sec-ch-ua": '"Google Chrome";v="110", "Chromium";v="110", "Not=A?Brand";v="99"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1"
            }
            
            if referer:
                headers["Referer"] = referer
            
            # 添加一些随机延迟，避免请求过快
            time.sleep(random.uniform(2, 5))
            
            # 先访问主页获取cookies
            if not self.cookies:
                logger.info("首次访问，获取初始cookies...")
                main_url = "https://jable.tv/"
                
                impersonate = "chrome110"
                response = curl_requests.get(
                    main_url,
                    headers=headers,
                    impersonate=impersonate,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    self.cookies = response.cookies
                    logger.info("成功获取初始cookies")
                    # 额外等待，避免被识别为机器人
                    time.sleep(random.uniform(3, 6))
            
            # 使用curl_cffi发送请求
            impersonate = "chrome110"
            response = curl_requests.get(
                url,
                headers=headers,
                cookies=self.cookies,
                impersonate=impersonate,
                timeout=self.timeout
            )
            
            # 更新cookies
            if response.cookies:
                self.cookies.update(response.cookies)
            
            # 检查状态码
            if response.status_code == 403:
                logger.warning(f"遇到403错误，尝试更多Cookie或等待...")
                # 等待更长时间后再次尝试
                time.sleep(random.uniform(10, 15))
                
                # 增加可能的必要cookie
                self.cookies.update({
                    "disclaimer_agreed": "true",
                    "age_verified": "true"
                })
                
                # 再次尝试
                response = curl_requests.get(
                    url,
                    headers=headers,
                    cookies=self.cookies,
                    impersonate=impersonate,
                    timeout=self.timeout
                )
            
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"请求失败: {str(e)}")
            return None
    
    def extract_video_info(self, html: str) -> dict:
        """
        从HTML中提取视频信息
        
        Args:
            html: 网页HTML内容
            
        Returns:
            包含视频信息的字典
        """
        # 这里可以使用Beautiful Soup或正则表达式来提取所需信息
        
        info = {
            "title": "",
            "video_url": "",
            "thumbnail": "",
            "header_right_content": ""
        }
        
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(html, 'html.parser')
        
        # 提取标题
        title_match = re.search(r'<title>(.*?)</title>', html)
        if title_match:
            info["title"] = title_match.group(1)
        
        # 查找class="header-right d-none d-md-block"的元素
        header_right = soup.find(class_="header-right d-none d-md-block")
        if header_right:
            # 只提取文本内容
            info["header_right_content"] = header_right.get_text(strip=True)
        
        return info

# 爬虫线程类
class ScraperThread(QThread):
    progress_signal = pyqtSignal(int, int)  # 当前索引, 总数
    result_signal = pyqtSignal(str, str)  # 键, 值
    finished_signal = pyqtSignal()
    error_signal = pyqtSignal(str, str)  # url, 错误信息
    
    def __init__(self, urls, parent=None):
        super().__init__(parent)
        self.urls = urls
        self.scraper = AdultWebScraper(timeout=30)
        self.results = {}
        
    def run(self):
        total = len(self.urls)
        for index, url in enumerate(self.urls):
            try:
                # 更新进度
                self.progress_signal.emit(index + 1, total)
                
                # 从URL中提取键值
                key_match = re.search(r'/([^/]+)/$', url)
                if key_match:
                    key = key_match.group(1)
                else:
                    key = url
                
                # 获取网页内容
                html = self.scraper.fetch_html(url)
                
                if html:
                    # 提取信息
                    info = self.scraper.extract_video_info(html)
                    
                    # 存储结果
                    if info["header_right_content"]:
                        result_value = info["header_right_content"]
                    else:
                        result_value = "未找到内容"
                else:
                    result_value = "获取失败"
                
                # 发送结果信号
                self.result_signal.emit(key, result_value)
                self.results[key] = result_value
                
                # 添加延迟，避免请求过快
                time.sleep(random.uniform(3, 5))
                
            except Exception as e:
                self.error_signal.emit(url, str(e))
        
        # 完成信号
        self.finished_signal.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.urls_to_scrape = []
        self.results = {}
        self.urls_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saved_urls.json')
        self.init_ui()
        self.load_saved_urls()
        
    def init_ui(self):
        # 设置窗口属性
        self.setWindowTitle('Jable TV 信息爬取工具')
        self.setGeometry(100, 100, 800, 600)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # URL 输入部分
        url_layout = QHBoxLayout()
        url_label = QLabel('URL:')
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText('输入Jable视频页面URL，例如: https://jable.tv/videos/sone-558/')
        add_button = QPushButton('添加')
        add_button.clicked.connect(self.add_url)
        
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(add_button)
        
        main_layout.addLayout(url_layout)
        
        # URL 列表
        url_list_label = QLabel('待处理URL列表:')
        self.url_list = QListWidget()
        
        # URL操作按钮布局
        url_actions_layout = QHBoxLayout()
        remove_button = QPushButton('删除所选')
        remove_button.clicked.connect(self.remove_selected_url)
        clear_button = QPushButton('清空列表')
        clear_button.clicked.connect(self.clear_urls)
        
        url_actions_layout.addWidget(remove_button)
        url_actions_layout.addWidget(clear_button)
        
        # 爬取控制按钮布局
        button_layout = QHBoxLayout()
        start_button = QPushButton('开始爬取')
        start_button.clicked.connect(self.start_scraping)
        
        button_layout.addWidget(start_button)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setFormat("%v/%m (%p%)")
        
        # 结果显示
        result_label = QLabel('爬取结果:')
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        
        main_layout.addWidget(url_list_label)
        main_layout.addWidget(self.url_list)
        main_layout.addLayout(url_actions_layout)  # URL操作按钮
        main_layout.addLayout(button_layout)       # 爬取控制按钮
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(result_label)
        main_layout.addWidget(self.result_text)
        
    def add_url(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, '警告', '请输入URL')
            return
            
        # 检查URL格式
        if not url.startswith('https://jable.tv/videos/'):
            QMessageBox.warning(self, '警告', 'URL格式不正确，应以 https://jable.tv/videos/ 开头')
            return
            
        # 确保URL以/结尾
        if not url.endswith('/'):
            url += '/'
            
        # 避免重复添加
        if url in self.urls_to_scrape:
            QMessageBox.information(self, '提示', '此URL已在列表中')
            return
            
        self.urls_to_scrape.append(url)
        self.url_list.addItem(url)
        self.url_input.clear()
        # 保存URLs
        self.save_urls()
        
    def remove_selected_url(self):
        """删除选中的URL"""
        selected_items = self.url_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, '提示', '请先选择要删除的URL')
            return
            
        for item in selected_items:
            url = item.text()
            if url in self.urls_to_scrape:
                self.urls_to_scrape.remove(url)
            
            # 从列表组件中移除
            row = self.url_list.row(item)
            self.url_list.takeItem(row)
            
        # 保存更改
        self.save_urls()
        
    def clear_urls(self):
        """清空URL列表"""
        self.urls_to_scrape.clear()
        self.url_list.clear()
        # 保存更改
        self.save_urls()
    
    def save_urls(self):
        """保存URLs到JSON文件"""
        try:
            with open(self.urls_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.urls_to_scrape, f, ensure_ascii=False, indent=2)
            logger.info(f"URLs saved to {self.urls_file_path}")
        except Exception as e:
            logger.error(f"Error saving URLs: {str(e)}")
            QMessageBox.warning(self, '保存失败', f'无法保存URL列表: {str(e)}')
    
    def load_saved_urls(self):
        """从JSON文件加载保存的URLs"""
        if not os.path.exists(self.urls_file_path):
            logger.info("No saved URLs file found")
            return
            
        try:
            with open(self.urls_file_path, 'r', encoding='utf-8') as f:
                urls = json.load(f)
                
            if urls and isinstance(urls, list):
                self.urls_to_scrape = urls
                # 更新URL列表组件
                self.url_list.clear()
                for url in self.urls_to_scrape:
                    self.url_list.addItem(url)
                    
                logger.info(f"Loaded {len(urls)} URLs from saved file")
        except Exception as e:
            logger.error(f"Error loading saved URLs: {str(e)}")
    
    def closeEvent(self, event):
        """在关闭前保存URLs"""
        self.save_urls()
        event.accept()
        
    def start_scraping(self):
        if not self.urls_to_scrape:
            QMessageBox.warning(self, '警告', '请先添加URL')
            return
            
        # 清空结果
        self.result_text.clear()
        self.results = {}
        
        # 设置进度条
        self.progress_bar.setRange(0, len(self.urls_to_scrape))
        self.progress_bar.setValue(0)
        
        # 创建并启动爬虫线程
        self.scraper_thread = ScraperThread(self.urls_to_scrape)
        self.scraper_thread.progress_signal.connect(self.update_progress)
        self.scraper_thread.result_signal.connect(self.update_result)
        self.scraper_thread.finished_signal.connect(self.scraping_finished)
        self.scraper_thread.error_signal.connect(self.scraping_error)
        
        self.scraper_thread.start()
        
    def update_progress(self, current, total):
        self.progress_bar.setValue(current)
        
    def update_result(self, key, value):
        self.results[key] = value

        # 更新结果显示（使用HTML富文本）
        result_text = ""
        for k, v in self.results.items():
            result_text += f"<b>==== {k} ====</b><br>"
            # 如果内容少于6个字符，显示URL并设置背景为绿色
            if len(v) < 6:
                url_for_key = next((u for u in self.urls_to_scrape if k in u), None)
                result_text += f'<span style="background-color: #90ee90;">{v}</span><br>'
                if url_for_key:
                    result_text += f'<span style="background-color: #90ee90;">[原始URL: {url_for_key}]</span><br>'
            else:
                result_text += v + "<br>"
            result_text += "=" * (8 + len(k)) + "<br><br>"

        self.result_text.setHtml(result_text)
        
    def scraping_finished(self):
        QMessageBox.information(self, '完成', '所有URL已处理完成')
        
    def scraping_error(self, url, error):
        self.result_text.append(f"处理 {url} 时出错: {error}\n")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())




