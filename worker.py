import os
from PyQt5.QtCore import QThread
from signals import WorkerSignals
from crawler import CustomCrawler

class DownloadWorker(QThread):
    """下载视频的工作线程"""
    def __init__(self, url):
        super().__init__()
        self.url = url
        self.signals = WorkerSignals()
        self.is_running = True
        self.crawler = None

    def run(self):
        try:
            # 自定义下载逻辑，用于集成进度报告
            self.crawler = CustomCrawler(self.report_progress)
            
            if not self.is_running:
                return
                
            # 调用主函数处理下载
            self.custom_main_jabel(self.url)
            
            if self.is_running:
                self.signals.finished.emit(self.url)
        except Exception as e:
            if self.is_running:
                self.signals.error.emit(self.url, str(e))
    
    def custom_main_jabel(self, url):
        """自定义main_jabel函数，集成进度报告"""
        try:
            # 准备阶段
            self.report_progress(0, "准备下载...")
            
            # 从原main_jabel获取必要的参数
            # 不再导入未使用的模块
            
            # 获取m3u8参数
            import re
            import m3u8
            import urllib.request
            import ssl
            from bs4 import BeautifulSoup
            from selenium import webdriver
            from selenium.webdriver.firefox.options import Options
            
            self.report_progress(5, "获取视频信息...")
            
            ssl._create_default_https_context = ssl._create_unverified_context
            
            # 获取URL中的目录名
            urlSplit = url.split('/')
            dirName = urlSplit[-2]
            
            # 设置浏览器选项
            options = Options()
            options.add_argument('--headless')
            
            self.report_progress(10, "启动浏览器...")
            
            # 打开浏览器获取页面内容 
            dr = webdriver.Firefox(options=options)
            dr.get(url)
            
            self.report_progress(20, "分析页面内容...")
            
            htmlfile = dr.page_source
            soup = BeautifulSoup(htmlfile, 'html.parser')
            videoName = soup.title.string
            videoName = videoName[:-33]
            
            # 使用正则表达式找到m3u8 URL
            result = re.search("https://.+m3u8", htmlfile)
            m3u8url = result[0]
            m3u8urlList = m3u8url.split('/')
            m3u8urlList.pop(-1)
            downloadurl = ('/'.join(m3u8urlList)).replace('\\','/')
            
            # 获取文件路径
            pathn = "D:/Game/xeditor.crx/JableTVDownload/videos/JAV"
            path2 = "E:/xeditor/videos/JAV"
            path3 = "J:/xeditor/videos/JAV"
            
            # 确定存储路径
            folderPath = None
            for path in [path3, path2, pathn]:
                if os.path.exists(path):
                    folderPath = os.path.join(path, dirName)
                    if not os.path.exists(folderPath):
                        os.makedirs(folderPath)
                    break
            
            if not folderPath:
                folderPath = os.path.join(pathn, dirName)
                if not os.path.exists(folderPath):
                    os.makedirs(folderPath)
            
            # 检查完整视频文件是否已存在
            final_video_path = os.path.join(folderPath, videoName + '.mp4')
            if os.path.exists(final_video_path):
                self.report_progress(100, "视频已存在，跳过下载")
                return
                
            self.report_progress(30, "下载m3u8文件...")
            
            # 下载m3u8文件
            m3u8file = os.path.join(folderPath, dirName + '.m3u8').replace('\\','/')
            urllib.request.urlretrieve(m3u8url, m3u8file)
            
            # 解析m3u8文件
            m3u8obj = m3u8.load(m3u8file)
            m3u8uri = ''
            m3u8iv = ''
            
            for key in m3u8obj.keys:
                if key:
                    m3u8uri = key.uri
                    m3u8iv = key.iv
            
            # 获取所有ts文件URL
            ts_list = []
            for seg in m3u8obj.segments:
                ts_url = downloadurl + '/' + seg.uri
                ts_list.append(ts_url)
            
            # 处理加密
            decryptor = None
            if m3u8uri:
                self.report_progress(40, "处理加密...")
                
                import requests
                from config import headers
                from Crypto.Cipher import AES
                
                m3u8keyurl = downloadurl + '/' + m3u8uri  # 获取key的URL
                
                # 获取key内容
                response = requests.get(m3u8keyurl, headers=headers, timeout=10)
                content_key = response.content
                
                vt = m3u8iv.replace("0x", "")[:16].encode()  # IV取前16位
                
                decryptor = AES.new(content_key, AES.MODE_CBC, vt)  # 构建解码器
            
            # 删除m3u8文件
            self.report_progress(45, "准备下载视频片段...")
            
            if os.path.exists(m3u8file):
                os.remove(m3u8file)
            
            # 这里使用我们自定义的爬虫进行下载
            self.crawler.startCrawl(decryptor, folderPath, ts_list)
            
            # 如果下载被停止，就退出
            if not self.is_running:
                return
            
            self.report_progress(95, "合并视频片段...")
            
            # 合成mp4
            try:
                from merge import mergeMp4
                mergeMp4(folderPath, ts_list, videoName)
            except Exception as e:
                self.report_progress(-1, f"合并失败: {str(e)}")
                raise e
            
            # 删除临时文件
            self.report_progress(98, "清理临时文件...")
            try:
                from delete import deleteMp4
                deleteMp4(folderPath, videoName)
            except Exception as e:
                self.report_progress(-1, f"清理文件失败: {str(e)}")
            
            # 下载封面
            self.report_progress(99, "下载封面...")
            try:
                # 下载封面图片的逻辑
                image_meta = soup.find('meta', property='og:image')
                if image_meta:
                    image_url = image_meta.get('content')
                    image_path = os.path.join(folderPath, 'cover.jpg').replace('\\','/')
                    urllib.request.urlretrieve(image_url, image_path)
            except Exception as e:
                self.report_progress(-1, f"下载封面失败: {str(e)}")
            
            # 完成
            self.report_progress(100, "下载完成")
            
        except Exception as e:
            self.report_progress(-1, f"错误: {str(e)}")
            raise e
    
    def report_progress(self, progress, status_message):
        """向主线程报告进度"""
        if self.is_running:
            self.signals.progress.emit(progress, status_message)
    
    def stop(self):
        """停止下载进程"""
        self.is_running = False
        if self.crawler:
            self.crawler.stop()

class Download91Worker(QThread):
    """下载91视频的工作线程"""
    def __init__(self, url):
        super().__init__()
        self.url = url
        self.signals = WorkerSignals()
        self.is_running = True
        self.crawler = None

    def run(self):
        try:
            if not self.is_running:
                return
                
            # 调用主函数处理91视频下载
            self.custom_main_91(self.url)
            
            if self.is_running:
                self.signals.finished.emit(self.url)
        except Exception as e:
            if self.is_running:
                self.signals.error.emit(self.url, str(e))
    
    def custom_main_91(self, url):
        """自定义main_91函数，集成进度报告"""
        try:
            # 准备阶段
            self.report_progress(0, "准备下载91视频...")
            
            # 导入必要的模块
            import requests
            import os
            import re
            import m3u8
            import urllib.request
            from Crypto.Cipher import AES
            from config import headers
            from merge import mergeMp4
            from delete import deleteM3u8, deleteMp4
            import time
            import cloudscraper
            from bs4 import BeautifulSoup
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            self.report_progress(5, "启动浏览器...")
            
            # 使用ChromeDriver启动浏览器
            options = Options()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-extensions')
            options.add_argument('--headless')
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36")

            driver = webdriver.Chrome(options=options)

            self.report_progress(10, "加载网页...")
            
            # 加载网页
            driver.get(url)

            # 等待页面完全加载
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # 获取渲染后的页面源码
            rendered_html = driver.page_source

            self.report_progress(20, "解析页面内容...")

            # 查找strencode2加密的视频源
            encoded_pattern = re.search(r"document\.write\(strencode2\(\"(.*?)\"\)\);", rendered_html)
            
            m3u8url = None
            if encoded_pattern:
                try:
                    # 需要解密strencode2函数
                    encoded_content = encoded_pattern.group(1)
                    
                    # 使用浏览器的JS引擎解密
                    decrypt_script = f"return strencode2(\"{encoded_content}\");"
                    decrypted_html = driver.execute_script(decrypt_script)
                    
                    # 从解密后的HTML中提取视频源URL - 匹配mp4或m3u8链接
                    source_pattern = re.search(r'<source src=[\'\"]([^\'\"]+(?:\.mp4|\.m3u8)[^\'\"]*?)[\'\"]', decrypted_html)
                    if source_pattern:
                        m3u8url = source_pattern.group(1)
                        # 记录找到的URL供调试
                        self.report_progress(25, f"找到视频源: {m3u8url[:50]}...")
                except Exception as e:
                    self.report_progress(-1, f"解密内容时出错: {str(e)}")
            
            # 如果上面的方法失败，尝试直接查找source标签
            if not m3u8url:
                try:
                    soup = BeautifulSoup(rendered_html, 'html.parser', from_encoding='iso-8859-1')
                    source_tag = soup.find('source')
                    if source_tag:
                        m3u8url = source_tag.get('src')
                except Exception as e:
                    self.report_progress(-1, f"查找source标签时出错: {str(e)}")
            
            # 如果仍然找不到，可能视频嵌在video.js播放器中
            if not m3u8url:
                try:
                    video_js_pattern = re.search(r'src=[\'\"](https?://[^\'\"]+\.(?:m3u8|mp4))[\'\"]', rendered_html)
                    if video_js_pattern:
                        m3u8url = video_js_pattern.group(1)
                except Exception as e:
                    self.report_progress(-1, f"查找video.js链接时出错: {str(e)}")
            
            # 关闭浏览器
            driver.quit()
            
            if not m3u8url:
                self.report_progress(-1, "未能找到视频源URL")
                return
                
            self.report_progress(30, "获取视频信息...")

            # 对视频URL进行简单处理，确保其有效
            if '?' in m3u8url:
                base_url = m3u8url
            else:
                base_url = m3u8url
            
            # 确认文件类型，决定使用哪种下载方法
            is_m3u8 = base_url.endswith('.m3u8') or '.m3u8?' in base_url
            is_mp4 = base_url.endswith('.mp4') or '.mp4?' in base_url
            
            # 获取视频标题
            cookies={"language":'zh_ZH'}
            try:
                htmlfile = cloudscraper.create_scraper(browser={
                    'browser': 'firefox',
                    'platform': 'android',
                    'desktop': False
                }, delay=10).get(url, cookies=cookies)
                
                for encoding in ['utf-8', 'iso-8859-1', 'gbk', 'big5']:
                    try:
                        htmlfile.encoding = encoding
                        soup = BeautifulSoup(htmlfile.text, 'html.parser')
                        videoName = soup.title.string
                        break
                    except UnicodeDecodeError:
                        continue
            except Exception as e:
                self.report_progress(-1, f"获取页面内容时出错: {str(e)}")
                videoName = url.split('/')[-1] or "unknownVideo"
            
            characters = "\nChinese homemade video"
            if videoName:
                for x in range(len(characters)):
                    videoName = videoName.replace(characters[x],"")
            else:
                videoName = "unknownVideo"
            
            # 清理文件名中不允许的字符
            import re
            videoName = re.sub(r'[\\/*?:"<>|]', '_', videoName)  # 替换Windows不允许的文件名字符
            
            self.report_progress(35, f"准备下载: {videoName}")

            # 直接使用存储路径，不创建子文件夹
            path3 = "J:/xeditor/videos/shortvideos"
            path2 = "D:/Game/xeditor.crx/JableTVDownload/videos/shortvideos"
            pathn = "D:/Game/xeditor.crx/JableTVDownload/videos/JAV"
            
            # 确定存储路径
            folderPath = None
            for path in [path3, path2, pathn]:
                if os.path.exists(path):
                    folderPath = path
                    break
            
            if not folderPath:
                if not os.path.exists(path3):
                    os.makedirs(path3)
                folderPath = path3
            
            # 检查完整视频文件是否已存在
            final_video_path = os.path.join(folderPath, videoName + '.mp4')
            if os.path.exists(final_video_path):
                self.report_progress(100, "视频已存在，跳过下载")
                return

            if is_m3u8:
                m3u8urlList = base_url.split('/')
                m3u8urlList.pop(-1)
                downloadurl = '/'.join(m3u8urlList)
                
                self.report_progress(40, "下载m3u8文件...")
                
                m3u8file = os.path.join(folderPath, videoName + '.m3u8')
                
                try:
                    response = requests.get(base_url, headers=headers, timeout=10)
                    with open(m3u8file, 'wb') as f:
                        f.write(response.content)
                except Exception as e:
                    self.report_progress(-1, f"下载m3u8文件失败: {str(e)}")
                    urllib.request.urlretrieve(base_url, m3u8file)
                
                self.report_progress(45, "解析m3u8文件...")
                
                try:
                    m3u8obj = m3u8.load(m3u8file)
                    m3u8uri = ''
                    m3u8iv = ''
                    
                    for key in m3u8obj.keys:
                        if key:
                            m3u8uri = key.uri
                            m3u8iv = key.iv
                    
                    ts_list = []
                    for seg in m3u8obj.segments:
                        ts_url = downloadurl + '/' + seg.uri
                        ts_list.append(ts_url)
                    
                    decryptor = None
                    if m3u8uri:
                        self.report_progress(50, "处理加密...")
                        
                        m3u8keyurl = downloadurl + '/' + m3u8uri
                        
                        response = requests.get(m3u8keyurl, headers=headers, timeout=10)
                        content_key = response.content
                        
                        vt = m3u8iv.replace("0x", "")[:16].encode() if m3u8iv else b'\0' * 16
                        
                        decryptor = AES.new(content_key, AES.MODE_CBC, vt)
                    
                    if os.path.exists(m3u8file):
                        os.remove(m3u8file)
                        
                    self.report_progress(55, "准备下载视频片段...")
                    
                    self.crawler = CustomCrawler(self.report_progress)
                    self.crawler.startCrawl(decryptor, folderPath, ts_list)
                    
                    if not self.is_running:
                        return
                        
                    self.report_progress(95, "合并视频片段...")
                    
                    try:
                        from merge import mergeMp4
                        mergeMp4(folderPath, ts_list, videoName)
                    except Exception as e:
                        self.report_progress(-1, f"合并失败: {str(e)}")
                        raise e
                    
                    self.report_progress(98, "清理临时文件...")
                    try:
                        from delete import deleteMp4
                        deleteMp4(folderPath, videoName)
                    except Exception as e:
                        self.report_progress(-1, f"清理文件失败: {str(e)}")
                except Exception as e:
                    self.report_progress(-1, f"处理m3u8文件失败: {str(e)}")
                    raise e
            
            elif is_mp4:
                self.report_progress(40, "开始下载MP4视频...")
                
                mp4_path = os.path.join(folderPath, videoName + '.mp4')
                
                try:
                    with requests.get(base_url, headers=headers, stream=True, timeout=30) as r:
                        r.raise_for_status()
                        total_size = int(r.headers.get('content-length', 0))
                        
                        if total_size == 0:
                            self.report_progress(-1, "无法获取文件大小信息")
                            self.report_progress(50, "使用备选下载方法...")
                            urllib.request.urlretrieve(base_url, mp4_path)
                            self.report_progress(100, "下载完成")
                            return
                        
                        downloaded = 0
                        with open(mp4_path, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                if not self.is_running:
                                    return
                                if chunk:
                                    f.write(chunk)
                                    downloaded += len(chunk)
                                    progress = int(50 + downloaded / total_size * 45)
                                    self.report_progress(progress, f"下载进度: {downloaded / total_size:.1%}")
                        
                        self.report_progress(98, "下载完成，检查文件...")
                        
                except Exception as e:
                    self.report_progress(-1, f"下载MP4文件失败: {str(e)}")
                    self.report_progress(50, "使用备选下载方法...")
                    urllib.request.urlretrieve(base_url, mp4_path)
            
            else:
                self.report_progress(-1, "无法识别视频类型，既不是m3u8也不是mp4")
                return
            
            self.report_progress(100, "下载完成")
            
        except Exception as e:
            self.report_progress(-1, f"下载视频时出错: {str(e)}")
            raise e
            
    def report_progress(self, progress, status_message):
        """向主线程报告进度"""
        if self.is_running:
            self.signals.progress.emit(progress, status_message)
    
    def stop(self):
        """停止下载进程"""
        self.is_running = False
        if self.crawler:
            self.crawler.stop()
