import pyinotify
import Queue
import threading
import time
import socket
import os
import shutil
from string import replace
from login import logIN
from s3 import S3


eventToSend = []
eventList = []
mutex = threading.Lock()
mutex_s = threading.Lock()
wm = pyinotify.WatchManager()
fileToRemove = -1
username = ''
root = ''


class MyEventHandler(pyinotify.ProcessEvent):

    def process_IN_MOVE_SELF(self, event):
        print "MOVE_SELF",str(event.pathname)

    def process_IN_MOVED_TO(self, event):
        mutex.acquire()
        print "MVT",str(event.pathname)
        #print "MOVED_TO event:", event.wd
        eventList.append(("MVT",str(event.pathname)))
        mutex.release()

    def process_IN_MOVED_FROM(self, event):
        mutex.acquire()
        #print "MOVED_FROM event:", event.pathname
        print "MVF",str(event.pathname)
        eventList.append(("MVF",str(event.pathname)))
        mutex.release()

    def process_IN_DELETE(self, event):
        mutex.acquire()
        #print "DELETE event:", event.pathname
        print "DEL",str(event.pathname)
        eventList.append(("DEL",str(event.pathname)))
        mutex.release()

    def process_IN_MODIFY(self, event):
        mutex.acquire()
        print "MOD",str(event.pathname)
        if len(eventList):
            eventList.pop(0)
        if len(eventList):
            eventList.pop(0)
        eventList.append(("MOD",str(event.pathname)))
        mutex.release()

def foo(notifier):
    global fileToRemove
    if fileToRemove != -1:
        #notifier._watch_manager.rm_watch(fileToRemove)
        print 'rmwatch',  fileToRemove
        fileToRemove = -1
    return False

def watch_manager(name, directory):
    #wm = pyinotify.WatchManager()
    mask = pyinotify.IN_DELETE | pyinotify.IN_MODIFY | pyinotify.IN_MOVED_TO | pyinotify.IN_MOVED_FROM | pyinotify.IN_MOVE_SELF
    wm.add_watch(directory, mask, rec=True, auto_add = True)
    # event handler
    eh = MyEventHandler()
    # notifier
    notifier = pyinotify.Notifier(wm, eh)
    print "watch_manager starts"
    notifier.loop(foo)


class eventReader(object):
    
    def __init__(self):
        print "eventHandler starts"
    def pEvent(self):
        mutex.acquire()
        print eventList.pop(0)
        mutex.release()
    def checkHide(self, path):
        sections = path.split('/')
        if sections[-1][0] == '.':
            return True
        else:
            return False
    def checkRename(self):
        print "eventList in checkRename:"
        print eventList
        if len(eventList) < 2:
            return False
        currEvent = eventList[0]
        nextEvent = eventList[1]
        if nextEvent[0] != 'MVT':
            return False
        
        Currs = currEvent[1].split('/')
        Nexts = nextEvent[1].split('/')
        lastCurr = Currs[-1] 
        lastNext = Nexts[-1]
        remain = nextEvent[1].replace(currEvent[1], "")
        if remain[:9] == '_conflict':
            eventList.pop(0)
            return True
        elif lastCurr == '.' +  lastNext:
            eventList.pop(0)
            return True
        else:
            return False

    def checkCreate(self, path):
        sections = path.split('/')
        if sections[-1] == 'Untitled Folder':
            return True
        else:
            return False

    def checkPathHide(self, path):
        sections = path.split('/')
        for sect in sections:
            if sect == '':
                continue
            if sect[0] == '.':
                return True
        return False

    def parseEvent(self):
        global fileToRemove
        global eventToSend
        mutex_s.acquire()
        mutex.acquire()
        if len(eventList) == 0:
            mutex.release()
            mutex_s.release()
            return
        event = eventList[0]
        if event[0] == 'MVT' or event[0] == 'MVF':
            mutex.release()
            time.sleep(0.5)
            mutex.acquire()
            event = eventList[0]
            if event[0] == 'MVT':
                print '---CRT', event[1]
                if not self.checkHide(event[1]):
                    if not self.checkPathHide(event[1]):
                        eventToSend.append(('CRT ' + event[1]))
                eventList.pop(0)
            elif event[0] == 'MVF':
                print '---DEL', event[1]
                if not self.checkRename():
                    if not self.checkHide(event[1]):
                        if not self.checkCreate(event[1]):
                            eventToSend.append(('DEL ' + event[1]))
                            #   fileToRemove = event[2]
                eventList.pop(0)
            elif event[0] == 'MOD':
                print '---'+event[0], event[1]
                if not self.checkHide(event[1]):
                    eventToSend.append(('MOD ' + event[1]))
                eventList.pop(0)
                eventList.pop(0)
        elif event[0] == 'MOD':
            print '---'+event[0], event[1]
            eventList.pop(0)
            mutex.release()
            time.sleep(0.5)
            mutex.acquire()
            if not self.checkHide(event[1]):
                eventToSend.append(('MOD ' + event[1]))
            #if len(eventList) > 0:
            #    eventList.pop(0)
        elif event[0] == 'DEL':
            print '---'+event[0], event[1]
            if not self.checkHide(event[1]):
                eventToSend.append(('DEL ' + event[1]))
            else:
                eventList.pop(0)                
            #fileToRemove = event[2]
            eventList.pop(0)
        mutex.release()
        mutex_s.release()

def event_reader(name, path):
    er = eventReader()
    while True:
        if len(eventList):
            er.parseEvent()

def parsePath(path):
    request = path.split()
    cmd = request[0]
    abPath = request[1]
    fileType = ''
    print 'abPath = ' + abPath
    if os.path.isfile(abPath):
        fileType = 'F'
    else:
        fileType = 'D'
    toStrip = cmd + ' ' + root + '/'
    filepath = path.replace(toStrip, "")
    return cmd, fileType, filepath


def sendRequest(name, sock):

    while True:
        mutex_s.acquire()
        if len(eventToSend) != 0:
            event = eventToSend.pop(0)
            cmd, fileType, filepath = parsePath(event)
            toSend = cmd + ' ' + fileType + ' ' + filepath
            print 'send out: ' + toSend
            sock.send(toSend)
            res = sock.recv(1024)
            if res == 'OK':
                continue
            elif res == 'conflict':
                eventContent = event.split()
                originPath = eventContent[1]
                newPath = originPath + '_conflict_' + username + '_' + str(time.time())
                os.rename(originPath, newPath)
        mutex_s.release()


def recvRequest(name, sock):
    s3Connecter = S3(access_key,secret_key)
    s3Connecter.connect()
    while True:
        request = sock.recv(1024)
        print request
        args = request.split()
        cmd = args[0]
        if cmd == 'upload':
            DorF = args[1]
            path = args[2]
            bucket = args[3]
            if DorF == 'F':
                s3Connecter.upload(bucket, os.path.join(root, path))
                sock.send('ACK')
            elif DorF == 'D':
                fileList = []
                for originDir,dirs,files in os.walk(os.path.join(root, path)):
                    for filename in files:
                        fileList.append(os.path.join(originDir, filename))
                for filetoUpload in fileList:
                    s3Connecter.upload(bucket, filetoUpload)
                sock.send('ACK')
            
        elif cmd == 'download':
            DorF = args[1]
            path = args[2]
            bucket = args[3]
            if DorF == 'F':
                filename = '.' + args[4]
                d_file = os.path.join(root, path, filename)
                s3Connecter.download(bucket, args[4], d_file)
                sock.send('Download finished')
                res = sock.recv(1024)
                if res == 'apply':
                    n_file = os.path.join(root, path, args[4])
                    os.rename(d_file, n_file)
            elif DorF == 'D':
                filename = '.' + args[4]
                d_file = os.path.join(root, path, filename)
                os.mkdir(d_file)
                fileList = s3Connecter.lsfile(bucket)
                for f in fileList:
                    new_f = '.' + f.name
                    d_f = os.path.join(d_file, new_f)
                    s3Connecter.download(bucket, f.name, d_f)
                sock.send('Download finished')
                res = sock.recv(1024)
                if res == 'apply':
                    for f in fileList:
                        new_f = '.' + f.name
                        d_f = os.path.join(d_file, new_f)
                        n_f = os.path.join(d_file, f.name)
                        os.rename(d_f, n_f)
                    n_file = os.path.join(root, path, args[4])
                    os.rename(d_file, n_file)
                    

        elif cmd == 'delete':
            DorF = args[1]
            path = args[2]
            mutex_s.acquire()
            mutex.acquire()
            if DorF == 'F':
                d_file = os.path.join(root, path)
                if os.path.exists(d_file) == False:
                    print 'File to delete does not exist '
                    mutex.release()                
                    mutex_s.release()
                    continue
                os.remove(d_file)
                oriLen = len(eventList)
                print 'oriLen: ' + str(oriLen)
                mutex.release()
                time.sleep(0.5)
                mutex.acquire()
                aftLen = len(eventList)
                print 'aftLen: ' + str(aftLen)
                if aftLen - oriLen == 1:
                    print 'delete in list: DEL ' + eventList.pop(oriLen)[1]
                else:
                    toRemove = ('DEL', d_file)
                    if toRemove in eventList:
                        eventList.remove(toRemove)
                        print 'delete event after remove'
                    else:
                        print 'no delete after remove. eventList:'
                        print eventList
                        print 'toRemove:'
                        print toRemove
            elif DorF == 'D':
                d_file = os.path.join(root, path)
                if os.path.exists(d_file) == False:
                    print 'File to delete does not exist '
                    mutex.release()                
                    mutex_s.release()
                    continue
                shutil.rmtree(d_file)
                oriLen = len(eventList)
                mutex.release()
                time.sleep(0.5)
                mutex.acquire()
                aftLen = len(eventList)
                toRemove = ('DEL', d_file)
                for i in range(oriLen, aftLen):
                    if eventList[i][0] == 'DEL' and (toRemove[1] in eventList[i][1]):
                        print 'delete event after remove: DEL' + eventList[i][1]
                        del eventList[i]
            mutex.release()                
            mutex_s.release()

def main():

    print "Welcome to DevilBOX."
    #    global eventList
    # watch manager
    
    hostname = 'colab-sbx-207.oit.duke.edu'
    IP = socket.gethostbyname(hostname)
    print IP
    port1 = 8000
    s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s1.connect((IP, port1))

    port2 = 8001
    s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s2.connect((IP, port2))

    global root 
    global username
    valid = 0
    while valid == 0:
        lors = raw_input("Log or Sign: -> (l/s) ")
        username = raw_input("Username: -> ")
        password = raw_input("Password: -> ")
        userPath = logIN(username, password, s1, lors)
        res = userPath.checkIN()
        if res == 'fail' or res == 'wrong_input':
            print 'Login failed, try again'
        else:
            root = res
            valid = 1
            
    #send request
    t1 = threading.Thread(target = sendRequest, args = ("sr", s2))
    t1.setDaemon(True)
    t1.start()
    #watch manager
    watchManager = threading.Thread(target = watch_manager, args = ("wm", root))
    watchManager.setDaemon(True)
    watchManager.start()
    #event reader
    ER = threading.Thread(target = event_reader, args = ("er", root))
    ER.setDaemon(True)
    ER.start()
    #recv request
    t2 = threading.Thread(target = recvRequest, args = ("rr", s1))
    t2.setDaemon(True)
    t2.start()

    global eventToSend
    while True:
        user_input = raw_input("What do you want?: -> (Try \'share\')")
        if user_input == 'print':
            print eventToSend
        if user_input == 'share':
            fileList = os.listdir(root)
            dirList = filter(lambda x: os.path.isdir(os.path.join(root, x)), fileList)
            print "Which directory to share? "
            count = 0
            for directory in dirList:
                print str(count) + ': ' + directory 
                count += 1
            shareChoice = -1
            while shareChoice < 0 or shareChoice > len(dirList):
                rangeToUser = "Dir to Share: -> (0 to %d)" % len(dirList)
                shareChoice = int(raw_input(rangeToUser))
            nameToShare = raw_input("Whom to share? -> ")
            shareinfo = 'SHR' +' '+ dirList[shareChoice] +' '+ nameToShare
            s2.send(shareinfo)
            response = s2.recv(1024)
            print response
            

if __name__ == '__main__':
    main()
