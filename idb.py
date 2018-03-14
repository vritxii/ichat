import os
import sys

def check(fpath, isFile=True):
    fpath = create_dbpath(fpath)
    print(fpath)
    if not os.path.exists(fpath):
        print(sys.path[0])
        if isFile:
            os.mknod(fpath)
        else:
            os.mkdir(fpath)
    return fpath

def create_dbpath(fpath):
    cur_path = sys.path[0]
    if fpath[0] == '.':
        db_path = cur_path + fpath[1:]
        return db_path
    
    if fpath[0] != '/':
        db_path = cur_path + '/' + fpath
        return db_path

    return fpath

def subset(a, b):
    return len(set(b).difference(set(a))) >= 0

import leveldb
import threading
class LevelDBConnection:
    __db = None
    __query = None
    __path = ''
    __name = ''
    __dbkey = None
    __snapshots = {}
    __lock = None

    def __init__(self, dbpath, dbkey=None):
        self.__path = dbpath
        self.__name = dbpath.split('/')[-1].split('.')[:-1]
        self.__db = leveldb.LevelDB(check(dbpath, False))
        self.__dbkey = dbkey
        self.__rlock = threading.RLock()
        pass

    def __checkbytes(self, key):
        if isinstance(key, bytes):
            return key
        elif isinstance(key, int):
            return bytes(key)
            pass
        return key.encode('utf_8')
            
    def Get(self, key, dbkey=None):
        if dbkey == self.__dbkey:
            key = self.__checkbytes(key)
            return self.__db.Get(key)
        print('Error dbkey')
        return None
        pass

    def Put(self, key, value, dbkey=None):
        if dbkey == self.__dbkey:
            key = self.__checkbytes(key)
            value = self.__checkbytes(value)
            self.__db.Put(key, value)
            return True
        print('Error dbkey')
        return False
        pass
    
    def Del(self, key, dbkey=None):
        if dbkey == self.__dbkey:
            key = self.__checkbytes(key)
            self.__db.Delete(key)
            return True
        print('Error dbkey')
        return False
        pass

    def mPut(self, data_dict, dbkey=None):
        if dbkey == self.__dbkey:
            for key in data_dict:
                key = self.__checkbytes(key)
                self.__db.Put(key, data_dict[key])
            return True
        print('Error dbkey')
        return False
        pass

    def mGet(self, key_arr, dbkey=None):
        data_dict = {}
        if dbkey == self.__dbkey:
            for key in key_arr:
                key = self.__checkbytes(key)
                data_dict[key] = self.__db.Get(key)
            return data_dict
        print('Error dbkey')
        return data_dict
        pass

    def mDel(self, key_arr, dbkey=None):
        if dbkey == self.__dbkey:
            for key in key_arr:
                key = self.__checkbytes(key)
                self.__db.Delete(key)
            return True
        print('Error dbkey')
        return False
        pass

    def Clear(self, dbkey=None):
        if dbkey == self.__dbkey:
            b = leveldb.WriteBatch()  
            for k in self.__db.RangeIter(include_value = False, reverse = True):  
                b.Delete(k)  
            self.__db.Write(b)
            return True
        print('Error dbkey')
        return False
        pass

    def CreateSnapshot(self, SnapshotName, dbkey=None, force=False):
        if dbkey == self.__dbkey:
            if SnapshotName not in self.__snapshots.keys() or force:
                self.__rlock.acquire()
                new_snapshot = self.__db.CreateSnapshot()
                self.__rlock.release()
                self.__snapshots[SnapshotName] = new_snapshot
                return True
            else:
                print('Snapshot already exists.')
                return False
        print('Error dbkey')
        return False
        pass

    def GetFromSnapshot(self, SnapshotName, key, dbkey=None):
        if dbkey == self.__dbkey:
            if SnapshotName in self.__snapshots.keys():
                key = self.__checkbytes(key)
                return self.__snapshots[SnapshotName].Get(key)
            else:
                print('Doesn\'t exist this Snapshot')
                return None
        print('Error dbkey')
        return None
        pass
    
    def Close(self, dbkey = None):
        if dbkey == self.__dbkey:
            for sk in self.__snapshots.keys():
                del self.__snapshots[sk]
            self.Clear(dbkey)
            return True

        print('Error dbkey')
        return False
        pass


from tinydb import TinyDB, Query


class TinyDBConnection:
    __db = None
    __query = None
    __query_map = {}
    __path = ''
    __name = ''
    __tables = {}
    __value_keys = ['owner', 'email', 'md5', 'user', 'blockstable', 'src','des', 'op', 'content']

    def __init__(self, dbpath):
        self.__path = dbpath
        self.__name = dbpath.split('/')[-1].split('.')[:-1]
        self.__db = TinyDB(check(dbpath))
        self.__query = Query()
        pass

    def __checkkeys(self, keys):
        for key in keys:
            if key in self.__value_keys:
                return True
        return False

    def insert(self, document, table_name=None):
        #print(document)
        if table_name != None and table_name in self.__tables.keys():
            #print('insert into ', table_name)
            if self.__checkkeys(document.keys()):
                self.__tables[table_name].insert(document)
            else:
                print('No valied key')
            return

        if table_name == None:
            #print('insert to default')
            self.__db.insert(document)
            return

        print('No this table')

    def minsert(self, documents, table_name=None):
        for document in documents:
            self.insert(document, table_name)
    def all(self, table_name=None):
        if table_name:
            return  self.__tables[table_name].all()

        return self.__db.all()

    def search(self, simple_condition, table_name=None):
        '''
        example:
            simple_condition = ['owner', '>', '0']
        '''
        results = []
        key = simple_condition[0]
        op = simple_condition[1]
        val = simple_condition[2]
        cs = Query()
        if not table_name:
            if op == '=':
                results = self.__db.search(getattr(cs, key) == val)
            elif op == '>':
                results = self.__db.search(getattr(cs, key) > val)
            elif op == '<':
                results = self.__db.search(getattr(cs, key) < val)
        else:
            if table_name not in self.__tables.keys():
                self.new_table(table_name)
            if op == '=':
                results = self.__tables[table_name].search(getattr(cs, key) == val)
            elif op == '>':
                results = self.__tables[table_name].search(getattr(cs, key) > val)
            elif op == '<':
                results = self.__tables[table_name].search(getattr(cs, key) < val)
        print('Table', table_name)
        return results
        pass

    def close(self):
        self.__db.close()

    def new_table(self, table_name):
        if table_name not in self.__tables.keys():
            #return self.__tables[table_name]
            self.__tables[table_name] = self.__db.table(table_name)
            return True
        #return self.__tables[table_name]
        print('table already exists')
        return False

    def delete(self, conditions, table_name=None, direct=True):
        if direct:
            if not table_name:
                self.__db.remove(conditions)
            else:
                self.__tables[table_name].remove(conditions)
        else:
            if not table_name:
                self.__db.remove(conditions)
            else:
                self.__tables[table_name].remove(conditions)
