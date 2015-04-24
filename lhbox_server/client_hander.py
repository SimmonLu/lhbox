import threading
from register import register

class client_handler(threading.Thread):  
    def __init__(self, name):
        threading.Thread.__init__(self)

    def setConnect(self, connect):  
        self.connect = connect  
      
    def run(self):
        #receive login or sign up request from client
        while True:
            res = login_and_signup()
            if res = 'OK':
                break
            elif res = 'EXIT':
                self.connect.close()
                return
            
         while True:
             
        

    def login_and_signup(self):
        msg = self.connect.recv(1024)
        msg = msg.split()
        if msg[0] == 'exit':
            return 'EXIT'
        username = msg[1]
        password = msg[2]
        myreg = register()
        if msg[0] == 'log':
            if myreg.login(username,password) == True:
                self.username = username
                self.connect.send('success')
                return 'OK'
            else:
                self.connect.send('fail')
                return 'FAIL'
        elif msg[0] == 'sign':
            if myreg.sign_up(username,password) == True:
                self.username = username
                self.connect.send('success')
                return 'OK'
            else:
                self.connect.send('fail')
                return 'FAIL'
        
                
            
