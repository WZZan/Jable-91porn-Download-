import requests
import os
from bs4 import BeautifulSoup
import urllib.request
import re


def get_cover(html_file, folder_path):
  # get cover
  soup = BeautifulSoup(html_file.text, "html.parser")
  cover_name = f"{os.path.basename(folder_path)}.jpg"
  cover_path = os.path.join('D:\Game\xeditor.crx\JableTVDownload\videos', cover_name)
  for meta in soup.find_all("meta"):
      meta_content = meta.get("content")
      if not meta_content:
          continue
      if "preview.jpg" not in meta_content:
          continue
      try:
          r = requests.get(meta_content)
          with open(cover_path, "wb") as cover_fh:
              r.raw.decode_content = True
              for chunk in r.iter_content(chunk_size=1024):
                  if chunk:
                      cover_fh.write(chunk)
      except Exception as e:
          print(f"unable to download cover: {e}")

  print(f"cover downloaded as {cover_name}")


def get91_cover(html_file, folder_path,dirName):
    print(html_file.text)
    os.chdir(folder_path)
    f = open(dirName+".jpg",'wb')
    f.write(html_file.content)
    f.close()
