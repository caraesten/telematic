import json, os
import time
from lib.connection_manager import ConnectionManager

CONFIG_PATH = "telematic.json"

if __name__ == '__main__':
    config_f = open(CONFIG_PATH, 'r')
    config = json.load(config_f)

    connection = ConnectionManager(config)
    connection.connect()
    
    print("Connecting...")
    while True:
        # idk maybe just check status periodically on bg threads
        time.sleep(5)
