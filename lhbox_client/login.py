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
        self.sock.send((header + ' ' + self.username + ' ' + self.password))
        res = self.sock.recv(1024)
        if res == 'fail':
            return 'fail'
        elif res == 'success':
            if self.username == 'jingxiong':
                return '/home/simon/Documents/devilbox'
            elif self.username == 'xinlu':
                return '/home/simon/Documents/devilbox2'
        
  
                
