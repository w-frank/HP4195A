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

    dp = hp.hp4195a(command_queue, message_queue, data_queue, logging_queue)
    dp.daemon = True
    dp.start()

    app = QtWidgets.QApplication(sys.argv)
    gp = MainWindow(command_queue, message_queue, data_queue, logging_queue)

    logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
    lp = threading.Thread(target=ml.logger_thread, args=(logging_queue,))
    lp.daemon = True
    lp.start()

    sys.exit(app.exec_())
    dp.join()
    logging_queue.put(None)
    lp.join()
