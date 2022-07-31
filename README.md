# Jable-91porn-Download

## 可以下載 Jable 和 91porn 的影片

### vitual env
```
python3 -m venv jable
source jable/bin/activate. # MacOS
```

### requirements
`pip install -r requirements.txt`

安裝 [FFmpeg] (未安裝也能下載 但影片拖拉時間軸會有卡幀情況發生)

### 執行jable程式(Execute) 或 91程式

要下載哪個網頁的影片請選擇對的程式

`python jable.py`    `python 91.py`

### 輸入影片網址(Input video url)
`https://jable.tv/videos/SSIS-423/`     
`https://www.91porn.com/view_video.php?viewkey=328e7b2ad40e015f35d5&page=1&viewtype=basic&category=mf`  

## #####選擇性使用(Optional use)#####

### 使用FFmpeg轉檔優化 : 參數能自己調(Use FFmpeg encode) 
`cd SSIS-423`  
`ffmpeg -i SSIS-423.mp4 -c:v libx264 -b:v 3M -threads 5 -preset superfast f_SSIS-423.mp4`  
  


### Argument parser
`$python jable.py -h`

![](https://i.imgur.com/qgyS5sf.png)

`$python jable.py --random True`

可以直接下載隨機熱門影片

![](https://i.imgur.com/dSsdB7Y.png)

可以直接爬取某個女優的全部影片(目前只支援jable)

`$python jable_model.py https://jable.tv/models/7cadf3e484f607dc7d0f1c0e7a83b007/`

