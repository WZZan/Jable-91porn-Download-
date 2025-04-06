import sys
from PyQt5.QtWidgets import QApplication
from main_window import MainWindow
from styles import get_stylesheet

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # 设置样式表以获得现代外观
    app.setStyleSheet(get_stylesheet())
    
    window = MainWindow()
    window.setWindowTitle("My Application")  # 更新应用程序标题
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
