__author__ = 'sanps'

import serial
import serial.tools.list_ports

ports = list(serial.tools.list_ports.comports())

# print ports

port_loc = None

for p in ports:
    if "2341" in p[2].lower():
        port_loc = p[0]
        break

print port_loc
