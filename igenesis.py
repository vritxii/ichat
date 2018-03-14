'''
Protocol(ICHAT/version)
Src(email) Des(email)
Method: Email | IChat
UserAgent:(OS,OS Version, OS Arch)
Sign: 0 | 1
Type:msg/{text | pic | file | video | p2p}, user/{register, login, logout, askgpg, adduser, addgroup, deluser, delgroup}, file/{download, upload, block, updatelist}
Crypto: aes | rsa | non
Status: -1 | 0 | 1
SeqNum:
Extra:example file block info {file_hash, block_hash, block_index}, update_info{src, des, group | contact, op:add, delete}

(Payload: file_block, file, user_info, user_fingerprint, user_contacts, msg_text, msg_pic)
'''
import inspect
import platform
import os
import time

VersionsFuncSet = {}
VALIED_VERSIONS = []
ClientPool = {}
ServerPool = {}
Version = 0.0
Daemon = 'S' # 'C'
Debug = True
System = platform.uname().system # Windows | Linux
#路径分割符
PathSep = '/' if System=='Windows' else '\\'

ModNum = 1510
#不同服务绑定端口
CHATPORT = 9900
P2PPORT = 9910
VIDEOPORT = 9920
HOME_DIR = os.getcwd()
DB_DIR = HOME_DIR + '/db/'
PIC_DIR = HOME_DIR + '/pics/'
TEMP_DIR = HOME_DIR + '/temp/'
FILE_DIR = HOME_DIR + '/files/'

def gen_user_agent():
    '''
    用于获取系统基本信息
    Return:
        user_agent: (OS,Version,Arch)
    '''
    uname = platform.uname()
    return '(' + uname.system + ',' + uname.release.split('-')[0] + ',' + uname.machine + ')'
    pass

def timestamp():
    return time.asctime(time.localtime(time.time()))
    pass

'''
Protocol(ICHAT/version)
Src(email) Des(email)
Method: Email | IChat
UserAgent:(OS,OS Version, OS Arch)
Sign: 0 | 1
Op:msg/{text | pic | file | video}, user/{register, login, logout, adduser, addgroup, deluser, delgroup}, file/{download, upload, block, updatelist} 
Crypto: AES | GPG
Status: -1 | 0 | 1
SeqNum:
Extra:for msg {'type': c | g, 'content'}, for user {'nickname', 'addr'(只在登录和响应有), 'nounce'， 'content'}     | example file block info {file_hash, block_hash, block_index}, update_info{src, des, group | contact, op:add, delete}

(Payload: file_block, file, msg_pic)
'''

Operations = ['msg/text', 'msg/pic', 'msg/file', 'msg/video', 'user/register', 'user/login', 'user/logout', 'user/addcontact', 'user/addgroup', 'user/delcontact', 'user/delgroup', 'file/download', 'file/upload', 'file/block', 'file/updatelist']
HEADER_SIZE = 2048
DEFAULT_TEMPLATE = '''Protocol:{protocol}\r
Op:{op}\r
Src:{src}\r
Des:{des}\r
Method:{method}\r
UserAgent:{useragent}\r
Sign:{sign}\r
Date:{date}\r
Crypto:{mode}\r
Status:{status}\r
SeqNum:{seqnum}\r
Extra:{extra}\r
\r
'''

DEFAULT_VALUES = {'protocol':'ICHAT/1.1', 'method':'IChat', 'mode':'GPG', 'extra':'{}', 'sign':1, 'useragent':gen_user_agent()}
VALIED_VERSIONS = ['ICHAT/'+'%.01f'% (ver) for ver in [1.0, 1.1, 1.2]]


def SetVersionsFuncSet(NewVersionFuncSet={}):
    global VersionsFuncSet, VALIED_VERSIONS
    if Debug:
        print('Call: ', inspect.stack()[0][3])

    if NewVersionFuncSet == {}:
        VersionsFuncSet[1.0] = {
            'server':['__msg_text', '__user_register', '__user_login', '__user_logout',
                        '__user_adduser', '__user_deluser'
                    ],
            'client':['__msg_text', '__user_register', '__user_login', '__user_logout',
                        '__user_adduser', '__user_deluser'
                    ]
        }

        VersionsFuncSet[1.1] = {
            'server':['__msg_text', '__msg_pic', '__msg_file', '__user_register', '__user_login', '__user_logout',
                        '__user_askgpg', '__user_adduser', '__user_deluser', '__user_addgroup', '__user_delgroup',
                        '__file_download', '__file_upload', '__file_block', '__file_updatelist'
                    ],
            'client':['__msg_text', '__msg_pic', '__msg_file', '__user_register', '__user_login', '__user_logout',
                        '__user_askgpg', '__user_adduser', '__user_deluser', '__user_addgroup', '__user_delgroup',
                        '__file_download', '__file_upload', '__file_block', '__file_updatelist'
                    ]
        }
    else:
        for version in NewVersionFuncSet.keys():
            if version not in VersionsFuncSet.keys():
                VersionsFuncSet[version] = NewVersionFuncSet[version]
            else:
                print('Version %d already existed' % version)
    VALIED_VERSIONS = ['ICHAT/'+'%.01f'% (ver) for ver in VersionsFuncSet.keys()]
    pass


SetVersionsFuncSet()


def DefineVersion():
    global Version
    if Debug:
        print('Call: ', inspect.stack()[0][3])
    NewVewsion = 0.0
    for version in VersionsFuncSet.keys():
        vfs_keys = list(VersionsFuncSet[version].keys())
        ok = len((list(set(ClientPool.keys()).intersection(set(VersionsFuncSet[version][vfs_keys[0]]))))) == len(VersionsFuncSet[version][vfs_keys[0]]) and \
                len((list(set(ServerPool.keys()).intersection(set(VersionsFuncSet[version][vfs_keys[1]]))))) == len(VersionsFuncSet[version][vfs_keys[1]])
        if ok and version > NewVewsion:
            NewVewsion = version
    Version = NewVewsion
    pass


DefineVersion()


def GetUid(name, email):
    uid = '%s <%s>' % (name, email)
    return uid


def Init(obj, args:dict, defaults={}):
    if defaults != {}:
        for attr_name in defaults.keys():
            if attr_name in args.keys():
                setattr(obj, attr_name, args[attr_name])
            else:
                setattr(obj, attr_name, defaults[attr_name])
        return
    for attr_name in args.keys():
        setattr(obj, attr_name, args[attr_name])
    pass