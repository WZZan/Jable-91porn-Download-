import os
import copy
import concurrent.futures
from functools import partial

class CustomCrawler:
    """自定义爬虫类，用于集成进度报告和停止功能"""
    def __init__(self, progress_callback=None):
        self.progress_callback = progress_callback
        self.is_running = True
        
    def scrape(self, ci, folderPath, downloadList, tsList, urls):
        if not self.is_running:
            return
            
        fileName = urls.split('/')[-1][0:-3]
        saveName = os.path.join(folderPath, fileName + ".mp4")
        total_files = len(tsList)

        if os.path.exists(saveName):
            # 跳过已下载
            if urls in downloadList:
                downloadList.remove(urls)
            completed = total_files-len(downloadList)
            progress = int((completed / total_files) * 100)
            
            # 报告进度
            if self.progress_callback:
                self.progress_callback(progress, f"下载中: {completed}/{total_files}")
            return

        try:
            from config import headers
            import requests
            
            response = requests.get(urls, headers=headers, timeout=10)
            if response.status_code == 200:
                content_ts = response.content
                if ci:
                    content_ts = ci.decrypt(content_ts)  # 解码
                with open(saveName, 'ab') as f:
                    f.write(content_ts)
                if urls in downloadList:
                    downloadList.remove(urls)
                completed = total_files - len(downloadList)
                progress = int((completed / total_files) * 100)
                
                # 报告进度
                if self.progress_callback:
                    self.progress_callback(progress, f"下载中: {completed}/{total_files}")
        except Exception as e:
            if self.progress_callback:
                self.progress_callback(-1, f"错误: {str(e)}")

    def startCrawl(self, ci, folderPath, tsList):
        if not self.is_running:
            return
            
        # 同时建立及启用 8 个执行线程
        downloadList = copy.deepcopy(tsList)
        round = 0
        
        while downloadList and self.is_running:
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                executor.map(partial(self.scrape, ci, folderPath,
                                    downloadList, tsList), downloadList[:])
            
            # 如果用户停止下载，则退出循环
            if not self.is_running:
                break
                
            round += 1
            
            # 检查是否所有文件都已下载
            if not downloadList:
                if self.progress_callback:
                    self.progress_callback(100, "下载完成")
                break
            else:
                if self.progress_callback:
                    completed = len(tsList) - len(downloadList)
                    progress = int((completed / len(tsList)) * 100)
                    self.progress_callback(progress, f"重试第{round}轮: {completed}/{len(tsList)}")
        
        # 如果被停止，发送停止状态
        if not self.is_running and self.progress_callback:
            self.progress_callback(-1, "已停止")
    
    def stop(self):
        """停止爬虫处理"""
        self.is_running = False
