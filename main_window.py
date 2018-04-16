import sys
import hp4195a as hp
from multiprocessing import Queue

from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import random
import time

class MainWindow(QtWidgets.QMainWindow):
    '''
    This class is for the main GUI, it creates the buttons and their events.
    It does not directly communicate with the hardware, but instead puts
    items in a command queue which are handled by another process.
    '''
    def __init__(self, command_queue, data_queue):
        super(MainWindow, self).__init__()
        self.command_queue = command_queue
        self.data_queue = data_queue
        self.left = 50
        self.top = 50
        self.title = 'HP4195A Control'
        self.width = 640
        self.height = 400
        self.initUI()


    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        window_icon = QIcon('hp_icon.png')
        self.setWindowIcon(window_icon)
        self.graph = PlotCanvas(self, data_queue=self.data_queue, width=5, height=4)
        self.graph.move(0,0)

        self.connect_button = QtWidgets.QPushButton('Connect', self)
        self.connect_button.setToolTip('Connect to a HP4195A Network Analyser')
        self.connect_button.move(500, 0)
        self.connect_button.resize(140, 100)
        self.connect_button.clicked.connect(self.connect)

        self.connect_button = QtWidgets.QPushButton('Acquire Data', self)
        self.connect_button.setToolTip('Acquire data from a HP4195A Network Analyser')
        self.connect_button.move(500, 100)
        self.connect_button.resize(140, 100)
        self.connect_button.clicked.connect(self.start_acquisition)

        self.connect_button = QtWidgets.QPushButton('Update Plot', self)
        self.connect_button.setToolTip('Update the plot')
        self.connect_button.move(500, 200)
        self.connect_button.resize(140, 100)
        self.connect_button.clicked.connect(self.update_plot)

        self.show()

    def connect(self):
        print('GUI: connecting to HP4195A')
        self.command_queue.put('connect')
        print('GUI: command queue size = ', self.command_queue.qsize())

    def start_acquisition(self):
        print('GUI: starting acquisition')
        self.command_queue.put('start_acquisition')

    def update_plot(self):
        print('GUI: updating plot')
        self.graph.plot()

class PlotCanvas(FigureCanvas):

    def __init__(self,
                 parent=None,
                 data_queue=None,
                 width=5,
                 height=4,
                 dpi=100):
        self.data_queue = data_queue
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.plot()

    def plot(self):
        data = [random.randint(0, 10) for i in range(random.randint(0, 10))]
        ax = self.figure.add_subplot(111)
        ax.clear()
        ax.plot(data, 'k')
        ax.set_xlim(0, 11)
        ax.set_ylim(-2, 12)
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Magnitude (dB)')
        self.draw()

if __name__ == '__main__':
    command_queue = Queue()
    data_queue = Queue()

    b = hp.hp4195a(command_queue, data_queue)
    b.daemon = True
    b.start()

    a = QtWidgets.QApplication(sys.argv)
    ex = MainWindow(command_queue, data_queue)
    sys.exit(a.exec_())
