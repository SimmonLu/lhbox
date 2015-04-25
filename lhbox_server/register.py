from database import Mydb

class Register(object):
    def __init__(self):
        self.regdb = Mydb('localhost',27017)
        self.regdb.use('devilbox')
        self.regdb.setCollection('register')
    

    def sign_up(self, username, password):
        if self.regdb.exist({'username':username}) == True:
            print('Sign up fail: User already exists.')
            return False
        else:
            self.regdb.insert({'username':username, 'password': password})
            print(username + ' sign up successfully.')
            return True
    
    def login(self, username, password):
        if self.regdb.exist({'username':username}) == False:
            print('Login fail: User not exist')
            return False
        else:
            result = self.regdb.find_one({'username':username})
            if result['password'] != password:
                print('Login fail: Incorrect password.')
                return False
            else:
                print(username + ' login successfully')
                return True
                
    def user_exist(self,username):
        if self.regdb.exist({'username':username}) == False:
            return False
        else:
            return True
        
    def delete_user(self, username):
        if self.regdb.exist({'username':username}) == False:
            print('Delete user fail: user not exist.')
            return False
        else:
            self.regdb.remove({'username':username})
            print('Delete user:' + username + ' successfully.')
        
    def print_database(self):
        self.regdb.print_database()

def test():
    myreg = Register()
    myreg.delete_user('jingxiong')
    myreg.print_database()
    
if __name__ == '__main__':
    test()
