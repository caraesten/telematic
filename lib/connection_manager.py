import serial
import subprocess
import threading
from telnetlib import Telnet

class ConnectionManager:
    def __init__(self, config):
        self.host = config['telnet_host']
        self.serial_path = config['serial_path']
        self.baud = config['baud_rate']
        self.read_size = config['max_read_size']

        self.data_forwarding = threading.Thread(target = self._forward_data)
    
    def connect(self):
        self.serial_connection = serial.Serial(self.serial_path, self.baud, timeout=1)
        self._wait_for_go()
        self._begin_telnet()

    def _wait_for_go(self):
        ready_for_start = False
        while not ready_for_start:
            if self.serial_connection.read() == b'\r':
                ready_for_start = True
    
    def _forward_data(self):
        is_connected = True
        while is_connected:
            try:
                data = self.serial_connection.read()
                tel_data = self.telnet_connection.read_eager()
                self.telnet_connection.write(data)
                self.serial_connection.write(tel_data.replace(b'\n',b'\n\r'))
                self.serial_connection.flush()
            except EOFError:
                self.serial_connection.write("\n\Server Disconnected!\n".encode("ascii"))
                is_connected = False
                
    def _begin_telnet(self):
        connection_msg = "\033c connecting to: %s" % (self.host)
        self.serial_connection.write(connection_msg.encode('ascii'))
        self.telnet_connection = Telnet(self.host)
        self.data_forwarding.start()
