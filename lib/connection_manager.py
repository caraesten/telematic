import serial
import subprocess
import threading
import time
from telnetlib import Telnet

class ConnectionManager:
    def __init__(self, config):
        self.hosts = config['telnet_hosts']
        self.serial_path = config['serial_path']
        self.baud = config['baud_rate']
        self.read_size = config['max_read_size']
        self.is_running = False
    
    def connect(self):
        self.serial_connection = serial.Serial(self.serial_path, self.baud, timeout=1)
        self._main_loop()

    def _main_loop(self):        
        self._wait_for_go()
        continue_execution = self._select_active_host()
        if continue_execution:
            self._begin_telnet()
            while self.is_running:
                time.sleep(5)
            print("\nServer disconnected, restarting.\n")
        self._main_loop()

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
                self.serial_connection.write("\r\n\Server Disconnected!\n".encode("ascii"))
                is_connected = False
        self.telnet_connection.close()
        self.is_running = False
    
    def _select_active_host(self):
        option = 0
        for host in self.hosts:
            self.serial_connection.write(b'\n\r')
            opt_string = "%d> %s" % (option, host)
            self.serial_connection.write(opt_string.encode("ascii"))
        self.serial_connection.write(b'\n\rQ> Quit')
        self.serial_connection.write(b'\n\r#>')
        selection = b''
        while selection == b'':
            selection = self.serial_connection.read(1)
        if selection == b'Q':
            self.serial_connection.write(b'\033cPRESS ENTER TO START!')
            return False
        try:
            self.active_host = self.hosts[int(selection)]
        except:
            self.serial_connection.write(b'\n\r')
            self.serial_connection.write("ERROR! Try again.".encode('ascii'))
            self._select_active_host()
        return True

    def _begin_telnet(self):
        connection_msg = "\033c connecting to: %s" % (self.active_host)
        self.serial_connection.write(connection_msg.encode('ascii'))
        self.telnet_connection = Telnet(self.active_host)
        self.is_running = True
        data_forwarding = threading.Thread(target = self._forward_data)
        data_forwarding.start()
