from database import Mydb
import string

class Task_Queue(object):
    def __init__(self,username):
        self.username = username
        self.tqdb = Mydb('localhost',27017)
        self.tqdb.use('devilbox')
        self.tqdb.setCollection(username+'_tq')
        #a temporary task queue stored in memory
        self.task_queue = [] #[{'action':action,'source':'self'}]

    #check if the task queue in db is empty
    def db_is_empty(self):
        if self.tqdb.count() == 0:
            return True
        else:
            return False
            
    #insert task into user's task queue database
    def db_push(self,action,source):
        self.tqdb.insert({'action':action.str_action,'source':source})
    
    def db_pop_to_queue(self):
        result = self.tqdb.find()
        for i in result:
            tmp_act = Action(i['action'])
            source = i['source']
            self.task_queue.append({'action':tmp_act,'source':source}) 
            self.tqdb.remove(i)

    
            
    
    #push a action into task queue    
    def push(self, action):
        act = Action(action)
        if len(filter(lambda x: x['action'].is_same(act) == True and x['source'] == 'share', self.task_queue)) == 0:
            self.task_queue.append({'action':act,'source':'self'})
            return True
        else:
            self.task_queue.append({'action':act,'source':'conflict'})
            return False
    
    def check_conflict(self,action):
        if len(filter(lambda x: x['action'].is_same(action) == True and x['source'] == 'conflict', self.task_queue)) == 0:
            return True
        else:
            return False

    def delete_last(self):
        self.task_queue.pop()
        

    #pop a task out of the queue
    def pop(self):
        if len(self.task_queue) != 0:
            self.task_queue.pop(0)
            return True
        else:
            print('Pop fail: Task queue is empty.')
            return False

    def top(self):
        if not self.empty():
            return self.task_queue[0]
        else:
            print('Top fail: Task queue is empty.')
            return None
            
        
    #test whether the queue is empty
    def empty(self):
        if len(self.task_queue) == 0:
            return True
        else:
            return False
    #print the whole task queue
    def print_task_queue(self):
        for i in self.task_queue:
            print(i['action'].type,i['action'].object,i['action'].dir_name,i['action'].filename, i['source'])

    def print_database(self):
        self.tqdb.print_database()

class Action(object):
    def __init__(self,raw_action):
        #raw_action is a string
        self.str_action = raw_action
        raw_action = raw_action.split()
        self.type = raw_action[0]
        self.object = raw_action[1] 
        if len(raw_action[2].split('/')) == 1:
            self.dir_name = '.'
            self.filename = raw_action[2]
        else:   
            self.dir_name = raw_action[2][:string.rfind(raw_action[2],'/')]
            self.filename = raw_action[2][string.rfind(raw_action[2],'/')+1:]
    
    def is_same(self,action):
        if self.type == action.type and self.dir_name == action.dir_name and self.filename == action.filename:
            return True
        else:
            return False
            
    def dir_for_dir(self):
        if self.dir_name == '.':
            return self.filename
        else:
            return self.dir_name+'/'+self.filename

    def dir_for_file(self):
        return self.dir_name
            
    def change_dir(self,dir_name):
        return self.type+' '+self.object+' '+dir_name+' '+self.filename
        
    def change_object(self,object):
        self.object = object
        dir = self.dir_for_dir()
        self.raw_action = self.type+' '+self.object+' '+dir
    


def test():
    mytq = Task_Queue('jingxiong')
    mytq2 =Task_Queue('xinlu')
    mytq.print_database()
    mytq2.print_database()
        

if __name__ == '__main__':
    test()
