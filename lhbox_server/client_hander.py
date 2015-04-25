import threading
from register import Register
from s3 import S3
from authority import Authority
from task_queue import Task_Queue
import socket

class Client_handler(threading.Thread):  
    def __init__(self):
        threading.Thread.__init__(self)
        self.s3 = S3()
        self.s3.connect()
        self.lock = threading.Lock()
        

    def setConnect(self, connect1):  
        self.connect1 = connect1  
      
    def run(self):
        #receive login or sign up request from client
        while True:
            res = login_and_signup()
            if res == 'OK':
                self.task_queue = Task_Queue(self.username)
                break
            elif res == 'EXIT':
                self.connect.close()
                return
        t1 = threading.Thread(target = self.action_from_sharer)
        t2 = threading.Thread(target = self.action_from_user)
        t1.setDaemon(True)
        t2.setDaemon(True)
        
        t1.start()
        t2.start()
        
        self.handle_task()
        
        

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
                self.au = Authority(self.username)
                #use username to create a root directory
                self.create_dir('.')
                self.connect.send('success')
                return 'OK'
            else:
                self.connect.send('fail')
                return 'FAIL'
        
    
    def create_dir(self,dir_name):
        if dir_name == '.':
            self.s3.create_bucket(self.username)
            self.au.add_bucket('.',self.username)
            return self.username
        elif dir_name != '':
            self.s3.create_bucket(self.username+'/'+dir_name)
            self.au.add_bucket(dir_name,self.self.username+'/'+dir_name)
            return self.username+'/'+dir_name
        else:
            print('dir_name is empty.')
            return None


            
    def handle_task(self):
        while True:
            self.lock.acquire()
            if not self.task_queue.empty():
                #task = {'action':action, 'source':source}
                task = self.task_queue.top()
            self.lock.release()
            
            self.do_task(task)
            
            

    def do_task(self,task):
        action_type = task['action'].type
        action_object = task['action'].object
        action_dir_name = task['action'].dir_name
        action_filename = task['action'].filename
        if task['source'] == 'self':
            if action_type == 'CRT':
                #create new directory, create a new bucket
                if action_object == 'D':
                    if action_dir_name == '.':
                        bucket = self.create_dir(action_filename)
                        self.connect1.send('upload D '+action_filename+' '+bucket)
                    else:
                        bucket =self.create_dir(action_dir_name+'/'+action_filename)
                        self.connect1.send('upload D '+action_dir_name+'/'+action_filename+' '+bucket)
                    response = self.connect1.recv(1024)
                    if response == 'ack':
                        self.task_queue.pop()                                
                elif action_object == 'F':
                    if action_dir_name == '.':
                        bucket = self.au.find_bucket(action_dir_name)
                        self.connect1.send('upload F '+action_filename+' '+bucket)
                    else:
                        bucket = self.au.find_bucket(action_dir_name)
                        self.connect1.send('upload F '+action_dir_name+'/'+action_filename+' '+bucket)
                
       
            elif action_type == 'MOD':
                #mod action's object must be file
                if action_dir_name == '.':
                    bucket = self.au.find_bucket(action_dir_name)
                    self.connect1.send('upload F '+action_filename+' '+bucket)
                else:
                    bucket = self.au.find_bucket(action_dir_name)
                    self.connect1.send('upload F '+action_dir_name+'/'+action_filename+' '+bucket)

        elif task['source'] == 'share':
            
            
            
            
        
            
                
    #receive action from user, push into task queue
    def action_from_user(self):
        ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #port 8001 is responsible for receiving request
        while True:
            action = self.connect2.recv(1024)
            print('Receive a request.')
            self.lock.acquire()
            if self.task_queue.push(action) == False:
                self.lock.release()
                self.connect2.send('conflict')
            else:
                self.lock.release()
                self.connect2.send('ok')
 
    #check if there is any task in database, if yes push into queue
    def action_from_sharer(self):
        while True:
            if self.task_queue.db_is_empty() == False:
                self.lock.acquire()
                self.task_queue.db_pop_to_queue()
                self.lock.release()

                
    

