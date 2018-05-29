import csv
import markdown
import logging
import logging.handlers
import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui, QtWebEngineWidgets
from PyQt5.QtGui import QIcon
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class MainWindow(QtWidgets.QMainWindow):
    '''
    This class is for the main GUI window, it creates the graph, textboxes, buttons etc. and their events. It does not directly communicate with the hardware but instead puts messages in a command queue which are handled by another process.
    '''
    def __init__(self, command_queue, message_queue, data_queue, logging_queue):
        super(MainWindow, self).__init__()
        # create data queues
        self.command_queue = command_queue
        self.message_queue = message_queue
        self.data_queue = data_queue
        self.logging_queue = logging_queue

        # main window settings
        self.title = 'HP4195A'
        self.window_icon = QIcon('hp_icon.png')
        self.width = 740
        self.height = 600

        # create logging queue and handler
        self.qh = logging.handlers.QueueHandler(self.logging_queue)
        self.root = logging.getLogger()
        self.root.setLevel(logging.DEBUG)
        self.root.addHandler(self.qh)
        self.logger = logging.getLogger(__name__)

        self.connected = False
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setFixedSize(self.width, self.height)
        self.setWindowIcon(self.window_icon)

        self.graph = PlotCanvas(self,
                                data_queue=self.data_queue,
                                width=6,
                                height=4.1)
        self.graph.move(0,20)

        self.generate_connection_button()
        self.generate_acquire_button()
        self.generate_update_button()
        self.generate_save_button()
        self.generate_command_box()
        self.generate_command_button()
        self.generate_response_box()
        self.generate_persistance_checkbox()
        self.generate_mag_enable_checkbox()
        self.generate_phase_enable_checkbox()
        self.generate_menu_bar()

        self.acquire_button.setEnabled(False)
        self.update_button.setEnabled(False)
        self.save_button.setEnabled(True)

        self.show()

    def generate_menu_bar(self):
        self.main_menu = self.menuBar()
        self.file_menu = self.main_menu.addMenu('File')
        self.about_menu = self.main_menu.addMenu('About')

        self.generate_menu_save_button()
        self.generate_menu_exit_button()
        self.generate_menu_help_button()

    def generate_menu_save_button(self):
        self.save_button = QtWidgets.QAction(QIcon('exit24.png'),
                                            'Save As...',
                                            self)
        self.save_button.setShortcut('Ctrl+S')
        self.save_button.setStatusTip('Save As')
        self.save_button.triggered.connect(self.save_file_dialog)
        self.file_menu.addAction(self.save_button)

    def generate_menu_exit_button(self):
        self.exit_button = QtWidgets.QAction(QIcon('exit24.png'), 'Exit', self)
        self.exit_button.setShortcut('Ctrl+Q')
        self.exit_button.setStatusTip('Exit application')
        self.exit_button.triggered.connect(self.close)
        self.file_menu.addAction(self.exit_button)

    def generate_menu_help_button(self):
        self.help_button = QtWidgets.QAction(QIcon('exit24.png'), 'Help', self)
        self.help_button.setShortcut('Ctrl+H')
        self.help_button.setStatusTip('Help')
        self.help_button.triggered.connect(self.help_dialog)
        self.about_menu.addAction(self.help_button)

    def generate_connection_button(self):
        self.connect_button = QtWidgets.QPushButton('Connect', self)
        self.connect_button.setToolTip('Connect to a HP4195A Network Analyser')
        self.connect_button.move(600, 30)
        self.connect_button.resize(140, 100)
        self.connect_button.clicked.connect(self.connect)

    def generate_acquire_button(self):
        self.acquire_button = QtWidgets.QPushButton('Acquire Data', self)
        self.acquire_button.setToolTip('Acquire data from a HP4195A Network Analyser')
        self.acquire_button.move(600, 130)
        self.acquire_button.resize(140, 100)
        self.acquire_button.clicked.connect(self.start_acquisition)

    def generate_update_button(self):
        self.update_button = QtWidgets.QPushButton('Update', self)
        self.update_button.setToolTip('Update the display')
        self.update_button.move(600, 230)
        self.update_button.resize(140, 100)
        self.update_button.clicked.connect(self.update_plot)

    def generate_save_button(self):
        self.save_button = QtWidgets.QPushButton('Save', self)
        self.save_button.setToolTip('Save the data')
        self.save_button.move(600, 330)
        self.save_button.resize(140, 100)
        self.save_button.clicked.connect(self.save_file_dialog)

    def generate_command_box(self):
        self.command_box = QtWidgets.QLineEdit(self)
        self.command_box.move(140, 510)
        self.command_box.resize(440,30)
        self.command_box.textChanged.connect(self.toggle_connect_button)
        self.command_box_label = QtWidgets.QLabel('GPIB Command:', self)
        self.command_box_label.resize(120,30)
        self.command_box_label.move(10,510)

    def generate_command_button(self):
        self.command_button = QtWidgets.QPushButton('Send Command', self)
        self.command_button.move(590,510)
        self.command_button.resize(140,30)
        self.command_button.setToolTip('Send the GPIB command')
        self.command_button.clicked.connect(self.send_command)
        self.command_button.setEnabled(False)

    def generate_response_box(self):
        self.response_box = QtWidgets.QLineEdit(self)
        self.response_box.move(140, 550)
        self.response_box.resize(590,30)
        self.response_box_label = QtWidgets.QLabel('Response:', self)
        self.response_box_label.resize(120,30)
        self.response_box_label.move(10,550)

    def generate_persistance_checkbox(self):
        self.p_cb = QtWidgets.QCheckBox('Persist', self)
        self.p_cb.resize(100,30)
        self.p_cb.move(10, 450)
        self.p_cb.setToolTip('Set display to persist')
        self.p_cb.stateChanged.connect(self.change_persist_state)

    def generate_mag_enable_checkbox(self):
        self.mag_cb = QtWidgets.QCheckBox('Magnitude', self)
        self.mag_cb.toggle()
        self.mag_cb.resize(590,30)
        self.mag_cb.move(100, 450)
        self.mag_cb.setToolTip('Display magnitude data')
        self.mag_cb.stateChanged.connect(self.change_mag_state)

    def generate_phase_enable_checkbox(self):
        self.phase_cb = QtWidgets.QCheckBox('Phase', self)
        self.phase_cb.toggle()
        self.phase_cb.move(210, 450)
        self.phase_cb.setToolTip('Display phase data')
        self.phase_cb.stateChanged.connect(self.change_phase_state)

    def change_persist_state(self):
        if self.graph.persist:
            self.graph.persist = False
            self.mag_cb.setEnabled(True)
            self.phase_cb.setEnabled(True)
            self.logger.info('Persistence: Disabled')
        else:
            self.graph.persist = True
            self.mag_cb.setEnabled(False)
            self.phase_cb.setEnabled(False)
            self.logger.info('Persistence: Enabled')

    def change_mag_state(self):
        if self.graph.magnitude:
            self.graph.magnitude = False
            self.logger.info('Magnitude: Disabled')
            self.graph.plot()
        else:
            self.graph.magnitude = True
            self.logger.info('Magnitude: Enabled')
            self.graph.plot()

    def change_phase_state(self):
        if self.graph.phase:
            self.graph.phase = False
            self.logger.info('Phase: Disabled')
            self.graph.plot()
        else:
            self.graph.phase = True
            self.logger.info('Phase: Enabled')
            self.graph.plot()

    def toggle_connect_button(self):
        if len(self.command_box.text()) > 0 and self.connected:
            self.command_button.setEnabled(True)
        else:
            self.command_button.setEnabled(False)

    def connect(self):
        if self.connected:
            self.logger.info('Disconnecting from HP4195A')
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            self.command_queue.put('disconnect')
            self.logger.info('Command queue size = {}'.format(self.command_queue.qsize()))
            if self.message_queue.get():
                self.logger.info('Message queue size = {}'.format(self.message_queue.qsize()))
                self.logger.info('Successfully disconnected from HP4195A')
                QtWidgets.QApplication.restoreOverrideCursor()
                self.connect_button.setText("Connect")
                self.acquire_button.setEnabled(False)
                self.connected = False
            else:
                self.logger.info('Disconnection from HP4195 failed')
        else:
            self.logger.info('Attempting to connect to HP4195A')
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            self.command_queue.put('connect')
            self.logger.info('Command queue size = {}'.format(self.command_queue.qsize()))
            if self.message_queue.get():
                self.logger.info('Message queue size = {}'.format(self.message_queue.qsize()))
                self.logger.info('Successfully connected to HP4195A')
                QtWidgets.QApplication.restoreOverrideCursor()
                self.connect_button.setText("Disconnect")
                self.acquire_button.setEnabled(True)
                self.connected = True
            else:
                self.logger.info('Connection to HP4195 failed')

    def start_acquisition(self):
        self.logger.info('Starting data acquisition')
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.acquire_button.setEnabled(False)
        self.command_queue.put('start_acquisition')
        self.logger.info('Command queue size = {}'.format(self.command_queue.qsize()))
        reply = self.message_queue.get()
        self.logger.info('Message queue size = {}'.format(self.message_queue.qsize()))
        if reply:
            self.logger.info('Successfully acquired data')
            QtWidgets.QApplication.restoreOverrideCursor()
            self.update_button.setEnabled(True)
            self.save_button.setEnabled(True)
        else:
            self.logger.info('Data acquisition failed')
            self.acquire_button.setEnabled(True)

    def update_plot(self):
        self.logger.info('Updating plot')
        self.graph.plot()
        # TODO: check plot updated OK
        self.update_button.setEnabled(False)
        self.acquire_button.setEnabled(True)

    def send_command(self):
        command = self.command_box.text()
        self.command_queue.put('send_command')
        self.logger.info('Command queue size = {}'.format(self.command_queue.qsize()))
        self.command_queue.put(command)
        self.logger.info('Command queue size = {}'.format(self.command_queue.qsize()))
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        response = self.data_queue.get()
        self.logger.info('Data queue size = {}'.format(self.data_queue.qsize()))
        if len(response) > 0:
            QtWidgets.QApplication.restoreOverrideCursor()
            self.response_box.setText('{}: {}'.format(command, response))
            self.command_box.setText('')

    def save_file_dialog(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(self,"Save File","","All Files (*);;Text Files (*.txt);;CSV Files (*.csv)", options=options)
        if file_name:
            self.save_file(file_name)

    def save_file(self, file_name):
        file_name = file_name +'.csv'
        self.logger.info('Saving data to: {}'.format(file_name))
        rows = zip(self.graph.freq_data,
                   self.graph.mag_data,
                   self.graph.phase_data)
        with open(file_name, "w") as output:
            writer = csv.writer(output, lineterminator='\n')
            writer.writerow(['Frequency', 'Magnitude', 'Phase'])
            for row in rows:
                writer.writerow(row)

    def help_dialog(self):
        help_window = Help_Window()
        help_window.exec_()

    def closeEvent(self, event):
        if True:
            if self.connected:
                self.connect()
            event.accept()
        else:
            event.ignore()


class PlotCanvas(FigureCanvas):
    '''
    This class is for the figure that displays the data, it reads data off the data queue and updates the graph depending on the settings.
    '''
    def __init__(self,
                 parent=None,
                 data_queue=None,
                 width=5,
                 height=4,
                 dpi=100):
        self.data_queue = data_queue
        self.persist = False
        self.magnitude = True
        self.phase = True
        self.freq_data = range(1, 100)
        self.mag_data = [0 for i in range(1, 100)]
        self.phase_data = [0 for i in range(1, 100)]
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.mag_ax = self.fig.add_subplot(111)
        self.phase_ax = self.mag_ax.twinx()

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.plot()

    def plot(self):
        if self.persist == False:
            self.mag_ax.clear()
            self.phase_ax.clear()

        if self.data_queue.qsize():
            self.mag_data = self.data_queue.get()
            self.phase_data = self.data_queue.get()
            self.freq_data = self.data_queue.get()

        self.mag_ax.set_ylabel('Magnitude (dB)')
        self.phase_ax.set_ylabel('Phase (deg)')
        self.mag_ax.set_xlabel('Frequency (Hz)')
        self.phase_ax.set_xlim(np.min(self.freq_data),                                                 np.max(self.freq_data))
        self.phase_ax.set_ylim(np.min(self.phase_data)-20,                                             np.max(self.phase_data)+20)
        self.mag_ax.set_xlim(np.min(self.freq_data), np.max(self.freq_data))
        self.mag_ax.set_ylim(np.min(self.mag_data)-20,                                               np.max(self.mag_data)+20)

        if self.magnitude == True:
            self.mag_ax.grid(color='0.9', linestyle='--', linewidth=1)
            self.mag_ax.semilogx(self.freq_data, self.mag_data, 'b')

        if self.phase == True:
            self.phase_ax.grid(color='0.9', linestyle='--', linewidth=1)
            self.phase_ax.semilogx(self.freq_data, self.phase_data, 'r')

        self.fig.tight_layout()
        self.draw()

class Help_Window(QtWidgets.QDialog):
    '''
    This class is for the help window that displays the readme file to the user, it reads the readme file and displays the information as html using the markdown syntax.
    '''
    def __init__(self):
        super(Help_Window, self).__init__()
        self.setWindowTitle("Help")
        self.setWindowIcon(QIcon('hp_icon.png'))
        self.view = QtWebEngineWidgets.QWebEngineView(self)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.view)
        self.file = QtCore.QFile('README.md')
        if not self.file.open(QtCore.QIODevice.ReadOnly):
            QtGui.QMessageBox.information(None, 'info', self.file.errorString())
        self.stream = QtCore.QTextStream(self.file)
        self.html = markdown.markdown(self.stream.readAll())

        self.view.setHtml(self.html)
