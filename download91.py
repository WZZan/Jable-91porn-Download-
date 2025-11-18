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
import copy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import base64
import html

def strencode(encoded_str):
    """
    Decode the encoded string found in the JavaScript strencode2 function
    """
    # Remove HTML entities and decode the string
    encoded_str = html.unescape(encoded_str)
    
    # Extract the hex values from the string
    hex_values = re.findall(r'%([0-9a-fA-F]{2})', encoded_str)
    
    # Convert hex values to characters
    decoded_str = ''.join([chr(int(hex_val, 16)) for hex_val in hex_values])
    
    return decoded_str

def main_91(url):
    # Use ChromeDriver to start the browser
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-extensions')
    options.add_argument('--headless')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36")

    driver = webdriver.Chrome(options=options)

    # Load the webpage
    driver.get(url)

    # Wait until page is fully loaded
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    # Get the rendered page source
    rendered_html = driver.page_source
    
    # Close the browser
    driver.quit()
    
    # Use BeautifulSoup to parse the HTML
    soup = BeautifulSoup(rendered_html, 'html.parser')
    
    # Look for the encrypted video source in the script
    encoded_source = None
    scripts = soup.find_all('script')
    
    for script in scripts:
        if script.string and 'strencode2' in script.string:
            # Extract the encoded string between the strencode2 function
            match = re.search(r'strencode2\("([^"]+)"', script.string)
            if match:
                encoded_source = match.group(1)
                break
    
    if not encoded_source:
        # Try another method - look for document.write(strencode2
        script_with_source = soup.find('script', string=lambda text: text and 'document.write(strencode2' in text)
        if script_with_source:
            # Extract content between the quotes after strencode2
            match = re.search(r'strencode2\("([^"]+)"', script_with_source.string)
            if match:
                encoded_source = match.group(1)
    
    m3u8url = None
    
    if encoded_source:
        # Decode the encoded source
        decoded_html = strencode(encoded_source)
        # Extract the video source URL
        source_match = re.search(r'<source\s+src=[\'"]([^\'"]+)[\'"]', decoded_html)
        if source_match:
            m3u8url = source_match.group(1)
            print("Found video URL:", m3u8url)
    else:
        # Fallback to the original method
        source_tag = soup.find('source')
        if source_tag:
            m3u8url = source_tag.get('src')
            print("SRC:", m3u8url)
        else:
            print("未找到<source>元素。")
            return

    # Create folder for the video
    cookies = {"language": 'zh_ZH'}
    htmlfile = cloudscraper.create_scraper(browser={
        'browser': 'firefox',
        'platform': 'android',
        'desktop': False
    }, delay=10).get(url, cookies=cookies)

    pathn = "D:/Game/xeditor.crx/JableTVDownload/videos/shortvideos"
    path2 = "D:/Game/xeditor.crx/JableTVDownload/videos/JAV"
    soup = BeautifulSoup(htmlfile.text, 'html.parser')

    dirName = soup.title.string
    characters = "\nChinese homemade video"
    for x in range(len(characters)):
        dirName = dirName.replace(characters[x], "")
    videoName = dirName

    os.chdir(pathn)
    if not os.path.exists(dirName):
        os.makedirs(dirName)
    folderPath = os.path.join(os.getcwd(), dirName)
    os.chdir(path2)

    if m3u8url:
        m3u8urlList = m3u8url.split('/')
        m3u8urlList.pop(-1)
        downloadurl = '/'.join(m3u8urlList)

        # Save m3u8 file to folder
        m3u8file = os.path.join(folderPath, dirName + '.mp4')
        urllib.request.urlretrieve(m3u8url, m3u8file)
        print(f"Downloaded video to: {m3u8file}")
    else:
        print("无法获取视频链接")


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()

    if(len(args.url) != 0):
        url = args.url
    elif(args.random == True):
        url = av_recommand()
    else:
        # User inputs Jable URL
        url = input('輸入91PORN網址:')
    main_91(url)

