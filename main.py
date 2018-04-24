import sys
import threading
import logging.config

import hp4195a as hp
import multi_logging as ml

from multiprocessing import Queue, freeze_support
from main_window import MainWindow
from PyQt5 import QtWidgets

if __name__ == '__main__':
    freeze_support()

    command_queue = Queue()
    message_queue = Queue()
    data_queue = Queue()
    logging_queue = Queue()

    logging.config.fileConfig("logging.conf", disable_existing_loggers=False)

    b = hp.hp4195a(command_queue, message_queue, data_queue, logging_queue)
    b.daemon = True
    b.start()

    a = QtWidgets.QApplication(sys.argv)
    ex = MainWindow(command_queue, message_queue, data_queue, logging_queue)

    lp = threading.Thread(target=ml.logger_thread, args=(logging_queue,))
    lp.start()

    logging_queue.put(None)
    lp.join()
    sys.exit(a.exec_())
