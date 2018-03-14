import socket
import threading
import json
import platform
import datetime
import time
from ierror import IError
import smtplib, imaplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from igenesis import System
import inspect
from igenesis import DEFAULT_TEMPLATE, DEFAULT_VALUES, timestamp, Debug, HEADER_SIZE

class Packet:
    __template = None
    def __init__(self, template=DEFAULT_TEMPLATE):
        self.__template = template
        pass

    def Pack(self, header:dict, payload=b''):
        '''
        args:
            header: 报文头信息(dict)至少需要{op, src, des, seqnum, status}
            payload: 要打包的信息内容(bytes)
        
        return:
            packet_data(bytes)
        '''
        if Debug:
            print('Call: ', inspect.stack()[0][3])

        tmp_keys = header.keys()
        for key in DEFAULT_VALUES.keys():
            if key not in tmp_keys:
                header[key] = DEFAULT_VALUES[key]
        if 'date' not in tmp_keys:
            header['date'] = timestamp()
        format_header = self.__template.format(protocol=header['protocol'],op=header['op'],
                                                    src=header['src'], des=header['des'],method=header['method'],
                                                    useragent=header['useragent'],sign=header['sign'],
                                                    date=header['date'], mode=header['mode'],status=header['status'],
                                                    seqnum=header['seqnum'],extra=header['extra'])
        if isinstance(payload, str):
            payload = payload.encode('utf_8')

        return format_header.encode('utf_8') + payload
        pass
    
    def Unpack(self, data:bytes, max_size=HEADER_SIZE, seq_sign=b'\r\n\r\n'):
        '''
        args:
            data: 打包好的信息内容, bytes
            max_size: 最大报文头长度
            seq_sign: 报文头结束标志

        return:
            header(dict), payload(bytes)
        '''
        payload = b''
        if Debug:
            print('Call: ', inspect.stack()[0][3])
        if len(data) >= max_size:
            print('1024')
            print(data[:max_size])
            if seq_sign not in data[:max_size]:
                print('Error format header')
                return None, None
            header = data[:max_size].split(seq_sign, 1)[0]
            payload = data[(len(header)+len(seq_sign)):]
        else:
            print(data[:250])
            if seq_sign not in data:
                print('Error format header')
                return None, None
            header = data.split(seq_sign, 1)[0]
            payload = data[(len(header)+len(seq_sign)):]

        header_dict = {}
        header_arr = header.split(b'\r\n')
        for line in header_arr:
            key, value = line.split(b':', 1)
            header_dict[key.lower().decode('utf_8')] = value.decode('utf_8')

        return header_dict, payload
        pass

class IEmail:
    def __init__(self, email:str, email_pass:str, subject:str):
        self.__email= email
        self.__subject = subject
        self.__smtp = smtplib.SMTP_SSL("smtp.qq.com", 465)
        self.__smtp.login(email, email_pass)
        self.__imap = imaplib.IMAP4("imap.qq.com", 143)
        self.__imap.login(email, email_pass)
        pass
    
    def receive(self):
        '''
        return:
            mail_content: bytes
            att_data: bytes
        '''
        if Debug:
            print('Call: ', inspect.stack()[0][3])
        #try:
        self.__imap.select("INBOX")
        data = [b'']
        while data == [b'']:
            ok, data = self.__imap.search('UNSEEN', 'SUBJECT "%s"' % self.__subject)

        msgList = data[0].split()
        last = msgList[len(msgList) - 1]
        ok, data = self.__imap.fetch(last, "(RFC822)")
        mailtext = data[0][1]
        msg = email.message_from_bytes(mailtext)
        mail_content, att_data = self.__parseEmail(msg)

        self.__imap.store(last,'+FLAGS','\\seen')
        print('Type:::', type(mail_content))
        print('Len:::', len(mail_content))
        return mail_content, att_data
        #except Exception:
        #    print('error')

    def sendto(self, recipient_email:str, header:str, att_path=b''):
        if Debug:
            print('Call: ', inspect.stack()[0][3])
        # Create message self.__smtp.ainer - the correct MIME type is multipart/alternative
        msg = MIMEMultipart('alternative')
        msg['Subject'] = self.__subject
        # Record the MIME types of both parts - text/plain and text/html.
        text = MIMEText(header, 'plain')
        msg['From'] = formataddr(["From ", self.__email])  # 发件人邮箱昵称、发件人邮箱账号
        msg['To'] = formataddr(["FK", recipient_email])
        msg.attach(text)
        print(text)
        print('lennnnnnnn', len(header))
        if att_path != b'':
            att_path = att_path.decode('utf_8')
            print('Send Pic', att_path)
            if System == 'Windows':
                temp_list = att_path.split('\\')
            else:
                temp_list = att_path.split('/')
            file_name = temp_list[len(temp_list) - 1]
            pic_data = open(att_path, 'rb').read()
            print('SIze', len(pic_data))
            att = MIMEText(pic_data, 'base64', 'utf-8')
            att["Content-Type"] = 'application/octet-stream'
            att["Content-Disposition"] = 'attachment; filename=' + file_name # 改文件名
            msg.attach(att)

        self.__smtp.sendmail(self.__email, recipient_email, msg.as_string())

    #解析邮件方法（区分出正文与附件）
    def __parseEmail(self, msg):
        if Debug:
            print('Call: ', inspect.stack()[0][3])
        mail_content = None
        contenttype = None
        file_data = b''
        for part in msg.walk():
            if not part.is_multipart():
                contenttype = part.get_content_type()
                filename = part.get_filename()
                charset = part.get_charset()
                # 是否有附件
                if filename:
                    file_data = part.get_payload(decode=True)
                else:
                    if charset == None:
                        mail_content = part.get_payload(decode=True)
                    else:
                        mail_content = part.get_payload(decode=True).decode(charset)
        return mail_content, file_data
    
    def close(self):
        self.__smtp.quit()
        self.__imap.close()

class ISocket():
    __uuid = None #email
    __server_socket = None
    __conns = {} #dict: {email:tcp_client}
    __email_obj = None
    __buffer = []
    __rlock = threading.RLock()
    __wait = True
    __status = False
    __server = False
    __packer = None
    __client_status = False

    def __init__(self, uuid, email_pass='', only=None, server=False, subject='ichat', pack=True, limit=100):
        '''
        uuid: self email
        only: N(None) | S(socket) | E(email)
        '''
        if Debug:
            print('Call: ', inspect.stack()[0][3])
        self.__uuid = uuid
        self.__only = only
        self.__server = server
        self.__packer = Packet()
        self.__limit = limit
        self.__default = None
        self.__pack = pack
        '''
        if only in [None, 'N']:
            if self.__server:
                self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.__socket.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
                self.__conns[self.__uuid] = self.__socket
                self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.__server_socket.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
            else:
                self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.__conns[self.__uuid] = self.__socket
            if email_pass != '':
                self.__email_obj = IEmail(self.__uuid, email_pass, subject)

        elif only in ['S', 'socket']:
            if self.__server:
                self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.__socket.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
                self.__conns[self.__uuid] = self.__socket
                self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.__server_socket.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
            else:
                self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.__self.__smtp.s[self.__uuid] = self.__socket
        '''
        if only in [None, 'N']:
            if self.__server:
                self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.__server_socket.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
            if email_pass != '':
                print(self.__uuid, email_pass)
                self.__email_obj = IEmail(self.__uuid, email_pass, subject)

        elif only in ['S', 'socket']:
            if self.__server:
                self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.__server_socket.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
        elif only in ['E', 'email']:
            self.__email_obj = IEmail(self.__uuid, email_pass, subject)
        else:
            raise IError('Error parameters, only = {N(None) | S(socket) | E(email)}')
        
    def close(self):
        for conn in self.__conns:
            conn.close()
        self.__server_socket.close()
        self.__email_obj.close()

    def login_email(self, email_pass, subject='ichat'):
        if self.__email_obj != None:
            self.__email_obj = IEmail(self.__uuid, email_pass, subject)
        pass

    def bind(self, addr):
        if self.__only not in ['E', 'email']:
            if self.__server:
                self.__server_socket.bind(addr)              
        pass
    
    def connect(self, other_addr:str, other_email='', default=False, keepalive=1):
        if other_email in self.__conns.keys():
            return self.__conns[other_email]

        if self.__only not in ['E', 'email']:
            newsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            newsocket.connect(other_addr)
            newsocket.send(json.dumps({'email':self.__uuid, 'keepalive':keepalive}))
            if keepalive:
                self.__conns[other_email] = self.__socket
                self.__conns[other_addr].send(self.__uuid.encode('utf_8'))
            if default:
                self.__default = other_email
            return newsocket
        return None

    def delconn(self, email):
        if email in self.__conns.keys():
            self.__conns[email].close()
            del self.__conns[email]
        pass

    def broadcast(self, header:dict, payload:bytes):
        src = header['src']
        for conn in self.__conns.keys():
            if conn != src:
                header['des'] = conn
                self.send(header, payload, conn)

    def send(self, header:dict, payload=b'', default=True, method='Socket'):
        recipient_email = header['des']
        if method == 'Email':
            header = self.__packer.Pack(header)
            if isinstance(header, bytes):
                header = header.decode('utf_8')
            self.__email_obj.sendto(recipient_email, header, payload)
        else:
            if self.__pack:
                packet = self.__packer.Pack(header, payload)
            if self.__only not in ['E', 'email']:
                if default and self.__default:
                    self.__conns[self.__default].send(packet)
                else:
                    self.__conns[recipient_email].send(packet)
                return
            raise IError('only = Email')
        pass

    def __email_recv(self):
        if Debug:
            print('Call: ', inspect.stack()[0][3])
        while True:
            header, payload = self.__email_obj.receive()
            header = self.__packer.Unpack(header)[0]

            self.__rlock.acquire()
            self.__buffer.append((header, payload))
            self.__wait = False
            self.__rlock.release()
            
        pass
    
    def __socket_recv(self, tcp_conn, wait=True):
        recv_size = 1024**2
        email = None
        if wait:
            handinfo = tcp_conn.recv(1024).decode('utf_8')
            handinfo = json.loads(handinfo.decode('utf_8'))
            email = handinfo['email']
            keepalive = handinfo['keepalive']
            if keepalive:
                self.__conns[email] = tcp_conn

        while True:
            self.__rlock.acquire()
            recv_data = tcp_conn.recv(recv_size)
            if len(recv_data) < 24:
                tcp_conn.close()
                break
            if self.__pack:
                header, payload = self.__packer.Unpack(recv_data)
                self.__buffer.append((header, payload))
            else:
                self.__buffer.append(recv_data)
            self.__wait = False
            self.__rlock.release()

        if keepalive:    
            del self.__conns[email]
        print('discnnect')
        pass
    

    def recv(self, limit=1):
        if Debug:
            print('Call: ', inspect.stack()[0][3])
        index = 0
        packets = []
        while True and self.__status and index<limit:
            while self.__wait:
                time.sleep(0.1)
            self.__rlock.acquire()
            buf_size = len(self.__buffer)
            self.__rlock.release()
            for k in range(buf_size):
                packets.append(self.__buffer.pop())
                index += 1
                if index == limit:
                    break
            self.__rlock.acquire()
            buf_size = len(self.__buffer)
            self.__rlock.release()    
            if buf_size == 0:
                self.__wait = True
        if limit == 1:
            return packets[0]
        return packets

    def reciver(self, limit=0):
        '''
        limit: int
        return:
            limit=0 -> generator
            limit > 0 -> packets list (from new to old)
        '''
        while True and self.__status:
            while self.__wait:
                time.sleep(0.1)
            self.__rlock.acquire()
            buf_size = len(self.__buffer)
            tmp_buf = self.__buffer[:buf_size] #old to new
            tmp_buf.reverse() #new to old
            print(self.__buffer[:buf_size])
            self.__rlock.release()
            for k in range(buf_size):
                yield tmp_buf.pop()
                del self.__buffer[0]

            self.__rlock.acquire()
            buf_size = len(self.__buffer)
            self.__rlock.release()    
            if buf_size == 0:
                self.__wait = True
        pass

    def __handle_conn(self):
        if Debug:
            print('Call: ', inspect.stack()[0][3])
        self.__server_socket.listen(self.__limit)
        while True:
            conn,(addr,port)=self.__server_socket.accept()
            print('self.__smtp.ected by',addr,port)
            t = threading.Thread(target=self.__socket_recv, args=([conn]))
            t.setDaemon(True)
            t.start()
        pass

    def start(self):
        if Debug:
            print('Call: ', inspect.stack()[0][3])
        if self.__only in [None, 'N']:
            if self.__client_status:
                ts = threading.Thread(target=self.__socket_recv, args=(self.__socket, False))
                ts.setDaemon(True)
                ts.start()
            te=threading.Thread(target=self.__email_recv, args=())
            te.setDaemon(True)
            te.start()
        elif self.__only in ['S', 'socket']:
            if self.__client_status:
                ts=threading.Thread(target=self.__socket_recv, args=(self.__socket, False))
                ts.setDaemon(True)
                ts.start()
        elif self.__only in ['E', 'email']:
            te=threading.Thread(target=self.__email_recv, args=())
            te.setDaemon(True)
            te.start()

        if self.__server:
            tts = threading.Thread(target=self.__handle_conn, args=())
            tts.setDaemon(True)
            tts.start()

        self.__status = True
        pass