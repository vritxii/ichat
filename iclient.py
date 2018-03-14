from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import inspect
import sys, os, json, threading, time, random
sys.path.append('./')

from uis.ui_login import *
from uis.ui_main import *
from uis.ui_contact import *
from uis.ui_group import *
from uis.ui_modules import *
from iconfig import *
from igenesis import *
from idb import TinyDBConnection, LevelDBConnection
from isocket import ISocket
import ip
from ifileshare import FileCenter
from igpg import IGPG
from imodules import gen_nounce, check_nounce, RandStr

LOGIN_BTUS = {'login_btu':'active_login', 'register_btu':'active_register'}
MAIN_BUTS = {'logout':'active_logout'}
CONTACT_CHAT = {'send_text':'active_c_msg_text', 'send_pic':'active_c_msg_pic', 'send_file':'active_c_msg_file', 'send_video':'active_c_msg_video'}
GROUP_CHAT = {'send_text':'active_g_msg_text', 'send_pic':'active_g_msg_pic', 'send_file':'active_g_msg_file'}
msgs = {
    'zhongtao <2582783208@qq.com>':{
        'msg':[
            {
                'src': '781442859@qq.com',
                'des': '2582783208@qq.com',
                'type': 'text',
                'content': 'Hello Alice'
            },
            {
                'src': '2582783208@qq.com',
                'des': '781442859@qq.com',
                'type': 'pic',
                'content': '1.jpg'
            },
            {
                'src': '2582783208@qq.com',
                'des': '781442859@qq.com',
                'type': 'pic',
                'content': '2.jpg'
            },
            {
                'src': '781442859@qq.com',
                'des': '2582783208@qq.com',
                'type': 'text',
                'content': 'Hello Alice'
            },
            {
                'src': '781442859@qq.com',
                'des': '2582783208@qq.com',
                'type': 'file',
                'content': '123.pdf'
            },
            {
                'src': '2582783208@qq.com',
                'des': '781442859@qq.com',
                'type': 'pic',
                'content': '3.jpg'
            },
            {
                'src': '2582783208@qq.com',
                'des': '781442859@qq.com',
                'type': 'pic',
                'content': '4.jpg'
            }
        ],
        'file':[
            {
                'src': '2582783208@qq.com',
                'des': '781442859@qq.com',
                'type': 'file',
                'content': '123.pdf',
                'size': 29085
            },
            {
                'src': '781442859@qq.com',
                'des': '2582783208@qq.com',
                'type': 'file',
                'content': '123.txt',
                'size': 290
            },
            {
                'src': '781442859@qq.com',
                'des': '2582783208@qq.com',
                'type': 'file',
                'content': '高数.pdf',
                'size': 2967
            }
        ]
    },

    'fanjianzhong <781442859@qq.com>':{
        'msg':[
            {
                'src': '781442859@qq.com',
                'des': '2582783208@qq.com',
                'type': 'text',
                'content': 'Hello Alice'
            },
            {
                'src': '2582783208@qq.com',
                'des': '781442859@qq.com',
                'type': 'pic',
                'content': '1.jpg'
            },
            {
                'src': '2582783208@qq.com',
                'des': '781442859@qq.com',
                'type': 'pic',
                'content': '2.jpg'
            },
            {
                'src': '781442859@qq.com',
                'des': '2582783208@qq.com',
                'type': 'text',
                'content': 'Hello Alice'
            },
            {
                'src': '781442859@qq.com',
                'des': '2582783208@qq.com',
                'type': 'file',
                'content': '123.pdf'
            },
            {
                'src': '2582783208@qq.com',
                'des': '781442859@qq.com',
                'type': 'pic',
                'content': '3.jpg'
            },
            {
                'src': '2582783208@qq.com',
                'des': '781442859@qq.com',
                'type': 'pic',
                'content': '4.jpg'
            }
        ],
        'file':[
            {
                'src': '2582783208@qq.com',
                'des': '781442859@qq.com',
                'type': 'file',
                'content': '123.pdf',
                'size': 29085
            },
            {
                'src': '781442859@qq.com',
                'des': '2582783208@qq.com',
                'type': 'file',
                'content': '123.txt',
                'size': 290
            },
            {
                'src': '781442859@qq.com',
                'des': '2582783208@qq.com',
                'type': 'file',
                'content': '高数.pdf',
                'size': 2967
            }
        ]
    }
}

def geticon(pic_name, size):
    qp = QPixmap("icons/"+pic_name + '.jpg')
    qp.scaled(size, size)
    qi = QIcon()
    qi.addPixmap(qp)
    return qi


def msg_pic(pic_name, size):
    #print("ICHAT/pics/" + pic_name)
    qp = QPixmap(pic_name)
    qp.scaled(size, size)
    return qp

def getpixmap(pic_name, size):
    print("icons/"+pic_name+'.jpg')
    qp = QPixmap("icons/"+pic_name+'.jpg')
    qp.scaled(size, size)
    return qp

def gen_uuid(name, email):
    return "%s <%s>" % (name, email)


packet_buf = {}
buf_lock = threading.Lock()
class IRunner(QThread):
    __sig_send_packet = pyqtSignal(int, name='send_packet')
    def __init__(self):
        super(IRunner, self).__init__()
        self.__index = 0
        pass

    def set_isocket(self, s):
        self.__isocket_obj = s

    def bind(self, func):
        self.__sig_send_packet.connect(func)

    def run(self):
        global packet_buf
        for packet in self.__isocket_obj.reciver():
            print('Packet')
            print(packet[0])
            print(len(packet[1]))
            packet_buf[self.__index] = (packet[0], packet[1])
            self.__sig_send_packet.emit(self.__index)
            self.__index += 1

            pass
class IClient(QObject):
    __sig_msg_text = pyqtSignal(int, name='sig_msg_text')
    __sig_msg_pic = pyqtSignal(int, name='sig_msg_pic')
    __sig_msg_file = pyqtSignal(int, name='sig_msg_file')
    __sig_msg_video = pyqtSignal(int, name='sig_msg_video')

    __sig_user_register= pyqtSignal(int, name='sig_user_register')
    __sig_user_login = pyqtSignal(int, name='sig_user_login')
    __sig_user_logout = pyqtSignal(int, name='sig_user_logout')
    __sig_user_addcontact = pyqtSignal(int, name='sig_user_addcontact')
    __sig_user_delcontact = pyqtSignal(int, name='sig_user_delcontact')
    __sig_user_addgroup = pyqtSignal(int, name='sig_user_addgroup')
    __sig_user_delgroup = pyqtSignal(int, name='sig_user_delgroup')

    __sig_file_download = pyqtSignal(int, name='sig_file_download')
    __sig_file_upload = pyqtSignal(int, name='sig_file_upload')
    __sig_file_block = pyqtSignal(int, name='sig_file_block')
    __sig_file_updatelist = pyqtSignal(int, name='sig_file_updatelist')

    def __init__(self, parent=None):
        super(IClient, self).__init__(parent)
        if Debug:
            print('Call: ', inspect.stack()[0][3])

        self.__windows = {}
        self.__uis = {}
        self.__config = None
        self.__tinydb_conn = None
        self.__leveldb_conn = None
        self.__gpg_obj = None
        self.__ipinfo = {}
        self.__chat_isocket = None
        self.__chat_isocket = None
        self.__video_isocket = None
        self.__seqnums = {}  # {email/groupid:seqnum}
        self.__packet_count = 0
        self.__buf_lock = 0
        self.__online = False
        self.__registered = False
        self.__email = None
        self.__contacts_info = {}
        self.__chat_layouts = {}
        self.__contact_box_layouts = {}
        self.__file_table_layouts = {}
        self.__group_member_layouts = {}
        self.__out_counts = 0
        self.__folder = ''
        self.__runner = IRunner()
        self.__packet_buf = {}

    def Start(self):
        self.__config = load_config('C')
        self.__bind_signals()
        self.__ui_login()

    def __bind_signals(self):
        self.__signals = {}
        self.__signals['msg/text'] = self.__sig_msg_text
        self.__signals['msg/pic'] = self.__sig_msg_pic
        self.__signals['msg/file'] = self.__sig_msg_file
        self.__signals['msg/video'] = self.__sig_msg_video

        self.__signals['user/register'] = self.__sig_user_register
        self.__signals['user/login'] = self.__sig_user_login
        self.__signals['user/logout'] = self.__sig_user_logout
        self.__signals['user/addcontact'] = self.__sig_user_addcontact
        self.__signals['user/delcontact'] = self.__sig_user_delcontact
        self.__signals['user/addgroup'] = self.__sig_user_addgroup
        self.__signals['user/delgroup'] = self.__sig_user_delgroup

        self.__signals['file/download'] = self.__sig_file_download
        self.__signals['file/upload'] = self.__sig_file_upload
        self.__signals['file/block'] = self.__sig_file_block
        self.__signals['file/updatelist'] = self.__sig_file_updatelist

        for op in Operations:
            op_arr = op.split('/')
            print(op_arr)
            func_name = 'deal_' + op_arr[0] + '_' + op_arr[1]
            self.__signals[op].connect(getattr(self, func_name))
        pass

    def __initdb(self, contacts_info:dict):
        '''
        contacts_info:
            {
                'c':{
                    id:{
                        name:
                        id:
                }},
                'g':{
                    id:{
                        name:
                        id:
                },
                'b':{
                    id:{
                        name:
                        id:
                },
            }
        '''
        self.__contacts_info = contacts_info
        for box in self.__contacts_info.keys():
            for key in self.__contacts_info[box].keys():
                print(self.__contacts_info[box])
                self.__tinydb_conn.new_table(key)
                print(self.__contacts_info[box][key]['name'])
                self.__leveldb_conn.Put(key, self.__contacts_info[box][key]['name'])
        pass

    def __ui_login(self):
        login_window = QTabWidget()
        login_ui = Ui_LoginWidget()
        login_ui.setupUi(login_window)
        self.__windows['login'] = login_window
        self.__uis['login'] = login_ui

        back = "background.html"
        self.__set_back(back)
        self.__bind_active_funcs('login', LOGIN_BTUS)
        self.__uis['login'].email_cbox.currentTextChanged.connect(self.changeIcon)
        self.__center('login')
        self.__show('login')
        self.__set_config()
        pass

    def __set_config(self):
        _translate = QCoreApplication.translate
        last = self.__config['Last']
        users = self.__config['Users']
        user_emails = users.keys()
        default_user = None
        print(len(user_emails))
        self.__uis['login'].email_cbox.currentIndexChanged.connect(self.set_dafault)
        if len(last) > 0:
            default_user = users[last[0]]

        if len(user_emails) > 0:
            if not default_user:
                default_user = users[user_emails[0]]
            for email in user_emails:
                print('Add ', email)
                index = self.__uis['login'].email_cbox.count()
                self.__uis['login'].email_cbox.addItem("")
                self.__uis['login'].email_cbox.setItemText(index, _translate("LoginWidget", email))

        if default_user:
            self.set_dafault(default_user)
        pass

    def __ui_main(self, args:dict):
        print(args)
        self.__nickname = args['nickname']
        self.__email = args['src']
        self.__server_email = args['des']
        print(self.__email)
        print(self.__server_email)
        main_window = QFrame()
        main_ui = Ui_MainWindow()
        main_ui.setupUi(main_window)
        self.__windows['main'] = main_window
        self.__uis['main'] = main_ui
        self.__windows['login'].hide()
        self.__center('main')
        self.__uis['main'].usericon.setPixmap(getpixmap(self.__email, 70))
        self.__uis['main'].nickname.setText(self.__nickname)
        self.__uis['main'].useremail.setText(self.__email)
        self.__bind_active_funcs('main', MAIN_BUTS)
        contacts = {
            'c':{
                '781442859@qq.com': {'id': '781442859@qq.com', 'name': 'fanjianzhong', 'type': 'c'},
                '2582783208@qq.com': {'id': '2582783208@qq.com', 'name': 'zhongtao', 'type': 'c'},
            },
            'g':{
                '20182387': {'id': '20182387', 'name': 'four one nine', 'type': 'g'}
            },
            'b':{
                'nkdzt@foxmai.com': {'id': 'nkdzt@foxmai.com', 'name': 'zhongtao', 'type': 'b'}
            }
        }
        self.__initdb(contacts)
        for t in self.__contacts_info.keys():
            self.__new_contacts_groupbox(self.__contacts_info[t], t)

        self.__windows['main'].show()
        pass

    #*****************UI Funcs******************
    def __center(self, window_id):
        cp = QDesktopWidget().availableGeometry().center()
        qr = self.__windows[window_id].frameGeometry()
        qr.moveCenter(cp)
        self.__windows[window_id].move(qr.topLeft())

    def __set_back(self, html):
        url = QUrl(QUrl.fromLocalFile(os.path.abspath(html)))
        self.__uis['login'].background_l.load(url)
        self.__uis['login'].background_r.load(url)

    def __show(self, window_id):
        '''
        if window_id == 'login':
            self.__uis['login'].background_l.show()
        '''
        self.__windows[window_id].show()
    
    def hide(self, window_id):
        self.__windows[window_id].hide()

    def update_window(self, ops:dict, window_id):
        pass

    def changeIcon(self):
        print('Change ICON')
        time.sleep(0.5)
        email = self.__uis['login'].email_cbox.currentText()
        self.__uis['login'].usericon.setPixmap(getpixmap(email, 100))

    def set_dafault(self, default_user):
        print('Emit')
        print(default_user)
        if isinstance(default_user, int):
            default_user = self.__config['Users'][list(self.__config['Users'].keys())[default_user]]
            pass
        elif isinstance(default_user, str):
            default_user = self.__config['Users'][default_user]
        
        print('Set Default')
        self.__uis['login'].email_cbox.setCurrentText(default_user['Email'])

        self.__uis['login'].input_name_l.setText(default_user['NickName'])
        self.__uis['login'].input_email_pass_l.setText(default_user['Email Pass'])
        self.__uis['login'].input_server_email_l.setText(default_user['Server Email'])
        self.__uis['login'].input_server_addr_l.setText(default_user['Server Addr'])

        #self.__uis['login'].usericon.setPixmap(getpixmap('1.jpg', 100))



    def __new_contacts_groupbox(self, box_items:dict, box_type):
        if box_type == 'c':
            self.__contact_box_layouts['contacts_box'] = QVBoxLayout(self.__uis['main'].contacts_box)
            self.__contact_box_layouts['contacts_box'].setContentsMargins(0, 0, 0, 0)
            self.__contact_box_layouts['contacts_box'].setAlignment(Qt.AlignTop)
            for id in box_items.keys():
                label_text = json.dumps(box_items[id])
                c_label = ILabel(info=label_text)
                c_label.setText(gen_uuid(box_items[id]['name'], box_items[id]['id']))
                c_label.bindDoubleClicked(self.active_newchat)
                self.__contact_box_layouts['contacts_box'].addWidget(c_label)
        elif box_type == 'g':
            self.__contact_box_layouts['groups_box'] = QVBoxLayout(self.__uis['main'].groups_box)
            self.__contact_box_layouts['groups_box'].setContentsMargins(0, 0, 0, 0)
            self.__contact_box_layouts['groups_box'].setAlignment(Qt.AlignTop)
            for id in box_items.keys():
                _text = json.dumps(box_items[id])
                c_btu = IToolButton(info=_text)
                c_btu.setText(gen_uuid(box_items[id]['name'], box_items[id]['id']))
                c_btu.bindClicked(self.active_newchat)
                self.__contact_box_layouts['groups_box'].addWidget(c_btu)
        elif box_type == 'b':
            self.__contact_box_layouts['black_box'] = QVBoxLayout(self.__uis['main'].black_box)
            self.__contact_box_layouts['black_box'].setContentsMargins(0, 0, 0, 0)
            self.__contact_box_layouts['black_box'].setAlignment(Qt.AlignTop)
            for id in box_items.keys():
                _text = json.dumps(box_items[id])
                c_btu = IToolButton(info=_text)
                c_btu.setText(gen_uuid(box_items[id]['name'], box_items[id]['id']))
                self.__contact_box_layouts['black_box'].addWidget(c_btu)
        pass

    def search_table_index(self, window_id, val):
        results = self.__uis[window_id].file_table.findItems(val, Qt.MatchExactly)
        return self.__uis[window_id].file_table.indexFromItem(results[0])
        pass

    def flush_file_table(self, window_id, f:dict):
        rowPosition = self.__uis[window_id].file_table.rowCount()
        print('File')
        print(rowPosition)
        print(f)
        self.__uis[window_id].file_table.insertRow(rowPosition)
        name = QTableWidgetItem(f['content'])
        if isinstance(f['size'], int):
            f['size'] = str(f['size'])
        size = QTableWidgetItem(f['size'])
        down = IPushButton(info=f)
        down.setText('Click')
        down.bindClicked(self.active_download)
        self.__uis[window_id].file_table.setItem(rowPosition, 2, name)
        self.__uis[window_id].file_table.setItem(rowPosition, 1, size)
        self.__uis[window_id].file_table.setCellWidget(rowPosition, 0, down)

    def __new_file_table(self, window_id:str):
        window_info = window_id.split(' ')
        name = window_info[0]
        uid = window_info[1][1:-1]
        our_files = msgs[window_id]['file']
        self.__uis[window_id].file_table.setHorizontalHeaderLabels(['Download', 'Size', 'click'])
        self.__file_table_layouts[window_id] = QHBoxLayout()
        self.__file_table_layouts[window_id].addWidget(self.__uis[window_id].file_table)
        for f in our_files:
            self.flush_file_table(window_id, f)
        self.__uis[window_id].file_table.resizeColumnsToContents()
        pass

    def flush_new_record(self, window_id, msg):
        print(msg)
        sayer = msg['src']
        name = self.__leveldb_conn.Get(sayer)
        if len(name) > 0:
            print(name)
            name = name.decode('utf_8')
        print('res:', name)
        m_type = msg['type']
        content = msg['content']
        say_label = ILabel()
        say_label.setText(name + ':')
        say_label.setStyleSheet('background-color: rgb(171, 255, 188);')
        self.__chat_layouts[window_id].addWidget(say_label)
        if m_type == 'file':
            f_label = ILabel(info=msg)
            f_label.setText('file:' + content)
            self.__chat_layouts[window_id].addWidget(f_label)
            pass
        elif m_type == 'text':
            t_label = ILabel(info=content)
            t_label.setText(content)
            self.__chat_layouts[window_id].addWidget(t_label)
            pass
        else:
            p_label = ILabel(info=content)
            content = self.__folder + 'pics/' + content.split('/')[-1]
            print('图片路径', content)
            p_label.setPixmap(msg_pic(content, 70))
            self.__chat_layouts[window_id].addWidget(p_label)
            pass
        pass

    def __new_records_widget(self, window_id:str):
        window_info = window_id.split(' ')
        name = window_info[0]
        uid = window_info[1][1:-1]
        '''
        records = self.__tinydb_conn.search()

        w = QWidget()
        # w.setAutoFillBackground(True)
        w.setStyleSheet('background-color: rgb(170, 255, 127);')
        w.setGeometry(QRect(0, 0, 631, 471))
        
        qscrollarea = QScrollArea(w)
        qscrollarea.setWidgetResizable(True)
        qscrollarea.setGeometry(QRect(20, 10, 591, 441))
        # qscrollarea.addScrollBarWidget(w)
        # qscrollarea.setWidget(w)
        
        groupbox4 = QGroupBox()
        groupbox4.setStyleSheet('background-color: rgb(255, 255, 255);')
        groupbox4.setGeometry(QRect(20, 10, 591, 441))
        '''
        print('ID:', window_id)
        self.__chat_layouts[window_id] = QVBoxLayout(self.__uis[window_id].msgs_box)
        # vlayout2.setMargin(10)
        self.__chat_layouts[window_id].setContentsMargins(10, 10, 10, 10)
        self.__chat_layouts[window_id].setAlignment(Qt.AlignTop)
        '''
        png = QPixmap('./ICHAT/pics/1.jpg')
        for i in range(50):
            if i % 2 == 0:
                label1 = ILabel()
                label1.setText("No.%d" % i)
            else:
                label1 = ILabel(info='pic')
                label1.setPixmap(png)
            print(i)
            vlayout4.addWidget(label1)
            #qscrollarea.setWidget(groupbox4)
        '''
        print('>???')
        print(msgs.keys())
        our_msgs = msgs[self.__cur_window_id]['msg']
        for msg in our_msgs:
            print(msg)
            self.flush_new_record(window_id, msg)
        #return w
    pass

    #********************************Active Functions******************************************
    def active_login(self):
        login_dict = {}
        login_dict['op'] = 'user/login'
        login_dict['method'] = 'Email'
        login_dict['extra'] = {}
        nickname = ''
        if self.__uis['login'].email_cbox.currentText():
            email = self.__uis['login'].email_cbox.currentText()
            nickname = self.__uis['login'].input_name_l.displayText()
            email_pass = self.__uis['login'].input_email_pass_l.text()
            server_email = self.__uis['login'].input_server_email_l.displayText()
            server_addr = self.__uis['login'].input_server_addr_l.displayText()
            remember = self.__uis['login'].remember_btu.isChecked()
            #init isocket
            login_dict['src'] = email
            login_dict['des'] = server_email
            nounce = gen_nounce(email)
            login_dict['extra']['last addr'] = server_addr
            login_dict['extra']['nounce'] = nounce
            self.__email = email
            self.__server_addr = server_addr

            if self.__email == '781442859@qq.com':
                self.__folder = 'ICHAT/'
            else:
                self.__folder = 'ICHAT1/'

            self.__tinydb_conn = TinyDBConnection(self.__folder  + 'db/tinydb.json')
            self.__leveldb_conn = LevelDBConnection(self.__folder + 'db/leveldb')
            if not self.__registered:
                self.SetSockets(email_pass=email_pass)

        print(login_dict)
        if remember:
            print(email_pass)

        login_dict['nickname'] = nickname
        self.__ui_main(login_dict)
        index = 100
        self.__signals['user/login'].emit(1)
        while not self.__online and index > 0:
            time.sleep(0.1)
            index -= 1
        # self.__prepare(dict)

        if self.__online:
            self.__registered = True
            self.__windows['main'].show()
            if self.__email == '2582783208@qq.com':
                self.__cur_window_id = 'fanjianzhong <781442859@qq.com>'
            else:
                self.__cur_window_id = 'zhongtao <2582783208@qq.com>'
            print('Self UID', gen_uuid(nickname, self.__email))
            self.__gpg_obj = IGPG(gen_uuid(nickname, self.__email), passphrase='sustech2017')
            print('登录成功')
            print('当前聊天用户')
            print(self.__cur_window_id)
            self.__chat_isocket.start()
            self.__runner.start()
        else:
            print('登录失败')

    def active_register(self):
        register_dict = {}
        register_dict['extra'] = {}
        if self.__uis['login'].input_name_r:
            nickname = self.__uis['login'].input_name_r.displayText()
            email = self.__uis['login'].input_email_r.displayText()
            email_pass = self.__uis['login'].input_email_pass_r.text()
            server_email = self.__uis['login'].input_server_email_r.displayText()
            self.__email = email
        if not self.__online:
            self.SetSockets(email_pass=email_pass)
        register_dict['src'] = email
        register_dict['des'] = server_email
        register_dict['extra']['nickname'] = nickname
        register_dict['extra']['gpgid'] = 'hufshdu'
        nounce = gen_nounce(email)
        register_dict['extra']['nounce'] = nounce
        print(register_dict)

        index = 100
        self.__signals['user/register'].emit(12234)
        while not self.__registered and index > 0:
            time.sleep(0.1)
            index -= 1
        # self.__prepare(dict)
        if self.__registered:
            print('注册成功')
            self.__uis['login'].register_result.setText('注册成功!')
        else:
            print('注册失败')
            self.__uis['login'].register_result.setText('注册失败!')

    def active_logout(self):
        keys = [key for key in self.__windows.keys()]
        for window_id in keys:
            print(len(keys))
            
            if window_id != 'login':
                print(window_id)
                self.__windows[window_id].hide()
                del self.__uis[window_id]
                del self.__windows[window_id]
        self.__windows['login'].show()

    def active_newchat(self, window_info:dict):
        '''
        window_info: {name, type:{c | g}, email/groupid}
        '''
        if isinstance(window_info, str):
            window_info = json.loads(window_info)
            name = window_info['name']
            uid = window_info['id']
            window_type = window_info['type']
            window_id = gen_uuid(name, uid)

        print('Open New Chat')
        print(window_id)
        new_window = IFrame(window_id=window_id)
        #new_window.bindEntered(self.set_cur_window_id)
        #new_window.bindLeaved(self.reset_cur_window_id)
        new_window.bindClosed(self.active_closechat)
        new_ui = None
        if window_type == 'g':
            new_ui = Ui_GroupWindow()
            new_ui.setupUi(new_window)
            new_ui.group_icon.setPixmap(getpixmap(uid, 70))
            new_ui.group_id.setText(uid)
            new_ui.group_name.setText(name)
            print('初始化用户界面')
            
        elif window_type == 'c':
            new_ui = Ui_ContactWindow()
            new_ui.setupUi(new_window)
            new_ui.contact_icon.setPixmap(getpixmap(uid, 70))
            new_ui.contact_email.setText(uid)
            new_ui.contact_nickname.setText(name)
            print('初始化群聊界面')

        if new_ui:
            self.__windows[window_id] = new_window
            self.__uis[window_id] = new_ui
            self.__new_records_widget(window_id)
            self.__new_file_table(window_id)
            if window_type == 'c':
                self.__bind_active_funcs(window_id, CONTACT_CHAT, True)
            elif window_type == 'g':
                self.__bind_active_funcs(window_id, GROUP_CHAT, True)
            if window_id != 'main':
                self.__windows[window_id].show()
        
    def active_closechat(self, window_id):
        print(self.__windows.keys())
        if window_id in self.__windows.keys():
            del self.__windows[window_id]
        print(self.__windows.keys())

    def active_download(self, file_info):
        if isinstance(file_info, str):
            file_dict = json.loads(file_info)
        else:
            file_dict = file_info
        print('Downloading')
        print(file_dict)
        sender = file_dict['src']
        name = self.__leveldb_conn.Get(sender)
        if len(name) > 0:
            name = name.decode('utf_8')
        window_id = gen_uuid(name, sender)
        index = self.search_table_index(window_id, file_dict['content'])
        print(index.row())
        finished = True
        print()
        if finished:
            '''
            item = self.__uis[window_id].file_table.takeItem(index.row(), 1)
            item.setText('Finish')
            item.disconnect()
            self.__uis[window_id].file_table.setItem(index.row(), 1, item)
            '''
            print('Finished')
        pass

    def set_cur_window_id(self, window_id):
        print('Set Cur id', window_id)
        self.__cur_window_id = window_id

    def reset_cur_window_id(self):

        print('del id', self.__cur_window_id)
        self.__cur_window_id = None

    def active_c_msg_text(self):
        #window_id = self.__cur_window_id
        print('Cur id', self.__cur_window_id)
        to_email = self.__uis[self.__cur_window_id].contact_email.text()
        to_name = self.__uis[self.__cur_window_id].contact_nickname.text()

        if self.__cur_window_id:
            text = self.__uis[self.__cur_window_id].input_text.toPlainText()
            self.__uis[self.__cur_window_id].input_text.clear()
        header = {}
        header['content'] = {}
        header['des'] = to_email
        header['op'] = 'msg/text'
        header['method'] = 'Email'
        header['status'] = -1
        header['type'] = 'c'
        header['content']['src'] = self.__email
        header['content']['des'] = to_email
        header['content']['type'] = 'text'
        header['content']['content'] = text
        msg = {'src':self.__email, 'des':to_email, 'type':'text', 'content':text}
        self.flush_new_record(self.__cur_window_id, msg)
        self.__prepare(header)
        pass

    def active_c_msg_pic(self):
        window_id = self.__cur_window_id
        print('Cur id', self.__cur_window_id)
        to_email = self.__uis[self.__cur_window_id].contact_email.text()
        to_name = self.__uis[self.__cur_window_id].contact_nickname.text()

        pic_path = QFileDialog.getOpenFileName(self.__windows[self.__cur_window_id], "Open file", ".", "Images (*.png *.xpm *.jpg)")
        pic_name = pic_path[0].split(PathSep)[-1]
        header = {}
        header['content'] = {}
        header['des'] = to_email
        header['op'] = 'msg/pic'
        header['method'] = 'Email'
        header['status'] = -1
        header['type'] = 'c'
        header['content']['src'] = self.__email
        header['content']['des'] = to_email
        header['content']['type'] = 'pic'
        header['content']['content'] = pic_name
        msg = {'src': self.__email, 'des': to_email, 'type': 'pic', 'content': pic_name}
        self.flush_new_record(self.__cur_window_id, msg)
        self.__prepare(header, pic_path[0].encode('utf_8'))

        pass

    def active_c_msg_file(self, window_id):
        window_id = self.__cur_window_id
        print('Cur id', self.__cur_window_id)
        to_email = self.__uis[self.__cur_window_id].contact_email.text()
        to_name = self.__uis[self.__cur_window_id].contact_nickname.text()

        file_path = QFileDialog.getOpenFileName(self.__windows[self.__cur_window_id], "Open file", ".",
                                               "All Files (*)")
        file_name = file_path[0].split(PathSep)[-1]
        header = {}
        header['content'] = {}
        header['des'] = to_email
        header['op'] = 'msg/file'
        header['method'] = 'Email'
        header['status'] = -1
        header['type'] = 'c'
        header['content']['src'] = self.__email
        header['content']['des'] = to_email
        header['content']['type'] = 'file'
        header['content']['content'] = file_name
        msg = {'src': self.__email, 'des': to_email, 'type': 'file', 'content': file_name}
        self.flush_new_record(self.__cur_window_id, msg)
        self.__prepare(header, file_path[0].encode('utf_8'))
        pass

    def active_c_msg_video(self, window_id):
        text = self.__uis[window_id].input_text.toPlainText()
        print(text)
        pass

    def active_g_msg_text(self, window_id):
        text = self.__uis[window_id].input_text.toPlainText()
        print(text)
        pass

    def active_g_msg_pic(self, window_id):
        text = self.__uis[window_id].input_text.toPlainText()
        print(text)
        pass

    def active_g_msg_file(self, window_id):
        text = self.__uis[window_id].input_text.toPlainText()
        print(text)
        pass

    #****************bind Funcs*******************
    def __bind_active_funcs(self, window_id, funcs_dict, ibtu=False):
        for key in funcs_dict:
            getattr(self.__uis[window_id], key).clicked.connect(getattr(self, funcs_dict[key]))

    #***************** funcs in client and server (same)***************************

    def SetGPG(self, uuid: str, passpharse=None):
        #self.__gpg_obj = IGPG(uuid, passpharse)
        pass


    def SetSockets(self, email_pass):
        self.__chat_isocket = ISocket(uuid=self.__email, email_pass=email_pass, server=False)
        self.__chat_isocket.bind(('0.0.0.0', CHATPORT))
        self.__runner.set_isocket(self.__chat_isocket)
        self.__runner.bind(self.__resolve)
        #self.__chat_isocket.connect((self.__server_addr, CHATPORT), self.__email, True)
        self.__p2p_isocket = ISocket(uuid=self.__email, only='S', server=True)
        self.__p2p_isocket.bind(('0.0.0.0', P2PPORT))
        #self.__p2p_isocket.connect((self.__server_addr, P2PPORT), self.__email, True)
        self.__video_isocket = ISocket(uuid=self.__email, only='S', server=True, pack=False)
        self.__video_isocket.bind(('0.0.0.0', VIDEOPORT))
        #self.__video_isocket.connect((self.__server_addr, VIDEOPORT), self.__email, True)
        pass


    def SetDB(self, dbpath=''):
        '''
        if dbpath == '':
            dbpath = ''
        self.__tinydb_conn = TinyDBConnection(dbpath)
        self.__leveldb_conn = LevelDBConnection(dbpath)
        '''
        pass

    def SetIP(self):
        self.__ipinfo = ip.GetIPInfo()
        pass


    def GetDaemon(self):
        return self.__daemon
        pass


    def GetProtocol(self):
        return self.__protocol




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
            args['protocol'] = 'ICHAT/' + str(1.1)

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
            nickname = self.__leveldb_conn.Get(des).decode('utf_8')  # user name | group name
            uid = GetUid(nickname, des)
            recipient_keyid = self.__gpg_obj.get_keyid(uid)
            print('接收者keyid',recipient_keyid)
            #header['seqnum'] = self.__seqnums[des]
            header['seqnum'] = self.__out_counts
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

        self.__chat_isocket.send(header, payload, False, method)
        self.__out_counts += 1
        pass

    def __resolve(self, packet_index):
        print('Call: ', inspect.stack()[0][3])
        '''
        收到从ISocket传上来的header(dict)和payload,通过header里的Op字段选择对应的函数处理并把header和payload作为参数传递过去
        '''
        global packet_buf, buf_lock
        buf_lock.acquire()
        packet = packet_buf[packet_index]
        header = packet[0]
        payload = packet[1]
        del packet_buf[packet_index]
        buf_lock.release()
        protocol = header['protocol']
        sign = header['sign']
        des = header['des']
        if protocol not in VALIED_VERSIONS:
            print('Version Error, valied versions: ', json.dumps(VALIED_VERSIONS))
            return False
        print('extra')
        print(header['extra'].encode('utf_8'))

        print(type(header['extra']))
        print(header['extra'].split(': '))
        print(len(header['extra'].split(': ')))
        print(len(header['extra'].split(': ')[2]))
        print(header['extra'].split(': ')[2][:-1])
        extra_arr = header['extra'].split(': ')
        header['extra'] = {}
        header['extra']['type'] = extra_arr[1][1]
        extra_arr[2] = extra_arr[2][2:]
        extra_arr[2] = extra_arr[2].replace('\\n', '\n')
        extra_arr[2] = extra_arr[2].encode('utf_8')
        header['extra']['content'] = extra_arr[2]
        if des == self.__email:
            content = self.__gpg_obj.decrypt(header['extra']['content'], sign=True)
            print('解密后')
            print(content)
            header['extra']['content'] = json.loads(content.decode('utf_8'))
        select = header['op'].split('/')[0]  # msg | user | file
        op_type = header['op'].split('/')[1]
        func_name = 'deal_' + select + '_' + op_type
        self.__packet_buf[packet_index] = (header, payload)
        self.__signals[header['op']].emit(packet_index)
        #threading.Thread(target=getattr(self, func_name), args=([header, payload])).start()
        pass

    def __load_folder(self):
        '''
        加载下载目录内的文件信息
        '''
        print('Download folder: ', self.__folder)
        self.__fileshare_obj = FileCenter(self.__folder)
        self.__fileshare_obj.Initfiles()
        pass


    def deal_msg_text(self, packet_index):
        '''
        服务器收到
        '''
        header = self.__packet_buf[packet_index][0]
        payload = self.__packet_buf[packet_index][1]
        src = header['src']
        des = header['des']
        status = header['status']
        seqnum = header['seqnum']
        msg_type = header['extra']['type']  # g(group) | (user)
        msg = header['extra']['content']
        content = msg['content']
        print('Get Text MSG')
        print(msg)
        #content = header['extra']['content']
        # status: 0发送失败, 1是是接收， -1是发送请求
        if des == self.__email:
            if status != 0:
                document = {}
                if status == 1:
                    document = {'src': des, 'des': src, 'type': 'text', 'content': content, 'seqnum': seqnum}
                else:
                    document = {'src': src, 'des': des, 'type': 'text', 'content': content, 'seqnum': seqnum}

                self.__tinydb_conn.insert(document, src)
                if src in self.__cur_window_id:
                    print('刷新消息到聊天窗口')
                    print('text:', content)
                    self.flush_new_record(self.__cur_window_id, msg)
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

    def deal_msg_pic(self, packet_index):
        '''
        content: 图片文件名
        payload: 图片数据
        '''
        header = self.__packet_buf[packet_index][0]
        payload = self.__packet_buf[packet_index][1]
        src = header['src']
        des = header['des']
        status = header['status']
        seqnum = header['seqnum']
        msg_type = header['extra']['type']
        msg = header['extra']['content']
        content = msg['content']
        print('Get PIC MSG')
        print(msg)
        if des == self.__email:
            if status != 0:
                pic_path = self.__folder + '/pics/' + content.split('/')[-1]
                with open(pic_path, 'wb+') as f:
                    print('Output to ', pic_path)
                    f.write(payload)
                    pass

                document = {}
                if status == 1:
                    document = {'src': des, 'des': src, 'type': 'pic', 'content': content, 'seqnum': seqnum}
                else:
                    document = {'src': src, 'des': des, 'type': 'pic', 'content': content, 'seqnum': seqnum}

                self.__tinydb_conn.insert(document, src)
                if src in self.__cur_window_id:
                    print('刷新消息到聊天窗口')
                    print('pic:', content)
                    self.flush_new_record(self.__cur_window_id, msg)
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

    def deal_msg_file(self, packet_index):
        '''
        content: 图片文件名
        payload: 图片数据
        '''
        header = self.__packet_buf[packet_index][0]
        payload = self.__packet_buf[packet_index][1]
        src = header['src']
        des = header['des']
        status = header['status']
        seqnum = header['seqnum']
        msg_type = header['extra']['type']
        msg = header['extra']['content']
        content = msg['content']
        print('Get Text MSG')
        print(msg)
        #content = header['extra']['content']
        if des == self.__email:
            if status != 0:
                file_path = self.___folder + '/files/' + content.split('/')[-1]
                with open(file_path, 'wb+') as f:
                    print('Output to ', file_path)
                    f.write(payload)
                    pass
                document = {}
                if status == 1:
                    document = {'src': des, 'des': src, 'type': 'pic', 'content': content, 'seqnum': seqnum}
                else:
                    document = {'src': src, 'des': des, 'type': 'pic', 'content': content, 'seqnum': seqnum}

                self.__tinydb_conn.insert(document, src)
                if src in self.__cur_window_id:
                    print('刷新消息到聊天窗口')
                    print('pic:', content)
                    self.flush_new_record(self.__cur_window_id, msg)
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

    def deal_msg_video(self, packet_index:int):
        header = self.__packet_buf[packet_index][0]
        payload = self.__packet_buf[packet_index][1]
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

    # ********************client funcs*****************
    def __init_chatui(self):
        pass

    def __register_files(self):
        '''
        调用__load_folder后得到
        '''
        pass

    def __initvars(self, iargs: dict):
        self.__email = iargs['email']
        self.__nickname = iargs['nickname']
        self.__cur_contact = None  # 当前聊天窗口联系人邮箱
        self.__notify_list = {}
        pass

    #client packet deal funcs
    def deal_msg_file(self, packet_index:int):
        '''
        content: 文件md5值
        '''
        header = self.__packet_buf[packet_index][0]
        payload = self.__packet_buf[packet_index][1]
        src = header['src']
        des = header['des']
        seqnum = header['seqnum']
        status = header['status']
        filemd5 = header['extra']['md5']
        filename = header['extra']['name']
        msg_type = header['extra']['type']
        content = header['extra']['content']
        if status == -1:
            document = {'src':src, 'des':des, 'seqnum':seqnum, 'type':'file', 'name':filename, 'md5':filemd5}
            self.__tinydb_conn.insert(document, src)
            if src == self.__cur_contact:
                print('刷新消息到聊天窗口')
                print('file:%s', content)
        elif status == 0:
            print('先上传文件到服务器')
            tmp_conn = self.__p2p_isocket.connect(other_addr=(self.__server_addr, P2PPORT), keepalive=0)
            self.__fileshare_obj.Upload(tmp_conn, filemd5)
            print('从缓存中拿到该文件对象的信息，打包上传')
            print('上传玩从temp目录删除')
        else:
            print('服务器已存在该文件')
            print('从temp目录中删除该文件')
            self.__fileshare_obj.DelFile(filemd5)
        pass


    def deal_user_register(self, status, error=''):
        status = 1
        if status == 1:
            print('注册成功')
            self.__registered = True
        else:
            print('注册失败:')
        pass

    # client
    def deal_user_login(self, status):
        status = 1
        if status == 1:
            print('登录成功')
            self.__online = True
        else:
            print('登录失败')
        pass

    def deal_user_logout(self, status, error=''):
        if status == 1:
            print('注销成功')
        else:
            print('注销失败:', error)
        pass
    def deal_user_addcontact(self, other, status, error=''):
        if status == 1:
            print('成功删除', other)
            print('从界面上删除', other)
            print('删除和%s 相关', other)
        pass

    def deal_user_delcontact(self, other, status, error=''):
        if status == 1:
            print('成功删除', other)
            print('从界面上删除', other)
            print('删除和%s 相关', other)
        pass

    def deal_user_addgroup(self, header:dict, payload:bytes):
        src = header['src']
        des = header['des']
        nickname = header['extra']['nickname']
        remark = header['extra']['remark']
        status = header['status']
        groupid = header['extra']['groupid']
        groupname = header['extra']['groupname']
        if status == -1:
            print('%s(%s) want to add group(%s)!(%s)' % (nickname, src, groupname, remark))
            #弹出窗口显示请求者的邮箱，用户名和备注信息，并赋值给agree
            document = {'src':src,'nickname':nickname,'type':'addgroup', 'remark':remark, 'groupname':groupname, 'groupid':groupid}
            self.__tinydb_conn.insert(document, 'notify')
        elif status == 1:
            print('%s(%s) 同意添加群(%s)' % (nickname, src, groupname))
            self.__contacts[groupid] = groupname
        else:
            print('%s(%s) 拒绝添加群(%s)' % (nickname, src, groupname))
        pass

    def deal_user_delgroup(self, groupid, status, error=''):
        if status == 1:
            print('成功删除', groupid)
            print('从界面上删除', groupid)
            print('删除和%s 相关', groupid)
        pass

    #************in client and server(same)
    def deal_file_upload(self, header:dict, payload:bytes):
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

    def deal_file_download(self, header:dict, payload:bytes):
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
                newsocket=self.__p2p_isocket.connect((ipinfo['outernal'], ipinfo['port']), src)
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
                    new_conn = self.__p2p_isocket.connect((ipinfo['internal'],P2PPORT), src)
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

    def deal_file_block(self, header:dict, payload:bytes):
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
            print('%s hasn\'t this block' % src )
        else:
            print('Get block from ', src)
            self.__fileshare_obj.AddBlock(block_info, payload, src)
        pass

    def deal_file_updatelist(self, header:dict, payload:bytes):
        src = header['src']
        des = header['des']
        filemd5 = header['extra']['md5']
        file_sharers = header['extra']['sharers']
        self.__fileshare_obj.UpdateList(filemd5, file_sharers)
        pass
