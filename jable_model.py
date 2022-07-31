from bs4 import BeautifulSoup
import requests
import os
import re
import urllib.request
import m3u8
from Crypto.Cipher import AES
from config import headers
from crawler import prepareCrawl
from merge import mergeMp4
from delete import deleteM3u8, deleteMp4
from cover import get91_cover
from cover import get_cover
import time
import cloudscraper
from args import *



model_url= input('輸入jable model網址:')

htmlfile = cloudscraper.create_scraper(browser={
        'browser': 'firefox',
        'platform': 'android',
        'desktop': False
    }
    , delay=10).get(model_url)
soup = BeautifulSoup(htmlfile.text,'html.parser')
videoName = soup.find_all("li",class_='page-item')
page=len(videoName)
Video_html=[]
if page==0:
    page = page + 2  

for i in range(1,page):
    pageform = str(i)
    urlx = model_url+"?mode=async&function=get_block&block_id=list_videos_common_videos_list&sort_by=post_date&from=0"+ pageform +'&_=1659228741053'
    model_htmlfile = cloudscraper.create_scraper(browser={
        'browser': 'firefox',
        'platform': 'android',
        'desktop': False
    }, delay=10).get(urlx)
    video_html = re.findall("<h6 class=\"title\"><a href=\"(.*?)\">",model_htmlfile.text)
    Video_html = Video_html+video_html 
        

for x in range(0,len(Video_html),):
    url = Video_html[x]
    print(url)

    urlSplit = url.split('/')
    dirName = urlSplit[-2]
    


    htmlfile = cloudscraper.create_scraper(browser={
        'browser': 'firefox',
        'platform': 'android',
        'desktop': False
    }, delay=10).get(url)
    soup = BeautifulSoup(htmlfile.text,'html.parser')
    videoName = soup.title.string
    videoName = videoName[:-33]

    if not os.path.exists(dirName):
        os.makedirs(dirName)
    else :
        continue    
    folderPath = os.path.join(os.getcwd(), dirName)
    # In[4]:
    print(dirName)  

    # 得到 m3u8 網址

    result = re.search("https://.+m3u8", htmlfile.text)
    m3u8url = result[0]
    m3u8urlList = m3u8url.split('/')
    m3u8urlList.pop(-1)
    downloadurl = '/'.join(m3u8urlList)


    # 儲存 m3u8 file 至資料夾
    m3u8file = os.path.join(folderPath, dirName + '.m3u8')
    urllib.request.urlretrieve(m3u8url, m3u8file)


    # In[5]:


    # 得到 m3u8 file裡的 URI和 IV
    m3u8obj = m3u8.load(m3u8file)
    m3u8uri = ''
    m3u8iv = ''

    for key in m3u8obj.keys:
        if key:
            m3u8uri = key.uri
            m3u8iv = key.iv

    # 儲存 ts網址 in tsList
    tsList = []
    for seg in m3u8obj.segments:
        tsUrl = downloadurl + '/' + seg.uri
        tsList.append(tsUrl)


    # In[6]:


    # 有加密
    if m3u8uri:
        m3u8keyurl = downloadurl + '/' + m3u8uri  # 得到 key 的網址

        # 得到 key的內容
        response = requests.get(m3u8keyurl, headers=headers, timeout=10)
        contentKey = response.content

        vt = m3u8iv.replace("0x", "")[:16].encode()  # IV取前16位

        ci = AES.new(contentKey, AES.MODE_CBC, vt)  # 建構解碼器
    else:
        ci = ''


    # In[7]:


    # 刪除m3u8 file
    deleteM3u8(folderPath)


    # In[8]:


    # 開始爬蟲並下載mp4片段至資料夾
    prepareCrawl(ci, folderPath, tsList)


    # In[9]:


    # 合成mp4
    mergeMp4(folderPath, tsList,videoName)


    # In[10]:


    # 刪除子mp4
    deleteMp4(folderPath,videoName)

    # In[11]:
    # get cover
    get_cover(html_file=htmlfile, folder_path=folderPath)

    result2 = re.search("og:image\" content=\"https://assets-cdn.jable.tv/contents/videos_screenshots/.+jpg", htmlfile.text)
    result2 =  result2[0]
    result2 = result2[19:]

    html_file = cloudscraper.create_scraper(browser='firefox', delay=10).get(result2)
    get91_cover(html_file, folderPath,videoName)



