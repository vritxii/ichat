import sys
sys.path.append('./')
sys.path.append('../../')
from idb import *
from imodules import RandStr

def TinyDBTest(tname='nkdzt@foxmail.com'):
    tdb = TinyDBConnection('./db/test.json')
    print(tdb.all())
    #tdb.new_table(tname)
    '''
    for i in range(10):
        tdb.insert({'owner':str(i)})
        tdb.insert({'owner':str(i*i)},tname)
        pass
    '''
    print('DB res:')
    condition = ['owner', '>', '0']
    print(tdb.search(condition))
    print('Table res')
    print(tdb.search(condition, tname))
    return tdb.search(condition, tname)

def LevelDBTest():
    ldb = LevelDBConnection('./db/test')
    keys = [b'1',b'2',b'3']
    print('Simple Test')
    for i in keys:
        ldb.Put(i, RandStr().encode(encoding='utf_8'))
        print(ldb.Get(i))
    SnapshotName = 'v1'
    ldb.CreateSnapshot(SnapshotName)

    print("Multi Test")
    data_dict = {}
    for key in keys:
        data_dict[key] = RandStr().encode(encoding='utf_8')
    ldb.mPut(data_dict)
    print(ldb.mGet(keys))

    print('Snapshot Test')
    print(ldb.GetFromSnapshot(SnapshotName, b'1'))

if __name__ == '__main__':
    LevelDBTest()