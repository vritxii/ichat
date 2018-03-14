import json
import threading
import time

from igenesis import *
import json
import threading
import time

from iconfig import *
from igenesis import *
from idb import TinyDBConnection, LevelDBConnection
from isocket import ISocket
import ip
from ifileshare import FileCenter
from igpg import IGPG
from imodules import gen_nounce, check_nounce

class IServer():
    def __init(self):
        '''
        gpg: gpg user id
        daemon: client(C) | server(S)
        '''
        self.__tinydb_conn = None
        self.__laveldb_conn = None
        self.__gpg_obj = None
        self.__ipinfo = {}
        self.__chat_isocket = None
        self.__chat_isocket = None
        self.__video_isocket = None
        self.__seqnums = {}  # {email/groupid:seqnum}
        self.__out_counts = 0
        pass

    def Start(self):
        args = load_config('S')
        pass


    def SetGPG(self, uuid: str, passpharse=None):
        self.__gpg_obj = IGPG(uuid, passpharse)
        pass


    def SetSockets(self):
        self.__chat_isocket = ISocket(uuid=self.__email, email_pass=self.__email_pass, server=False)
        self.__chat_isocket.bind(('0.0.0.0', CHATPORT))
        self.__chat_isocket.connect((self.__server_addr, CHATPORT), self.__email, True)
        self.__p2p_isocket = ISocket(uuid=self.__email, only='S', server=True)
        self.__p2p_isocket.bind(('0.0.0.0', P2PPORT))
        self.__p2p_isocket.connect((self.__server_addr, P2PPORT), self.__email, True)
        self.__video_isocket = ISocket(uuid=self.__email, only='S', server=True, pack=False)
        self.__video_isocket.bind(('0.0.0.0', VIDEOPORT))
        self.__video_isocket.connect((self.__server_addr, VIDEOPORT), self.__email, True)
        pass


    def SetDB(self, dbpath=''):
        if dbpath == '':
            dbpath = DB_DIR
        self.__tinydb_conn = TinyDBConnection(dbpath)
        self.__leveldb_conn = LevelDBConnection(dbpath)
        pass

    def SetIP(self):
        self.__ipinfo = ip.GetIPInfo()
        pass


    def GetDaemon(self):
        return self.__daemon
        pass


    def GetProtocol(self):
        return self.__protocol


    def __resolve(self, header: dict, payload=None):
        '''
        收到从ISocket传上来的header(dict)和payload,通过header里的Op字段选择对应的函数处理并把header和payload作为参数传递过去
        '''
        protocol = header['protocol']
        sign = header['sign']
        des = header['des']
        if protocol not in VALIED_VERSIONS:
            print('Version Error, valied versions: ', json.dumps(VALIED_VERSIONS))
            return False

        if des == self.__email:
            content = self.__gpg_obj.decrypt(header['extra']['content'], sign)
            header['extra']['content'] = content
        select = header['op'].split('/')[0]  # msg | user | file
        op_type = header['op'].split('/')[1]
        func_name = '__' + select + '_' + op_type
        threading.Thread(target=getattr(self, func_name), args=([header, payload])).start()
        pass

    def __load_folder(self):
        '''
        加载下载目录内的文件信息
        '''
        print('Download folder: ', self.__folder)
        self.__fileshare_obj = FileCenter(self.__folder)
        self.__fileshare_obj.Initfiles()
        pass


    def __prepare(self, args: dict, payload=b''):
        '''
        准备header, 如果发送模式为socket,对payload和extra进行加密，如果是mail模式, 只加密extra, 将设置好的header(dict)和payload(bytes)一起传到ISocket发送出去
        header:
            报文参数: 至少需要{op, src, des, method, seqnum, status}
        '''
        if 'src' not in args.keys():
            args['src'] = self.__email
        if 'des' not in args.keys():
            args['des'] = self.__server_email
        if 'status' not in args.keys():
            args['status'] = -1
        if 'method' not in args.keys():
            args['method'] = 'IChat'
        if 'protocol' not in args.keys():
            args['protocol'] = 'ICHAT/' + str(Version)

        src = args['src']
        des = args['des']
        method = args['method']
        header= {}
        header['protocol'] = args['protocol']
        header['src'] = src
        header['des'] = des
        header['status'] = args['status']
        header['method'] = method
        header['op'] = args['op']
        select = args['op'].split('/')[0]
        op_type = args['op'].split('/')[1]
        msg_type = args['type']  # u(user) | g(group)
        method = args['method']
        default = (des == self.__server_email)
        if select == 'msg':
            nickname = args['name']  # user name | group name
            uid = GetUid(nickname, des)
            recipient_keyid = self.__gpg_obj.get_keyid(uid)
            header['seqnum'] = self.__seqnums[des]
            # 加密extra中的content
            content = args['content']
            if src == self.__email:
                content = self.__gpg_obj.encrypt(json.dumps(args['content']).encode('utf_8'), recipient_keyid, True)
            header['extra'] = {'type': msg_type, 'content': content}
            pass
        elif select == 'user':
            nickname = args['name']  # user name | group name
            uid = GetUid(nickname, des)
            recipient_keyid = self.__gpg_obj.get_keyid(uid)
            header['seqnum'] = self.__out_counts
            content = args['content']
            if src == self.__email:
                content = self.__gpg_obj.encrypt(json.dumps(args['content']).encode('utf_8'), recipient_keyid, True)
            header['extra'] = {'type': msg_type, 'content': content}
            pass
        elif select == 'file':
            content = args['content']
            header['extra'] = {'type': msg_type, 'content': content}
            pass
        else:
            print('Error packtet type')
        self.__chat_isocket.send(header, payload, default, method)
        self.__out_counts += 1
        pass

    def __msg_text(self, header: dict, payload: bytes):
        '''
        服务器收到
        '''
        src = header['src']
        des = header['des']
        status = header['status']
        seqnum = header['seqnum']
        msg_type = header['extra']['type']  # g(group) | (user)
        content = header['extra']['content']
        # status: 0发送失败, 1是是接收， -1是发送请求
        if des == self.__email:
            if status != 0:
                document = {}
                if status == 1:
                    document = {'src': des, 'des': src, 'type': 'text', 'content': content, 'seqnum': seqnum}
                else:
                    document = {'src': src, 'des': des, 'type': 'text', 'content': content, 'seqnum': seqnum}

                self.__tinydb_conn.insert(document, src)
                if src == self.__cur_contact:
                    print('刷新消息到聊天窗口')
                    print('text:', content)
            else:
                print('发送失败')
        else:
            '''
            服务器保存的是加密过的消息内容
            '''
            document = {'src': src, 'des': des, 'type': 'text', 'content': content, 'seqnum': seqnum}

            print('转发从%s 到 %s的消息' % (src, des))
            if msg_type == 'user':
                self.__tinydb_conn.insert(document, src)
                self.__tinydb_conn.insert(document, des)
                if des in self.__online_users:
                    self.__chat_isocket.send(header, payload, False)
            else:
                groupid = des
                print('群消息转发')
                self.__tinydb_conn.insert(document, des)
                members = self.__tinydb_conn.search({'groupid': groupid, 'status': 'online'}, 'groups')
                for member in members:
                    self.__chat_isocket.send(header, payload, False)
        pass

    def __msg_pic(self, header: dict, payload: bytes):
        '''
        content: 图片文件名
        payload: 图片数据
        '''
        src = header['src']
        des = header['des']
        status = header['status']
        seqnum = header['seqnum']
        msg_type = header['extra']['type']
        content = header['extra']['content']
        if des == self.__email:
            if status != 0:
                pic_path = self.___folder + '/pic/' + content
                with open(pic_path, 'wb+') as f:
                    print('Output to ', content)
                    f.write(payload)
                    pass

                document = {}
                if status == 1:
                    document = {'src': des, 'des': src, 'type': 'pic', 'content': content, 'seqnum': seqnum}
                else:
                    document = {'src': src, 'des': des, 'type': 'pic', 'content': content, 'seqnum': seqnum}

                self.__tinydb_conn.insert(document, src)
                if src == self.__cur_contact:
                    print('刷新消息到聊天窗口')
                    print('pic:', content)
            else:
                print('发送失败')
        else:
            '''
            服务器保存的是加密过的消息内容
            '''
            document = {'src': src, 'des': des, 'type': 'text', 'content': content, 'seqnum': seqnum}
            self.__tinydb_conn.insert(document, src)
            self.__tinydb_conn.insert(document, des)
            print('转发从%s 到 %s的消息' % (src, des))
            if msg_type == 'user':
                self.__tinydb_conn.insert(document, src)
                self.__tinydb_conn.insert(document, des)
                if des in self.__online_users:
                    self.__chat_isocket.send(header, payload, False)
            else:
                groupid = des
                print('群消息转发')
                self.__tinydb_conn.insert(document, des)
                members = self.__tinydb_conn.search({'groupid': groupid, 'status': 'online'}, 'groups')
                for member in members:
                    self.__chat_isocket.send(header, payload, False)
        pass

    def __msg_file(self,header: dict, payload: bytes):
        '''
        服务器处理客户端的发送文件请求，并且根据文件md5检查本地是否有，如果本地没有（设置status=0)，有则status=1,直接发送给接收者
        payload: 文件md5
        '''
        src = header['src']
        des = header['des']
        seqnum = header['seqnum']

        fileinfo = header['extra']['content']
        filemd5 = fileinfo['md5']
        filename = fileinfo['name']

        check_local = self.__fileshare_obj.CheckExist(filemd5)
        reply = header
        reply['src'] = self.__email
        reply['des'] = src
        if not check_local:
            reply['status'] = 0
            print('No Local', filemd5)
            ok = self.__fileshare_obj.Download(fileinfo)
        else:
            reply['status'] = 1
            print('Local exists')

        document = {'src': src, 'des': des, 'seqnum': seqnum, 'type': 'file', 'name': filename, 'md5': filemd5}
        self.__tinydb_conn.insert(document, src)
        self.__tinydb_conn.insert(document, des)
        print('转发从%s 到 %s的文件' % (src, des))
        # 回复发送者
        self.__prepare(reply, payload, False)
        # 转发
        self.__prepare(header, payload, False)
        pass


    def __msg_video(self, header: dict, payload: bytes):
        src = header['src']
        des = header['des']
        seqnum = header['seqnum']
        extra = header['extra']
        finish = extra['finish']
        if not finish:
            if des != self.__email:
                print('转发视频')
            else:
                print()
            pass
        else:
            self.__video_isocket.delconn(src)
            if des != self.__email:
                self.__video_isocket.delconn(des)
        pass


    def __s_user_register(self,header: dict, payload: bytes):
        '''
        payload: {GPG_keyid, nickname}
        '''
        payload = payload.decode('utf_8')
        user_info = json.loads(payload)
        user_email = header['src']
        nickname = user_info['nickname']
        keyid = user_info['gpgkeyid']

        if user_email in self.__users.keys():
            header['status'] = 0
            header['extra']['error'] = 'Email already registered'
            self.__chat_isocket.send(header, payload, False)
            return

        results = self.__gpg_obj.recv(keyid)
        status = len(results) > 0
        if status:
            header['status'] = 1
            document = {'email': user_email, 'nickname': nickname, 'keyid': keyid}
            self.__tinydb_conn.insert(document, 'users')
        else:
            header['status'] = 0
            header['extra']['error'] = 'Invalied gpg keyid'
        self.__chat_isocket.send(header, payload, False)



    def __s_user_login(self,header: dict, payload: bytes):
        '''
        ModNum default = 1510
        '''

        src = header['src']
        nounce = header['extra']['nounce']
        status = ((sum(int(ch) for ch in src) + nounce) % ModNum == 0)
        header['status'] = int(status)
        if status:
            document = {'email': src, 'nounce': nounce}
            self.__online_users[src] = nounce
        self.__chat_isocket.send(header, payload, False)

        if status:
            print('返回用户联系人(邮件+用户名）列表，未读消息')
            print('返回群列表（群名字，群id）,未读消息')
        pass



    def __user_logout(self, header: dict, payload: bytes):
        src = header['src']
        nounce = header['extra']['nounce']
        status = ((sum(int(ch) for ch in src) + nounce) % ModNum == 0)
        if not status:
            header['extra']['error'] = 'Check Nounce failed'

        haslogin = src in self.__online_users.keys()
        if not haslogin:
            header['extra']['error'] = '%s has logout' % src

        nounce_timeout = haslogin and self.__online_users[src] != nounce

        if nounce_timeout:
            header['extra']['error'] = 'Timeout nounce'

        status = status and nounce_timeout
        header['status'] = int(status)
        if status:
            del self.__online_users[src]
            print('成功注销:', src)
        self.__chat_isocket.send(header, payload, False)
        pass


    def __c_user_adduser(self, header: dict, payload: bytes):
        src = header['src']
        des = header['des']
        nickname = header['extra']['nickname']
        remark = header['extra']['remark']
        status = header['status']
        if status == -1:
            print('%s(%s) want to add you!(%s)' % (nickname, src, remark))
            # 弹出窗口显示请求者的邮箱，用户名和备注信息，并赋值给agree
            document = {'src': src, 'nickname': nickname, 'type': 'adduser', 'remark': remark}
            self.__tinydb_conn.insert(document, 'notify')
        elif status == 1:
            print('%s(%s) 同意添加为好友' % (nickname, src))
            self.__contacts[src] = nickname
        else:
            print('%s(%s) 拒绝添加为好友' % (nickname, src))
        pass


    def __user_adduser(self, header: dict, payload: bytes):
        src = header['src']
        des = header['des']
        status = header['status']
        if status == 1:
            document = {'user': src, 'contact': des}
            self.__tinydb_conn.insert(document, 'relations')
            document = {'user': des, 'contact': src}
            self.__tinydb_conn.insert(document, 'relations')
            self.__chat_isocket.send(header, payload, False)
        else:
            self.__chat_isocket.send(header, payload, False)


    def __user_deluser(self, header: dict, payload:bytes):
        src = header['src']
        des = header['des']
        status = header['status']
        if status == -1:
            self.__tinydb_conn.delete({'user': src, 'contact': des})
            self.__tinydb_conn.delete({'user': des, 'contact': src})
            header['status'] = 1
            self.__chat_isocket.send(header, payload, False)
        pass

    def __user_addgroup(self, header: dict, payload: bytes):
        '''
        des是群主邮箱
        '''
        src = header['src']
        des = header['des']
        status = header['status']
        groupid = header['extra']['groupid']
        groupname = header['extra']['groupname']
        if status == 1:
            document = {'group': groupid, 'user': des}
            self.__tinydb_conn.insert(document, 'relations')
            document = {'user': des, 'group': des}
            self.__tinydb_conn.insert(document, 'relations')
            self.__chat_isocket.send(header, payload, False)
        else:
            self.__chat_isocket.send(header, payload, False)
        pass


    def __user_delgroup(self, header:dict, payload:bytes):
        '''
        des是群主邮箱
        '''
        src = header['src']
        des = header['des']
        status = header['status']
        groupid = header['extra']['groupid']
        groupname = header['extra']['groupname']

        if status == -1:
            self.__tinydb_conn.delete({'user': src, 'group': groupid})
            self.__tinydb_conn.delete({'group': groupid, 'user': src})
            header['status'] = 1
            header['src'] = self.__email
            header['des'] = src
            self.__chat_isocket.send(header, payload, False)
        pass

    def __file_upload(self, header: dict, payload: bytes):
        src = header['src']
        des = header['des']
        status = header['status']
        filemd5 = header['extra']['md5']
        if status == -1:
            other_ip = header['extra']['ip']
            print('连接对方上传')
            tmp_conn = self.__p2p_isocket.connect(other_addr=(other_ip, P2PPORT), keepalive=0)
            self.__fileshare_obj.Upload(tmp_conn, filemd5)
        elif status == 1:
            print('上传成功')
        else:
            print('上传失败')
        pass

    def __file_download(self, header: dict, payload: bytes):
        '''
        header['extra']: {ipinfo:{'internal', 'outernal', 'trace', 'port'}, deepth:int, reaced:list, direct: 0 | 1, 'filemd5':str}
        '''
        print('搜索拥有该文件并且请求者能直接连接或者被直接连接的的其他用户')
        src = header['src']
        des = header['des']
        file_sharers = header['extra']
        status = header['status']
        broadcast = header['extra']['broadcast']
        extra = header['extra']
        ipinfo = extra['ipinfo']
        deepth = extra['deepth']
        reached = extra['reached']
        filemd5 = extra['filemd5']

        exist_not_full = self.__fileshare_obj.CheckExist(filemd5) and not self.__fileshare_obj.isFull(filemd5)
        if status == -1 and exist_not_full:
            if extra['direct']:
                newsocket = self.__p2p_isocket.connect((ipinfo['outernal'], ipinfo['port']), src)
                if newsocket:
                    header['status'] = 1
                    header['extra']['full'] = 0
                    newsocket.send(header, payload, False)

            elif self.__isdirect:
                print('叫对方连接自己')
                header['src'] = self.__email
                header['des'] = src
                header['status'] = 0
                header['extra']['in'] = 0
                self.__p2p_isocket.send(header, payload)
            else:
                res = ip.CompareIPS(self.__ipinfo['trace'], ipinfo['trace'])
                if res == 1:
                    print('连接对方')
                    newsocket = self.__p2p_isocket.connect((ipinfo['internal'], P2PPORT), src)
                    if newsocket:
                        header['status'] = 1
                        header['extra']['full'] = 0
                        newsocket.send(header, payload, False)
                elif res == 0:
                    print('叫对方连接自己')
                    header['src'] = self.__email
                    header['des'] = src
                    header['status'] = 0
                    header['extra']['in'] = 1
                    self.__p2p_isocket.send(header, payload)
        elif status == 0:
            full = extra['full']
            self_full = self.__fileshare_obj.isFull(filemd5)
            header['extra']['full'] = self_full
            if not self_full:
                isin = extra['in']
                new_conn = None
                if isin:
                    new_conn = self.__p2p_isocket.connect((ipinfo['internal'], P2PPORT), src)
                else:
                    new_conn = self.__p2p_isocket.connect((ipinfo['outernal'], P2PPORT), src)
                if new_conn:
                    print('P2P连接成功')
            else:
                print('满线程下载')
        else:
            full = extra['full']
            self_full = self.__fileshare_obj.isFull(filemd5)
            if (not full) and self_full:
                header['src'] = des
                header['des'] = src
                header['extra']['full'] = 1
                self.__p2p_isocket.send(header, payload, False)
                time.sleep(0.5)
                self.__p2p_isocket.delconn(src)
            elif full:
                self.__p2p_isocket.delconn(src)
            else:
                print('P2P connected')

        if (not full) and (self.__email not in reached) and (status == -1):
            print('广播')
            if header['deepth'] > 0:
                header['deepth'] -= 1
                header['reaced'].append(self.__email)
                self.__fileshare_obj.broadcast(header, payload)
        pass


    def __file_block(self, header:dict, payload:bytes):
        src = header['src']
        des = header['des']
        header['src'] = des
        header['des'] = src

        block_info = header['extra']
        status = header['status']
        block_data = None
        if status == -1:
            print('Send block to ', src)
            block_data = self.__fileshare_obj.TakeBlock(block_info)
            if not block_data:
                header['status'] = 0
                self.__chat_isocket.send(header, payload, False)
                return
            header['status'] = 1
            self.__chat_isocket.send(header, block_data, False)
            return

        elif status == 0:
            print('%s hasn\'t this block' % src)
        else:
            print('Get block from ', src)
            self.__fileshare_obj.AddBlock(block_info, payload, src)
        pass


    def __file_updatelist(self, header: dict, payload: bytes):
        src = header['src']
        des = header['des']
        filemd5 = header['extra']['md5']
        file_sharers = header['extra']['sharers']
        self.__fileshare_obj.UpdateList(filemd5, file_sharers)
        pass