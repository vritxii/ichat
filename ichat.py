from datetime import datetime
import json
import threading

class Contact:
    __email_address = None
    __nickname = None

    def __init__(self, email_address, nickname):
        self.__email_address = email_address
        self.__nickname = nickname

    def change_nickname(self, nickname):
        '''
        修改联系人昵称
        '''
        self.__nickname = nickname

    def get_email(self):
        '''
        获取联系人邮箱/帐号
        '''
        return self.__email_address
        pass

class ChatRecord:
    __user__name = ''
    __time = None
    __record_type = None
    __record = None

    def __init__(self, user_name, record):
        self.__user__name = user_name
        self.__record = record
        self.__time = datetime.now()
        pass

    def check_time(self, p2p_time):
        return p2p_time <= self.__time

    def __str__(self):
        gen_record = None
        if self.__record_type == 'msg':
            gen_record = self.__user__name + '(' + str(self.__time.hour()) + str(self.__time.hour()) + str(self.__time.hour()) +'):\n' + self.__record
        else:
            gen_record = [self.__user__name + '(' + str(self.__time.hour()) + str(self.__time.hour()) + str(self.__time.hour()) +'):\n', self.__record]
        
        return gen_record
        pass

class Chat:
    __chat_name = None
    __session = None
    __chat_records = None

    def __init__(self, to="", session=Session(), ui = None):
        self.__chat_name = to
        self.__session = session
        self.__chat_records = []

    def get_chat_name(self):
        return self.__chat_name

    def send_msg(self, msg):
        pass

    def send_expression(self, expression):
        pass

    def send_file(self, file_info):
        pass

    def info(self):
        print("I am chat class")
        pass

    def download_file(self, file_info):
        pass

    def upload_file(self, file_info):
        pass
    

class UserChat(Chat):
    __mode = 'cs'
    __mark_p2p_start_time = None

    def __init__(self, to="", session=Session(), ui = None):
        super().__init__(to, session, ui)
        pass

    def switch_mode(self):
        if self.__mode == 'cs':
            self.__mode = 'p2p'
            self.__mark_p2p_start_time = datetime.now()

        else:
            self.__mode = 'cs'
            self.__mark_p2p_start_time = None
        pass

    def open_video_call(self):
        #check mode
        pass

    def clear_p2p_history(self):
        for k in self.__chat_records:
            if self.__chat_records[k].check_time(self.__mark_p2p_start_time):
                print('Delete record')
        pass

    def clear_history(self):
        self.__chat_records = []
        pass

    def info(self):
        print('I am user_chat')
        pass

class Member:
    __member_name = ''
    __email_address = ''
    __member_type = None  #Owner(1),User(0)
    __uuid = None
    __fingerprint = None

    def __init__(self, name, email_address, mtype=0):
        self.__member_name = name
        self.__email_address = email_address
        self.__member_type = mtype

    def get_name(self):
        return self.__member_name

    def get_email(self):
        return self.__email_address

    def get_member_type(self):
        return self.__member_type
    
    '''
    def change_type(self, other_member, mtype):
        if self.__member_type > other_member.get_member_type():
            return Member(other_member.get_name(), other_member.get_email(), mtype)
        print("No enough privilege")
        return other_member
        pass
    '''
        
class GroupChat(Chat):
    __member_type = None  #Owner(1),User(0)
    __access_token = None   #Group Session Token
    __members = {}
    __my_name = ''
    __records = []

    def __init__(self, session, members_json, to="Server", ui = None):
        '''
         args:
            to: 接收端
            session: 群聊天会话
            member_json: 群成员信息json字符串
            ui: 界面
        '''
        super().__init__(to, session, ui)
        self.load_info(members_json)
        pass

    def isowner(self):
        return self.__member_type == 1
        pass

    def load_info(self, member_json):
        '''
        member_json: 群成员信息json字符串
        '''
        members = json.loads(member_json)
        self.__member_type = members['type']
        self.__access_token = members['token']
        self.__members_of_group = members['members']
        pass

    def dumps(self):
        members_info = {'type':self.__member_type, 'token':self.__access_token, 'members': self.__members_of_group}
        return json.dumps(members_info)
        pass

    def clear_history(self):
        '''
        清除聊天记录
        '''
        self.__chat_records = []
        pass

    def update_members_list(self, member):
        '''
        更新联系人列表
        '''
        self.__members_of_group.append(member)
        pass

    def del_member(self, member):
        '''
        群主删除联系人
        '''
        if self.__member_type > member.get_member_type():
            del self.__members_of_group[member.get_email()]
        pass

    def disband(self):
        '''
        解散群
        '''
        if self.__member_type == 1:
            print('解散群成功')
        pass

    '''
    #设置和删除管理员
    def set_admin(self, member=Member()):
        if 2 == self.__member_type and self.__my_name != member.get_name():
            member=self.__members_of_group[member].change_type(member, 1)
            return
        print("No enough privilege")
            
    def rm_admin(self, member=Member()):
        if 2 == self.__member_type and self.__my_name != member.get_name():
            member=self.__members_of_group[member].change_type(member, 0)
            return
        print("No enough privilege")
    '''

    def info(self):
        print('I am group_chat')
        pass

import json

if __name__ == '__main__':
    print("IClasses")
    members_info = {'type':1, 'token':'sustc2017', 'members':'{}'}
    print(json.dumps(members_info))
    gc = GroupChat('sustc', json.dumps(members_info))
    print(gc.info())
    print(gc.get_chat_name())
    print(gc.dumps())
    print(gc.disband())
    print(gc.isowner())