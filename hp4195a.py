import sys
import os
import time
import telnetlib
import multiprocessing
import numpy as np
import logging
import logging.handlers
import numpy.core._methods
import numpy.lib.format


class hp4195a(multiprocessing.Process):
    def __init__(self, command_queue, message_queue, data_queue, logger_queue):
        super(hp4195a, self).__init__()
        self.command_queue = command_queue
        self.message_queue = message_queue
        self.data_queue = data_queue
        self.logging_queue = logger_queue

        self.mag_data = []
        self.phase_data = []
        self.freq_data = []

        self.host = 'bi-gpib-01.dyndns.cern.ch'
        self.port = '1234'
        self.gpib_addr = 11

        self.telnet_id = 'Prologix GPIB-ETHERNET Controller version 01.06.06.00'
        self.device_id = 'HP4195A'

    def run(self):
        '''
        This function will run when the class is launched as a separate
        process.
        '''
        self.qh = logging.handlers.QueueHandler(self.logging_queue)
        self.root = logging.getLogger()
        self.root.setLevel(logging.DEBUG)
        self.root.addHandler(self.qh)
        self.logger = logging.getLogger(__name__)

        while True:
            self.command = self.command_queue.get()
            self.logger.info('Received \"{}\" from GUI'.format(self.command))
            self.logger.info('Command queue size = {}'.format(self.command_queue.qsize()))

            if self.command == 'connect':
                self.logger.info('Connecting to HP4195A')
                self.telnet_connect()

            elif self.command == 'disconnect':
                self.logger.info('Disconnecting from HP4195A')
                self.telnet_disconnect()

            elif self.command == 'start_acquisition':
                self.logger.info('Starting data acquisition')
                if self.acquire_mag_data():
                    if self.acquire_phase_data():
                        if self.acquire_freq_data():
                            self.logger.info('Acquired data OK')
                        else:
                            self.logger.warning('Frequency data acquisition failed')
                            self.message_queue.put(False)
                    else:
                        self.logger.warning('Phase data acquisition failed')
                        self.message_queue.put(False)
                else:
                    self.logger.warning('Magnitude data acquisition failed')
                    self.message_queue.put(False)

                mag_check = len(self.mag_data) == len(self.freq_data)
                phase_check = len(self.phase_data) == len(self.freq_data)

                if mag_check and phase_check:
                    self.logger.info('Data length check passed ({}, {}, {})'.format(len(self.mag_data),len(self.phase_data),len(self.freq_data)))
                    self.message_queue.put(True)
                    self.data_queue.put(self.mag_data)
                    self.data_queue.put(self.phase_data)
                    self.data_queue.put(self.freq_data)
                    self.mag_data = []
                    self.phase_data = []
                    self.freq_data = []
                else:
                    self.logger.warning('Data length check failed ({}, {}, {})'.format(len(self.mag_data),len(self.phase_data),len(self.freq_data)))
                    self.message_queue.put(False)

            elif self.command == 'send_command':
                self.command =  self.command_queue.get()
                self.logger.info('Sending GPIB command: {}'.format(self.command))
                self.response = self.send_query(self.command)
                self.logger.info('Response: {}'.format(self.response))
                self.data_queue.put(self.response)

    def telnet_connect(self):
        self.logger.info('Starting Telnet communications')
        self.tn = telnetlib.Telnet(self.host, self.port)
        if self.send_query('++ver') == self.telnet_id:
            self.logger.info('Successfully established connection with {}'.format(self.telnet_id))
            self.init_device()
        else:
            self.tn.close()
            self.logger.warning('Failed to setup Telnet communications')
            self.message_queue.put(False)

    def telnet_disconnect(self):
        self.logger.info('Disconnecting Telnet connection')
        self.tn.close()
        self.message_queue.put(True)

    def init_device(self):
        self.logger.info('Querying HP4195A')
        if self.send_query('ID?') == self.device_id:
            self.logger.info('Successfully found {}'.format(self.device_id))
            self.logger.info('Initialising HP4195A')
            self.send_command('++auto 1')
            self.message_queue.put(True)
        else:
            self.tn.close()
            self.logger.warning('Error unrecognised device')
            self.message_queue.put(False)

    def acquire_mag_data(self):
        raw_mag_data = self.send_query('A?')
        mag_data = np.fromstring(raw_mag_data, dtype=float, sep=',')
        if len(mag_data) > 0:
            self.mag_data = mag_data
            return True

    def acquire_phase_data(self):
            raw_phase_data = self.send_query('B?')
            phase_data = np.fromstring(raw_phase_data, dtype=float, sep=',')
            if len(phase_data) > 0:
                self.phase_data = phase_data
                return True

    def acquire_freq_data(self):
        raw_freq_data = self.send_query('X?')
        freq_data = np.fromstring(raw_freq_data, dtype=float, sep=',')
        if len(freq_data) > 0:
            self.freq_data = freq_data
            return True

    def send_command(self, command):
        cmd = command + '\r\n'
        self.logger.info('Sent \"{}\"'.format(cmd.rstrip()))
        self.tn.write(cmd.encode('ascii'))

    def send_query(self, command):
        self.send_command(command)
        data = ['init']
        response = []
        while data != []:
            raw_data = self.tn.read_until(b'\r\n', timeout=3).decode('ascii')
            self.logger.info('Received {} of {}'.format(len(raw_data), type(raw_data)))
            #raw_data = self.tn.read_until(b'EOF', timeout=4).decode('ascii')
            data = raw_data.splitlines()
            if data != []:
                response.append(data[0])

        if len(response) > 0:
            ret = response[0]
        else:
             ret = 'Command failed'
        return ret
