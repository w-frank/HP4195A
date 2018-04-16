import telnetlib
import numpy as np
import sys
import matplotlib.pyplot as plt

def send_cmd(command):
    cmd = command + '\r\n'
    print('SENT: ', cmd)
    tn.write(cmd.encode('ascii'))

def send_query(command):
    cmd = command + '\r\n'
    print('SENT: ', cmd)
    tn.write(cmd.encode('ascii'))
    raw_data = tn.read_until(b'\r\n').decode('ascii')
    print('RECEIVED:', len(raw_data), 'OF', type(raw_data))
    data = np.fromstring(raw_data, dtype=float, sep=',')
    return data

HOST = 'bi-gpib-01.dyndns.cern.ch'
PORT = '1234'
GPIB_ADDR = 11

tn = telnetlib.Telnet(HOST, PORT)

send_query('++ver')
send_cmd('++auto 1')
data = send_query('A?')

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(data, 'k')
ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Magnitude (dB)')
plt.show()
