import os

def ensure_dir_exists(path):
    """确保目录存在，如果不存在则创建"""
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def get_video_save_paths():
    """获取可用的视频保存路径"""
    paths = {
        "jable": [
            "J:/xeditor/videos/JAV",
            "D:/Game/xeditor.crx/JableTVDownload/videos/JAV",
            "E:/xeditor/videos/JAV"
        ],
        "91": [
            "J:/xeditor/videos/shortvideos",
            "D:/Game/xeditor.crx/JableTVDownload/videos/shortvideos",
            "E:/xeditor/videos/shortvideos"
        ]
    }
    
    # 检查路径可用性，返回第一个可用的路径
    def get_first_available(path_list):
        for path in path_list:
            if os.path.exists(os.path.dirname(path)):
                return ensure_dir_exists(path)
        # 如果没有可用路径，创建第一个
        return ensure_dir_exists(path_list[0])
    
    return {
        "jable": get_first_available(paths["jable"]),
        "91": get_first_available(paths["91"])
    }
