import csv
import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


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
        self.title = 'HP4195A Interface'
        self.width = 740
        self.height = 500
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        window_icon = QIcon('hp_icon.png')
        self.setWindowIcon(window_icon)
        self.graph = PlotCanvas(self, data_queue=self.data_queue, width=6, height=5)
        self.graph.move(0,0)

        self.generate_connect_button()
        self.generate_acquire_button()
        self.generate_update_button()
        self.generate_save_button()

        self.acquire_button.setEnabled(False)
        self.update_button.setEnabled(False)
        self.save_button.setEnabled(True)

        self.show()

    def connect(self):
        print('GUI: connecting to HP4195A')
        self.command_queue.put('connect')
        print('GUI: command queue size = ', self.command_queue.qsize())
        self.connect_button.setText("Disconnect")
        self.acquire_button.setEnabled(True)

    def start_acquisition(self):
        print('GUI: starting acquisition')
        self.acquire_button.setEnabled(False)
        self.command_queue.put('start_acquisition')
        self.acquire_button.setEnabled(True)
        self.update_button.setEnabled(True)
        self.save_button.setEnabled(True)

    def update_plot(self):
        print('GUI: updating plot')
        self.graph.plot()
        self.update_button.setEnabled(False)

    def generate_connect_button(self):
        self.connect_button = QtWidgets.QPushButton('Connect', self)
        self.connect_button.setToolTip('Connect to a HP4195A Network Analyser')
        self.connect_button.move(600, 0)
        self.connect_button.resize(140, 100)
        self.connect_button.clicked.connect(self.connect)

    def generate_acquire_button(self):
        self.acquire_button = QtWidgets.QPushButton('Acquire Data', self)
        self.acquire_button.setToolTip('Acquire data from a HP4195A Network Analyser')
        self.acquire_button.move(600, 100)
        self.acquire_button.resize(140, 100)
        self.acquire_button.clicked.connect(self.start_acquisition)

    def generate_update_button(self):
        self.update_button = QtWidgets.QPushButton('Update', self)
        self.update_button.setToolTip('Update the display')
        self.update_button.move(600, 200)
        self.update_button.resize(140, 100)
        self.update_button.clicked.connect(self.update_plot)

    def generate_save_button(self):
        self.save_button = QtWidgets.QPushButton('Save', self)
        self.save_button.setToolTip('Save the data')
        self.save_button.move(600, 300)
        self.save_button.resize(140, 100)
        self.save_button.clicked.connect(self.save_file_dialog)

    def save_file_dialog(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(self,"Save File","","AllFiles (*);;Text Files (*.txt)", options=options)
        if file_name:
            print(file_name)
            self.save_file(file_name)

    def save_file(self, file_name):
        file_name = file_name +'.csv'
        print('GUI: saving data to', file_name)
        rows = zip(self.graph.freq_data, self.graph.mag_data)
        with open(file_name, "w") as output:
            writer = csv.writer(output, lineterminator='\n')
            writer.writerow(["Frequency", "Magnitude"])
            for row in rows:
                writer.writerow(row)

    def closeEvent(self, event):
        if True:
            # TODO: try disconnect
            event.accept()
        else:
            event.ignore()


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
        if self.data_queue.qsize():
            self.mag_data = self.data_queue.get()
            self.freq_data = self.data_queue.get()
        else:
            self.freq_data = range(100)
            self.mag_data = [0 for i in range(100)]
        self.ax = self.figure.add_subplot(111)
        self.ax.clear()
        self.ax.semilogx(self.freq_data, self.mag_data, 'k')
        self.ax.set_xlim(np.min(self.freq_data), np.max(self.freq_data))
        self.ax.set_ylim(np.min(self.mag_data)-20, np.max(self.mag_data)+20)
        self.ax.set_xlabel('Frequency (Hz)')
        self.ax.set_ylabel('Magnitude (dB)')
        self.draw()
