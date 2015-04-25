from database import Mydb
from client_handler import Client_handler
import os
import socket


class server:      
    def __init__(self, ip='127.0.0.1', port1=8000, port2=8001):         
        self.ip = ip  
        self.port1 = port1  
        self.port2 = port2  
        print('DevilBox server created.')
      
    def start(self):          
        print("DevilBox server start({0}:{1}:{2})...".format(self.ip, self.port1, self.port2))  
                  
        s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # ss.settimeout(1000 * 10)  
        s1.bind((self.ip, self.port1))  
        s2.bind((self.ip, self.port2))  
        s1.listen(5)  
        s2.listen(5)  
          
        while True:  
            (client1, address1) = s1.accept()
            (client2, address2) = s2.accept()
            handler = Client_handler()
            handler.setConnect(client1,client2)  
            handler.setDaemon(True)
            handler.start()  
        ss.close()  
        print(self.server_type + "Server close, bye-bye.") 
  

def main():
    devilbox_server = server('127.0.0.1',8000,8001)
    devilbox_server.start()

if __name__ == '__main__':
    main()
