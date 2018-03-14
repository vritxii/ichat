import time, sys, threading

from imodules import MB, RandStr, LoopDir
from igenesis import PathSep
from igenesis import TEMP_DIR
import os
import hashlib
from isocket import Packet
def fullpath(fpath, isFile=True):
    cur_path = sys.path[0]
    full_path = fpath
    if fpath[0] == '.':
        full_path = cur_path + fpath[1:]
    
    if fpath[0] != '/':
        full_path = cur_path + '/' + fpath

    if not isFile:
        os.mkdir(full_path)
    return full_path

        
def md5hex(word):
    """ MD5加密算法，返回32位小写16进制符号
    """
    if isinstance(word, unicode):
        word = word.encode("utf-8")
    elif not isinstance(word, str):
        word = str(word)
    m = hashlib.md5()
    m.update(word)
    return m.hexdigest()

def calcmd5sum(bytes_data):
    new_md5 = hashlib.md5(bytes_data)
    return new_md5.hexdigest().encode(encoding='utf_8')
    pass

def md5sum(fname, key=b''):
    """ 计算文件的MD5值
    """
    def read_chunks(fh):
        fh.seek(0)
        chunk = fh.read(8096)
        while chunk:
            yield chunk
            chunk = fh.read(8096)
        else: #最后要将游标放回文件开头
            fh.seek(0)

    m = hashlib.md5(key)
    if isinstance(fname, (str)) \
            and os.path.exists(fname):
        with open(fname, "rb") as fh:
            for chunk in read_chunks(fh):
                m.update(chunk)
    #上传的文件缓存 或 已打开的文件流
    elif fname.__class__.__name__ in ["StringIO", "StringO"] \
            or isinstance(fname, file):
        for chunk in read_chunks(fname):
            m.update(chunk)
    else:
        return ""
    return m.hexdigest()

def BuildFileBlocksTable(fname, buf_size = 1*MB, newfile=None):
    fpath = fullpath(fname)
    if not os.path.exists(fpath):
        print(fpath)
        return None, None, False

    new_f = None
    if newfile != None:
        newfile = fullpath(newfile)
        new_f = open(newfile, 'wb+')

    read_size = buf_size
    index = 0
    total_md5 = b''
    blocks = []
    total_size = 0
    with open(fpath, 'rb') as f:
        while read_size == buf_size:
            buf = f.read(buf_size)
            if new_f != None:
                new_f.write(buf)
            read_size = len(buf)
            total_size += read_size
            #print('read size: ', read_size)
            buf_md5 = calcmd5sum(buf)
            total_md5 = calcmd5sum(total_md5+buf_md5)
            blocks.append(buf_md5)
    
    if new_f != None:
        new_f.close()
        print('Write to new file:', newfile)

    print(fpath + ': ' + str(total_size))
    return total_md5, blocks, read_size
    pass

class FileCenter():
    def __init__(self, owner, home_dir, max_num_proc=10):
        '''
        owner: email
        '''
        if home_dir[-1] != PathSep:
            home_dir += PathSep
        self.__owner = owner
        self.__home_dir = home_dir
        self.__max_num_proc = max_num_proc
        
        self.__file_md5table = {} #md5: blocks_md5_table
        self.__file_sizetable = {} #md5: size
        self.__file_states = {} #md5: [block states] {0(free) | 1(downloading) | 2(finish)}
        self.__file_finished = {} #{md5: 0(downloading) | 1(finish)}
        self.__file_sharers = {} #{md5:users_list}
        self.__sharefiles = [] #md5
        self.__rlock = threading.RLock()
        self.__block_size = 1*MB
        self.__tmpfiles = {} #{md5:{index:block_data}}
        
        self.__pointers = {} #{md5: file_writed_blocks}
        self.__file_objs = {} #{md5: opened_file_obj}
        self.__valid_users = {} #{email:state{0(free) | 1(transfer)}
        #self.__initfiles()
        pass

    def Initfiles(self):
        files = LoopDir(self.__home_dir)
        print(files)
        for file in files:
            self.AddFile(file)
        pass

    def CheckExist(self, file_md5:str):
        return file_md5 in self.__sharefiles
        pass

    def genpath(self, filemd5):
        path = self.__home_dir + filemd5
        return path
        pass

    def Download(self, fileinfo:dict):
        '''
        args:
            fileinfo: md5:str, table:list, sharers:list, name=None
        return:
            0 | 1
        '''
        filemd5 = fileinfo['md5']
        file_table = fileinfo['table']
        file_sharers = fileinfo['sharers']
        filename = None
        if 'name' in fileinfo.keys():
            filename = fileinfo['name']   
        if filemd5 in self.__file_states.keys() or filemd5 in self.__file_finished.keys():
            return 0
        filepath = self.genpath(filename) if filename else self.genpath(filemd5)
        self.__file_objs[filemd5] = open(filepath, 'wb+')
        self.__file_md5table[filemd5] = file_table
        self.__file_finished[filemd5] = 0
        self.__file_sharers[filemd5] = file_sharers
        self.__pointers[filemd5] = 0
        for user_email in file_sharers:
            if user_email not in self.__valid_users.keys():
                self.__valid_users[user_email] = 0
        self.__file_states[filemd5] = [0] * len(file_table)
        print('Init Downloading, Please call GetBlock function')
        self.__sharefiles.append(filemd5)
        return 1
        pass

    def Upload(self, tcp_conn, header:dict, payload=b''):
        '''
        file_info returned by AddFile
        '''
        pack = Packet()
        des = header['src']
        src = header['des']
        header['src'] = des
        header['des'] = src
        header['status'] = 1
        header['op'] = 'file/block'
        extra = header['extra']
        filemd5 = extra['md5']
        table = extra['table']
        filepath = extra['path']
        total_size = extra['size']
        if filemd5 in self.__sharefiles:
            try: 
                with open(filepath, 'rb') as f:
                    index = 0
                    send_size = 0
                    for block_md5 in table:
                        header['extra'] = {'md5':filemd5, 'index':index, 'blockmd5':block_md5}
                        payload = f.read(self.__block_size)
                        tcp_conn.sendall(pack.Pack(header, payload))
                        send_size += len(payload)
                        index += 1
                tcp_conn.close()
                print('发送了%d字节', send_size)
                print('发送成功?', send_size==total_size)
            except Exception as e:
                print('发送失败')
        pass 

    def __block_timer(self, block_info, timeout=30):
        '''
        block_info: {'md5', 'index', 'blockmd5', 'sharer'}
        '''
        time.sleep(timeout)
        filemd5 = block_info['md5']
        index = block_info['index']
        sharer = block_info['sharer']
        if self.__file_states[filemd5][index] == 1:
            self.__file_states[filemd5][index] = 0
        N = len(self.__file_sharers[filemd5])

        index = 0
        for i in range(N):
            if sharer == self.__file_sharers[filemd5]:
                index = i
                break
        del self.__file_sharers[filemd5][index]
        pass


    def NextBlock(self, filemd5, timeout=30):
        '''
        returns:
            index, free_user_email
        '''
        next_index = -1
        valid_user = ''
        if self.__file_finished[filemd5]:
            return next_index, valid_user
        

        for index in range(len(self.__file_states[filemd5])):
            if self.__file_states[filemd5][index] == 0:
                next_index = index
                break
        

        while (not self.__file_finished[filemd5]) and index != -1 and timeout > 0:
            for user in self.__valid_users.keys():
                if self.__valid_users[user] == 0:
                    valid_user == user
                    break
            if valid_user != '':
                break

            time.sleep(2)
            timeout -= 2
        return next_index, valid_user
        pass

    def TakeBlock(self, block_info:dict):
        '''
        block_info: {'md5', 'index', 'blockmd5'}
        '''
        filemd5 = block_info['md5']
        index = block_info['index']
        try:
            return self.__seek_block(filemd5, index)
        except Exception as e:
            return None
    
    def __checkfinished(self, filemd5:str):
        finished = self.__pointers[filemd5] == len(self.__file_states[filemd5])
        if finished:
            self.__file_finished[filemd5] = 1
            del self.__pointers[filemd5]
            del self.__file_states[filemd5]
            del self.__tmpfiles[filemd5]
            del self.__file_sharers[filemd5]
            self.__file_objs[filemd5].close()
            del self.__file_objs[filemd5]

    def AddBlock(self, block_info:dict, block_data:bytes, from_user:str):
        '''
        block_info: {'md5', 'index', 'blockmd5'}
        '''
        filemd5 = block_info['md5']
        index = block_info['index']

        try:
            if from_user in self.__valid_users.keys():
                self.__valid_users[from_user] = 0

            if index == self.__pointers[filemd5] and self.__file_states[filemd5][index] == 1:
                self.__file_objs[filemd5].write(block_data)
                self.__pointers[filemd5] += 1
                self.__file_states[filemd5][index] = 2

                while self.__pointers[filemd5] in self.__tmpfiles[filemd5].keys():
                    self.__file_objs[filemd5].write(self.__tmpfiles[filemd5][self.__pointers[filemd5]])
                    del self.__tmpfiles[filemd5][self.__pointers[filemd5]]
                    self.__pointers[filemd5] += 1

                self.__checkfinished(filemd5)
            else:
                if self.__file_states[filemd5][index] == 1:
                    self.__tmpfiles[filemd5][index] = block_data
                    self.__file_states[filemd5][index] = 2
            
        except Exception as e:
            pass
        finally:
            del block_data
        pass

        
    def AddFile(self, filepath:str):
        randname = RandStr(16)
        newfilepath = TEMP_DIR + randname
        file_md5, file_table, size = BuildFileBlocksTable(fname=filepath, newfile=newfilepath)
        os.rename(newfilepath, self.genpath(file_md5))
        document = None
        if size > 0:
            document = {'path':newfilepath, 'md5':file_md5, 'table':file_table, 'size':size}
            self.__file_md5table[file_md5] = file_table
            self.__file_sharers[file_md5] = [self.__owner]
            self.__file_sizetable[file_md5] = size
            self.__files_finished[file_md5] = 1
        return document
        pass

    def DelFile(self, fileinfo:dict):
        '''
        fileinfo: return by AddFile
        '''
        filepath = fileinfo['path']
        filemd5 = fileinfo['md5']
        try:
            os.remove(filepath)
        except Exception as e:
            pass
        pass

    def isFull(self, filemd5):
        if len(self.__file_sharers[filemd5]) > self.__max_num_proc:
            return True
        return False
        
    def UpdateList(self, filemd5, file_sharers:list):
        full = self.isFull()
        if full:
            return full

        if isinstance(file_sharers, str):
            file_sharers = [file_sharers]

        if filemd5 not in self.__file_sharers.keys():
            self.__file_sharers[filemd5] = []

        for user_email in file_sharers:
            if user_email not in self.__valid_users.keys():
                self.__valid_users[user_email] = 0

            if user_email not in self.__file_sharers[filemd5]:
                self.__file_sharers[filemd5].append(file_sharers)
        return full
        #无效用户不用在这里删除，因为在块下载超时后会把该用户删掉

    def __seek_block(self, filemd5, index):
        block_data = None
        if filemd5 in self.__file_states[filemd5] and self.__file_states[filemd5][index] == 2:
            if index in self.__tmpfiles[filemd5]:
                block_data = self.__tmpfiles[filemd5][index]
                return block_data
            start = index * self.__block_size
            self.__file_objs[filemd5].seek(start, 0)
            blockdata = self.__file_objs[filemd5].read(self.__block_size)
            self.__file_objs[filemd5].seek(0, 2)
            return blockdata

        filepath = self.genpath(filemd5)
        with open(filepath, 'rb') as f:
            start = index * self.__block_size
            f.seek(start, 0)
            blockdata = f.read(self.__block_size)
            f.close()
            return blockdata