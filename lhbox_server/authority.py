from database import Mydb

class Authority(object):
    def __init__(self,username):
        self.username = username
        self.audb = Mydb('localhost',27017)
        self.audb.use('devilbox')
        self.audb.setCollection(self.username+'_au')
        self.budb = Mydb('localhost',27017)
        self.budb.use('devilbox')
        self.budb.setCollection('bucket')

    def add_bucket(self,dir_name,bucket):
        self.audb.insert({'dir_name':dir_name,'bucket':bucket})
        self.budb.insert({'bucket':bucket,'users':[self.username]})
        
    def remove_bucket(self,dir_name):
        #result is dict
        bucket = self.audb.find_one({'dir_name':dir_name})['bucket']
        #self.audb.remove({'dir_name':dir_name})
        #users is list
        users = self.budb.find_one({'bucket':bucket})['users']
        users.remove(self.username)
        if len(users) == 0:
            self.budb.remove({'bucket':bucket})
        else:
            self.budb.update({'bucket':bucket},{'users':users})

    def remove_dir(self,bucket):
        self.audb.remove({'bucket':bucket})
    
    

    def find_bucket(self,dir_name):
        bucket = self.audb.find_one({'dir_name':dir_name})
        if bucket == None:
            print('Can not find bucket.')
            return None
        else:
            bucket = bucket['bucket']
            return bucket
        

    def share_bucket(self,bucket):
        dir_name = bucket.split('-')[-1]
        #shared directory will be in the root directory
        self.audb.insert({'dir_name':dir_name, 'bucket':bucket})
        users = self.budb.find_one({'bucket':bucket})['users']
        users.append(self.username)
        self.budb.update({'bucket':bucket},{'users':users})

    def inherit_bucket(self,old_bucket,new_bucket):
        old_dir_name = self.audb.find_one({'bucket':old_bucket})['dir_name']
        dir_name = new_bucket.split('-')[-1]
        new_dir_name = old_dir_name+'/'+dir_name
        #shared directory will be in the root directory
        self.audb.insert({'dir_name':new_dir_name, 'bucket':new_bucket})
        users = self.budb.find_one({'bucket':new_bucket})['users']
        users.append(self.username)
        self.budb.update({'bucket':new_bucket},{'users':users})

        
    def find_sharer(self,bucket,username):
        print('username: '+username)
        sharer = []
        users = self.budb.find_one({'bucket':bucket})
        if users == None:
            print sharer
            return sharer
        users = users['users']
        print('users:')
        print users
        try:users.remove(username)
        except ValueError:
            print('find sharer')
        
        sharer = users
        print('sharer:')
        print sharer
        return sharer
        
        
    def find_dir(self, bucket):
        dir_name = self.audb.find_one({'bucket':bucket})['dir_name']
        return dir_name
        
    def print_database(self):
        self.audb.print_database()
        self.budb.print_database()

def test():
    myau = Authority('jingxiong')
    myau.print_database()
    myau2 = Authority('xinlu')
    myau2.print_database()


if __name__ == '__main__':
    test()
