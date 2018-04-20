import sys
import os
import telnetlib
import time
import multiprocessing
import numpy as np
import numpy.core._methods
import numpy.lib.format


class hp4195a(multiprocessing.Process):
    def __init__(self, command_queue, data_queue):
        super(hp4195a, self).__init__()
        self.command_queue = command_queue
        self.data_queue = data_queue
        self.host = 'bi-gpib-01.dyndns.cern.ch'
        self.port = '1234'
        self.gpib_addr = 11
        self.id = 'Prologix GPIB-ETHERNET Controller version 01.06.06.00'

    def run(self):
        '''
        This function will run when the class is launched as a separate
        process.
        '''

        while True:
            command = self.command_queue.get()
            print('TELNET: received', command, 'from gui')
            print('TELNET: command queue size = ', self.command_queue.qsize())
            sys.stdout.flush()

            if command == 'connect':
                print('TELNET: connecting...')
                sys.stdout.flush()
                self.telnet_connect()

            elif command == 'disconnect':
                self.telnet_disconnect()

            elif command == 'start_acquisition':
                print('TELNET: starting acquisition')
                sys.stdout.flush()
                self.acquire_mag_data()
                self.acquire_freq_data()

    def telnet_connect(self):
        self.tn = telnetlib.Telnet(self.host, self.port)
        if self.send_query('++ver') == self.id:
            self.init_device()
        else:
            print('TELNET: error connecting to HP4195A.')
            sys.stdout.flush()

    def init_device(self):
        print('TELNET: initialising HP4195A')
        sys.stdout.flush()
        self.send_command('++auto 1')

    # def disconnect(self):

    def acquire_mag_data(self):
        raw_mag_data = self.send_query('A?')
        mag_data = np.fromstring(raw_mag_data, dtype=float, sep=',')
        sys.stdout.flush()
        self.data_queue.put(mag_data)
        print('TELNET: data queue size = ', self.data_queue.qsize())
        sys.stdout.flush()
        #self.command_queue.put(True)
        #print('TELNET: command queue size = ', self.command_queue.qsize())
        sys.stdout.flush()

    def acquire_freq_data(self):
        raw_freq_data = self.send_query('X?')
        freq_data = np.fromstring(raw_freq_data, dtype=float, sep=',')
        #sys.stdout.flush()
        self.data_queue.put(freq_data)
        print('TELNET: data queue size = ', self.data_queue.qsize())
        #sys.stdout.flush()

    def send_command(self, command):
        cmd = command + '\r\n'
        print('TELNET: sent', cmd.rstrip())
        sys.stdout.flush()
        self.tn.write(cmd.encode('ascii'))

    def send_query(self, command):
        cmd = command + '\r\n'
        print('TELNET: sent', cmd.rstrip())
        sys.stdout.flush()
        self.tn.write(cmd.encode('ascii'))
        raw_data = self.tn.read_until(b'\r\n').decode('ascii')
        print('TELNET: received', len(raw_data), 'of', type(raw_data))
        sys.stdout.flush()
        # remove trailing newline and carriage return
        return raw_data.rstrip()

#data = np.fromstring(raw_data, dtype=float, sep=',')
#print(data)
#sys.stdout.flush()
