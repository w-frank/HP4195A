import sys
import hp4195a as hp
from multiprocessing import Queue, freeze_support
from main_window import MainWindow
from PyQt5 import QtWidgets

if __name__ == '__main__':
    freeze_support()
    command_queue = Queue()
    data_queue = Queue()

    b = hp.hp4195a(command_queue, data_queue)
    b.daemon = True
    b.start()

    a = QtWidgets.QApplication(sys.argv)
    ex = MainWindow(command_queue, data_queue)
    sys.exit(a.exec_())
