def get_stylesheet():
    """返回应用程序的样式表"""
    return """
    QMainWindow {
        background-color: #f0f0f0;
    }
    QFrame {
        border: 1px solid #ddd;
        border-radius: 5px;
        background-color: white;
        margin: 5px;
        padding: 5px;
    }
    QPushButton {
        background-color: #0078d7;
        color: white;
        border: none;
        border-radius: 3px;
        padding: 5px 10px;
        min-width: 80px;
    }
    QPushButton:hover {
        background-color: #1e88e5;
    }
    QPushButton:pressed {
        background-color: #0062b1;
    }
    QPushButton:disabled {
        background-color: #cccccc;
        color: #666666;
    }
    QProgressBar {
        border: 1px solid #ddd;
        border-radius: 3px;
        text-align: center;
    }
    QProgressBar::chunk {
        background-color: #4caf50;
    }
    QComboBox {
        border: 1px solid #ddd;
        border-radius: 3px;
        padding: 5px;
        min-width: 100px;
    }
    QComboBox::drop-down {
        width: 20px;
    }
    """
