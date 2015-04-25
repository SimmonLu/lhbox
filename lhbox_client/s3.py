from boto.s3.connection import S3Connection
from boto.s3.bucketlistresultset import BucketListResultSet
from boto.s3.key import Key

class S3(object):
    def __init__(self, access_key, secret_key):
        self.access_key = access_key
        self.secret_key = secret_key
        
    def connect(self):
        self.conn = S3Connection(self.access_key, self.secret_key)
        self.connected = 1
    
    def creat_bucket(self,bucket_name):
        if self.connected == 0:
            print('Not connected!')
        elif self.onnected == 1:
            bucket = self.conn.create_bucket(bucket_name)
        
    def upload(self, bucket, local_file):
        if self.connected == 0:
            print 'Not connected!'
        elif self.connected == 1:
            b = self.conn.get_bucket(bucket)
            k = Key(b)
            args = local_file.split('/')
            filename = args[-1]
            k.key = filename
            k.set_contents_from_filename(local_file)
        
    def ls(self):
        if self.connected == 0:
            print 'Not connected!'
        elif self.connected == 1:
            rs = self.conn.get_all_buckets()
            for b in rs:
                print b.name

    def lsfile(self, bucket):
        if self.connected == 0:
            print 'Not connected!'
        elif self.connected == 1:
            b = self.conn.get_bucket(bucket)
            file_list = b.list()
            for l in file_list:
                print l.name
            return file_list
            
    def info(self, bucket, filename):
        if self.connected == 0:
            print 'Not connected!'
        elif self.connected == 1:
            b = self.conn.get_bucket(bucket)
            brs = BucketListResultSet(bucket=b)
            for f in brs:
                key = b.lookup(f.name)
                print 'File: ' + f.name
                print 'size: ' + str(key.size)
                print 'last modified: ' + str(key.last_modified)
                print 'etag (md5): ' + str(key.etag)
            
    def permission(self,bucket,permission):
        if self.connected == 0:
            print 'Not connected!'
        elif self.connected == 1:
            while True:
                if permission not in ['private', 'public-read']:
                    print 'Input error!'
                elif permission in ['private', 'public-read']:
                    break
            b = self.conn.get_bucket(bucket)
            b.set_acl(permission)
            
    def download(self,bucket,s_file,d_file):
        if self.connected == 0:
            print 'Not connected!'
        elif self.connected == 1:
            b = self.conn.get_bucket(bucket)
            key = b.lookup(s_file)
            key.get_contents_to_filename(d_file)
        
    def delete_bucket(self,bucket):
        if self.connected == 0:
            print 'Not connected!'
        elif self.connected == 1:
            self.conn.delete_bucket(bucket)
        
    def delfile(self,bucket,filename):
        if self.connected == 0:
            print 'Not connected!'
        elif self.connected == 1:
            b = self.conn.get_bucket(bucket)
            b.delete_key(filename)
        
def showMenu():
    title = '''
        Amazon S3 Service
 
    connect        Get user credential and connect to Amazon S3
    creat        Creat bucket
    put        Upload file to S3
    ls        List buckets
    lsfile        List files in a bucket
    info        Display information of a file
    permission    Set bucket permissions
    get        Download file from S3
    delete        Delete bucket
    delfile        Delete file
    quit        Quit
 
Enter choice:'''


if __name__ == '__main__':
    showMenu()
