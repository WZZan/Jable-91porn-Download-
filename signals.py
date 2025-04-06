from PyQt5.QtCore import pyqtSignal, QObject

class WorkerSignals(QObject):
    """定义工作线程可用的信号"""
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str, str)
