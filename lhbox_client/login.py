import os
import socket

class logIN(object):
    def __init__(self, username, password, sock, lors):
        self.username = username
        self.password = password
        self.pathList = ''
        self.login_or_sign = lors
        self.sock = sock

    def checkIN(self):
        header = ''
        if self.login_or_sign == 'l':
            header = 'log'
        elif self.login_or_sign == 's':
            header = 'sign'
        else:
            return 'wrong_input'
        self.sock.send((header + ' ' + self.username + ' ' + self.password))
        res = self.sock.recv(1024)
        if res == 'fail':
            return 'fail'
        elif res == 'success':
            if self.username == 'user1':
                return '/home/simon/Desktop/devilbox'
            elif self.username == 'user2':
                return '/home/simon/Desktop/devilbox2'
        
  
                
