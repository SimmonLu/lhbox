import os

class logIN(object):
    def __init__(self, username, password, sock, lors):
        self.username = username
        self.password = password
        self.pathList = ''
        header = ''
        if lors == 'l':
            header = 'log'
        elif lors == 's':
            header = 'sign'
        sock.send((header + ' ' + username + ' ' + password))
        res = sock.recv()
        if res == 'fail':
            return 'fail'
        elif res == 'success':
            return self.checkIN()

    def checkIN(self):
        self.pathList = '/home/seven79/Desktop/590final/test_watch'
        return self.pathList
  
                
