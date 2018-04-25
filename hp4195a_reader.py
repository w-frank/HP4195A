import sys
import os
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
    print(os.path.dirname(sys.executable))
    if getattr(sys, 'frozen', False):
        dir_name = os.path.dirname(sys.executable)
    else:
        dir_name = os.path.dirname(__file__)

    print(dir_name)

    log_file_path = os.path.join(dir_name, 'logging.conf')
    print(log_file_path)

    logging.config.fileConfig(log_file_path, disable_existing_loggers=False)
    lp = threading.Thread(target=ml.logger_thread, args=(logging_queue,))
    lp.daemon = True
    lp.start()

    sys.exit(app.exec_())
    dp.join()
    logging_queue.put(None)
    lp.join()
