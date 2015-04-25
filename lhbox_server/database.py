#! /usr/bin/env python
# -*- coding: utf-8 -*-
import pymongo

class Mydb(object):
    
    def __init__(self, host, port):
        #conn 类型<class 'pymongo.connection.Connection'>
        try:
            self.client = pymongo.MongoClient(host, port)
        except pymongo.errors.ConnectionFailure:
            print 'connect to %s:%s fail' %(host, port)
            exit(0)

    def __del__(self):
        self.client.close()

    def use(self, dbname):
        # 这种[]获取方式同样适用于shell,下面的collection也一样
        #db 类型<class 'pymongo.database.Database'>
        self.db = self.client[dbname]

    def setCollection(self, collection):
        if not self.db:
            print 'don\'t assign database'
            exit(0)
        else:
            self.coll = self.db[collection]

    def find_one(self, query = {}):
        #注意这里query是dict类型
        if type(query) is not dict:
            print 'the type of query isn\'t dict'
            exit(0)
        try:
            #result type<'dict'>
            if not self.coll:
                print 'don\'t assign collection'
            else:
                result = self.coll.find_one(query)
        except NameError:
            print 'some fields name are wrong in ',query
            exit(0)
        return result

    def find(self, query = {}):
        #注意这里query是dict类型
        if type(query) is not dict:
            print 'the type of query isn\'t dict'
            exit(0)
        try:
            #result类型<class 'pymongo.cursor.Cursor'>
            if not self.coll:
                print 'don\'t assign collection'
            else:
                result = self.coll.find(query)
        except NameError:
            print 'some fields name are wrong in ',query
            exit(0)
        return result

    def exist(self, query):
        if type(query) is not dict:
            print 'the type of query isn\'t dict'
            exit(0)
        try:
            if not self.coll:
                print 'don\'t assign collection'
                return False
            else:
                result = self.coll.find_one(query)
                print result
                if result != None:
                    return True
                else:
                    return False
        except NameError:
            print 'some fields name are wrong in ',query
            exit(0)
        
        
    

    def insert(self, data):
        if type(data) is not dict:
            print 'the type of insert data isn\'t dict'
            exit(0)
        #insert会返回新插入数据的_id
        if self.exist(data) == True:
            print('Document already exist.')
            return False
        else:
            self.coll.insert_one(data)
            print('Insert successfully.')
            return True

    def remove(self, data):
        if type(data) is not dict:
            print 'the type of remove data isn\'t dict'
            exit(0)
        #remove无返回值
        self.coll.delete_one(data)

    def update(self, data, setdata):
        if type(data) is not dict or type(setdata) is not dict:
            print 'the type of update and data isn\'t dict'
            exit(0)
        #update无返回值
        self.coll.update_one(data,{'$set':setdata})

    def count(self):
        return self.coll.count()
        
    def print_database(self):
        result = self.coll.find()
        for i in result:
            print i

if __name__ == '__main__':
    connect = mydb('localhost', 27017)
    connect.use('test_for_new')
    connect.setCollection('collection1')
    connect.insert({'a':10, 'b':1})
    connect.insert({'a':5, 'b':6})
    connect.coll.find_one_and_delete({'c':5})    
    #x也是dict类型，非常好
    print type(result)
    for x in result:
        print type(x)
        if 'c' in x:
            print x['_id'], x['a'], x['b'], x['c']
        else:
            print x['_id'], x['a'], x['b']
