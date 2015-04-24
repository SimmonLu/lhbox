from database import mydb
from register import register
import os
import socket


class server:      
    def __init__(self, ip='127.0.0.1', port=8000):          
        self.ip = ip  
        self.port = port  
        print('DevilBox server created.')
      
    def start(self):          
        print("DevilBox server start({0}:{1})...".format(self.ip, self.port))  
                  
        ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # ss.settimeout(1000 * 10)  
        ss.bind((self.ip, self.port))  
        ss.listen(5)  
          
        while True:  
            (client, address) = ss.accept()
            handler = client_handler()
            handler.setConnect(client)  
            handler.setDaemon(True)
            handler.start()  
        ss.close()  
        print(self.server_type + "Server close, bye-bye.") 
  

def main():

if __name__ == '__main__':
    main()
