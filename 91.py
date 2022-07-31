
import requests
import os
import re
import m3u8
import urllib.request
from Crypto.Cipher import AES
from config import headers
from crawler import prepareCrawl
from merge import mergeMp4
from delete import deleteM3u8, deleteMp4
from cover import get91_cover
import time
import cloudscraper
from args import *
from bs4 import BeautifulSoup



parser = get_parser()
args = parser.parse_args()

if(len(args.url) != 0):
    url = args.url
elif(args.random == True):
    url = av_recommand()
else:
    # 使用者輸入Jable網址
    url = input('輸入91PORN網址:')





# 建立番號資料夾
cookies={"language":'zh_ZH'}
htmlfile = cloudscraper.create_scraper(browser='firefox', delay=10).get(url,cookies=cookies)


pathn="D:/Game/xeditor.crx/JableTVDownload/videos/91porn"
path2="D:/Game/xeditor.crx/JableTVDownload/videos/JAV"
soup = BeautifulSoup(htmlfile.text,'html.parser')


dirName = soup.title.string
characters = "\nChinese homemade video"
for x in range(len(characters)):
    dirName = dirName.replace(characters[x],"")
videoName = dirName





os.chdir(pathn)
if not os.path.exists(dirName):
    os.makedirs(dirName)
folderPath = os.path.join(os.getcwd(), dirName)
os.chdir(path2)





result = re.findall('<div id=VID style="display:none;">(.*?)</div>', htmlfile.text)
m3u8url = 'https://cdn77.91p49.com/m3u8/'+ result[0]+'/'+result[0]+'.m3u8'
m3u8urlList = m3u8url.split('/')
m3u8urlList.pop(-1)
downloadurl = '/'.join(m3u8urlList)


# 儲存 m3u8 file 至資料夾
m3u8file = os.path.join(folderPath, dirName + '.m3u8')
urllib.request.urlretrieve(m3u8url, m3u8file)



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
result2 = re.search("https://img.91p51.com/thumb/.+jpg", htmlfile.text)
print(result2[0])


html_file = cloudscraper.create_scraper(browser='firefox', delay=10).get(result2[0])

get91_cover(html_file, folderPath,videoName)
