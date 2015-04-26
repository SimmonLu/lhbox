import threading
from register import Register
from s3 import S3
from authority import Authority
from task_queue import Task_Queue, Action
import socket

access_key = 'AKIAJGCZ2F45AZJQ2UGA'
secret_key = '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'

class Client_handler(threading.Thread):  
    def __init__(self):
        threading.Thread.__init__(self)
        self.s3 = S3(access_key, secret_key)
        self.s3.connect()
        self.lock = threading.Lock()


    def setConnect(self, connect1, connect2):  
        self.connect1 = connect1  
        self.connect2 = connect2  

    def run(self):
        #receive login or sign up request from client
        while True:
            res = self.login_and_signup()
            if res == 'OK':
                self.task_queue = Task_Queue(self.username)
                break
            elif res == 'EXIT':
                self.connect1.close()
                self.connect2.close()
                return
        t1 = threading.Thread(target = self.action_from_sharer)
        t2 = threading.Thread(target = self.action_from_user)
        t1.setDaemon(True)
        t2.setDaemon(True)
        
        t1.start()
        t2.start()
        
        self.handle_task()

        

    def login_and_signup(self):
        msg = self.connect1.recv(1024)
        msg = msg.split()
        if msg[0] == 'exit':
            return 'EXIT'
        username = msg[1]
        password = msg[2]
        myreg = Register()
        if msg[0] == 'log':
            if myreg.login(username,password) == True:
                self.username = username
                self.au = Authority(self.username)
                self.connect1.send('success')
                return 'OK'
            else:
                self.connect1.send('fail')
                return 'FAIL'

        elif msg[0] == 'sign':
            if myreg.sign_up(username,password) == True:
                self.username = username
                #use username to create a root directory
                self.au = Authority(self.username)
                self.create_dir('.')
                self.connect1.send('success')
                return 'OK'
            else:
                self.connect1.send('fail')
                return 'FAIL'


    def create_dir(self,dir_name):
        print('enter create dir')
        if dir_name == '.':
            bucket = '590cloudcomputing-juehanbode-'+self.username 
            self.s3.create_bucket(bucket)
            self.au.add_bucket('.',bucket)
            return bucket
        elif dir_name != '':
            dir = dir_name.replace('/','-')
            bucket = '590cloudcomputing-juehanbode-'+self.username+'-'+dir
            self.s3.create_bucket(bucket)
            self.au.add_bucket(dir_name,bucket)
            return bucket
        else:
            print('dir_name is empty.')
            return None

    def delete_dir(self,dir_name):
        print('enter delete dir')
        bucket = self.au.find_bucket(dir_name)
        #remove authority first
        self.au.remove_bucket(dir_name)
        #delete bucket second

        
        
        


    def handle_task(self):
        while True:
            task = {}
            self.lock.acquire()
            if not self.task_queue.empty():
                #task = {'action':action, 'source':source}
                print('task queue is not empty')
                task = self.task_queue.top()
            self.lock.release()
            self.task_queue.print_task_queue()
            if len(task) != 0:
                self.do_task(task)
            
            

    def do_task(self,task):
        print('start ' + task['action'].str_action)
        curr_action = task['action']
        action_type = task['action'].type
        print action_type
        action_object = task['action'].object
        print action_object
        action_dir_name = task['action'].dir_name
        print action_dir_name
        action_filename = task['action'].filename
        print action_filename

        if task['source'] == 'self':
            if action_type == 'CRT' and action_object == 'D':
                #create new directory, create a new bucket
                if action_dir_name == '.':
                    bucket = self.create_dir(action_filename)# Notice: here is filename nor dir_name!!!!!!
                    self.connect1.send('upload D '+action_filename+' '+bucket)
                    print('send: '+'upload D '+action_filename+' '+bucket)
                else:
                    bucket = self.create_dir(action_dir_name+'/'+action_filename)
                    self.connect1.send('upload D '+action_dir_name+'/'+action_filename+' '+bucket)
                    print('send: '+'upload D '+action_dir_name+'/'+action_filename+' '+bucket)

            elif (action_type == 'CRT' or action_type == 'MOD') and action_object == 'F':
                if action_dir_name == '.':
                    bucket = self.au.find_bucket(action_dir_name)
                    self.connect1.send('upload F '+action_filename+' '+bucket)
                    print('send: '+'upload F '+action_filename+' '+bucket)
                else:
                    bucket = self.au.find_bucket(action_dir_name)
                    self.connect1.send('upload F '+action_dir_name+'/'+action_filename+' '+bucket)
                    print('send: '+'upload F '+action_dir_name+'/'+action_filename+' '+bucket)
       
            elif action_type == 'DEL':
                real_object = ''
                test_dir = curr_action.dir_for_dir()
                if self.au.find_bucket(test_dir) == None:
                    real_object = 'F'
                else:
                    real_object = 'D'
                print('real_object: '+real_object)
                curr_action.change_object(real_object)
                task['action'] = curr_action

                if real_object == 'D':
                    if action_dir_name == '.':
                        self.delete_dir(action_filename)
                        deleted_bucket = self.au.find_bucket(action_filename)
                        #delete bucket on s3
                        self.s3.delete_bucket(deleted_bucket)
                        
                    else:
                        self.delete_dir(action_dir_name+'/'+action_filename)
                        deleted_bucket = self.au.find_bucket(action_dir_name+'/'+action_filename)
                        #delete bucket on s3
                        self.s3.delete_bucket(deleted_bucket)
                elif real_object == 'F':
                    upper_bucket = self.au.find_bucket(action_dir_name)
                    #delete file on s3
                    self.s3.delfile(upper_bucket,action_filename)

                self.lock.acquire()
                self.task_queue.pop()
                self.lock.release()
                self.share_task(task)
                return

            response = self.connect1.recv(1024)
            if response == 'ACK':
                print('receive ack')
                self.lock.acquire()
                self.task_queue.pop()
                self.lock.release()
                self.share_task(task)

        elif task['source'] == 'share':
            if action_type == 'CRT' and action_object == 'D':
                #create new directory, create a new bucket
                if action_dir_name == '.':
                    bucket = self.au.find_bucket(action_filename)# Notice: here is filename nor dir_name!!!!!!
                else:
                    bucket =self.au.find_bucket(action_dir_name+'/'+action_filename)
                    
                self.connect1.send('download D '+action_dir_name+' '+bucket+' '+action_filename)
                print('send: '+'download D '+action_dir_name+' '+bucket+' '+action_filename)

            elif (action_type == 'CRT' or action_type == 'MOD') and action_object == 'F':
                bucket = self.au.find_bucket(action_dir_name)
                self.connect1.send('download F '+action_dir_name+' '+bucket+' '+action_filename)
                print('send: '+ 'download F '+action_dir_name+' '+bucket+' '+action_filename)
       
            elif action_type == 'DEL':


                if action_dir_name == '.':
                    self.connect1.send('delete '+action_object+' '+action_filename)
                    print('send: '+'delete '+action_object+' '+action_filename)
                    if action_object == 'D':
                        new_bucket = self.au.find_bucket(action_filename)
                        self.delete_dir(action_filename)
                        self.au.remove_dir(new_bucket)
                else:
                    self.connect1.send('delete '+action_object+' '+action_dir_name+'/'+action_filename)
                    print('send: '+'delete '+action_object+' '+action_dir_name+'/'+action_filename)
                    if action_object == 'D':
                        new_bucket = self.au.find_bucket(action_dir_name+'/'+action_filename)
                        self.delete_dir(action_dir_name+'/'+action_filename)                    
                        self.au.remove_dir(new_bucket)
                self.lock.acquire()
                self.task_queue.pop()
                self.lock.release()
                return

            response = self.connect1.recv(1024)
            if response == 'Download finished':
                while self.task_queue.check_conflict(curr_action) == False:
                    pass
                self.connect1.send('apply')
                self.lock.acquire()
                self.task_queue.pop()
                self.lock.release()
            
                
    #receive action from user, push into task queue
    def action_from_user(self):
        while True:
            action = self.connect2.recv(1024)
            #deal with share directory with other user
            print('receive: '+action)
            if action.split()[0] == 'SHR':
                self.share_directory(action)
                continue

            tmp_act = Action(action)
            self.lock.acquire()
            if self.task_queue.push(action) == False:

                self.connect2.send('conflict')
                response = self.connect2.recv(1024)
                if response == 'ok':
                    self.task_queue.delete_last()
                self.lock.release()                    
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

    def share_directory(self, action):
        action = action.split()
        dir_name = action[1]
        username = action[2]
        bucket = self.au.find_bucket(dir_name)
        myreg = Register()
        if myreg.user_exist(username) == False:
            print('User not exist.')
            self.connect2.send('User not exist.')
            return
        else:
            sharer_au = Authority(username)
            sharer_au.share_bucket(bucket)
            sharer_tq = Task_Queue(username)
            new_dir_name = sharer_au.find_dir(bucket)
            str_action = 'CRT D '+new_dir_name    
            action = Action(str_action)
            sharer_tq.db_push(action,'share')
            print('Share successfully')
            self.connect2.send('Share successfully.')

        
        
    

    def share_task(self,task):
        action_dir_name = task['action'].dir_name
        action_filename = task['action'].filename
        #find the upper level directory
        bucket = self.au.find_bucket(action_dir_name)
        sharer = self.au.find_sharer(bucket,self.username)
        #if action is create a directory,authorize the new 
        #directory to owner of upper level directory
        new_bucket = ''
        
        if task['action'].type != 'DEL':
            if task['action'].object == 'D':                
                if action_dir_name == '.':
                    new_bucket = self.au.find_bucket(action_filename)
                else:
                    new_bucket = self.au.find_bucket(action_dir_name+'/'+action_filename)
                #add authority
                for i in sharer:
                    sharer_au = Authority(i)
                    sharer_au.share_bucket(new_bucket)
                    sharer_tq = Task_Queue(i)
                    #change dir_name to new user's dir_name
                    new_dir_name = sharer_au.find_dir(new_bucket)
                    str_action = 'CRT D '+new_dir_name
                    action = Action(str_action)
                    sharer_tq.db_push(action,'share')
                
                
            elif task['action'].object == 'F':
                for i in sharer:
                    sharer_tq = Task_Queue(i)
                    sharer_au = Authority(i)
                    #change dir_name to new user's dir_name
                    new_dir_name = sharer_au.find_dir(bucket)
                    str_action = task['action'].change_dir(new_dir_name)
                    action = Action(str_action)
                    sharer_tq.db_push(action,'share')
        
        elif task['action'].type == 'DEL':
            if task['action'].object == 'D':                
                if action_dir_name == '.':
                    new_bucket = self.au.find_bucket(action_filename)
                else:
                    new_bucket = self.au.find_bucket(action_dir_name+'/'+action_filename)
  
                new_sharer = self.au.find_sharer(new_bucket,self.username)
                for i in new_sharer:
                    sharer_tq = Task_Queue(i)
                    #change dir_name to new user's dir_name
                    new_dir_name = sharer_au.find_dir(new_bucket)
                    str_action = 'DEL D '+new_dir_name
                    action = Action(str_action)
                    sharer_tq.db_push(action,'share')
                self.au.remove_dir(new_bucket)
                
                
            elif task['action'].object == 'F':
                for i in sharer:
                    sharer_tq = Task_Queue(i)
                    sharer_au = Authority(i)
                    #change dir_name to new user's dir_name
                    new_dir_name = sharer_au.find_dir(bucket)
                    str_action = task['action'].change_dir(new_dir_name)
                    action = Action(str_action)
                    sharer_tq.db_push(action,'share')
            
            

        
