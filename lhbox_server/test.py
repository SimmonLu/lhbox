import time
import threading

class test(object):
    def __init__(self):
        self.data = 10
    
    def write(self):
        while True:
            self.data += 1
            time.sleep(3)
        
    def print_data(self):
        tt = threading.Thread(target = self.write)
        tt.setDaemon(True)
        tt.start()
        while True:
            print('data = '+str(self.data))
            time.sleep(3)
        

def main():
    list = [1,2]
    try: list.remove(3)
    except ValueError:
        print('it is ok')
    print(list)
    
        

if __name__ == '__main__':
    main()
        
