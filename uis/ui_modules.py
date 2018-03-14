from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import json, sys
from uis.ui_group import Ui_GroupWindow


class ILabel(QLabel):
    __sig_send = pyqtSignal(str, name='sig_send')
    def __init__(self,parent=None, info='ILabel'):
        super(ILabel, self).__init__(parent)
        self.__info = info
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
        self.contextMenu = QMenu(self)
        self.__actions = {}

        self.add_menu({'Echo': self.actionHandler})
        self.count = 0

    def mouseDoubleClickEvent(self,e):
        print('mouse double clicked') 
        info = self.__info
        if not isinstance(info, str):
            info = json.dumps(info)
        self.__sig_send.emit(info)

    def bindDoubleClicked(self, func):
        self.__sig_send.connect(func)

    def showContextMenu(self):
        self.count+=1  
        # 菜单显示前，将它移动到鼠标点击的位置    
        self.contextMenu.exec_(QCursor.pos()) #在鼠标位置显示  
        #self.contextMenu.show()    

    def add_menu(self, actions_dict:dict):
        # 创建QMenu
        for key in actions_dict:
            self.__actions[key] = self.contextMenu.addAction(key)
            if actions_dict[key]:
                self.__actions[key].triggered.connect(actions_dict[key])
            
    def actionHandler(self):
        print(self.__info)



class IPushButton(QPushButton):
    __sig_send = pyqtSignal(str, name='sig_send')
    def __init__(self, parent=None, info="IPushButton"):
        super(IPushButton, self).__init__(parent)
        self.__info = info
        self.clicked.connect(self.__sendinfo)

    def __sendinfo(self):
        info = self.__info
        if not isinstance(info, str):
            info = json.dumps(info)
        self.__sig_send.emit(info)
    
    def bindClicked(self, func):
        self.__sig_send.connect(func)

    def disconnect(self):
        self.__sig_send = None
        pass

    def setIcon(self, text=None, icon=None):
        info = json.loads(self.__info)
        if not icon and 'name' in info.keys():
            text = info['name'] + '< ' + info['id'] + '>'
            icon = 'icons/' + text + '.jpg'
        painter = QPainter()
        pixmap = QPixmap(icon)
        painter.drawPixmap(10, 10, pixmap, 50, 50, 50, 50)
        print(type(QRect))
        painter.drawText(QRect(), Qt.AlignLeft, text)

        return

class IToolButton(QToolButton):
    __sig_send = pyqtSignal(str, name='sig_send')

    def __init__(self, parent=None, info="IToolButton"):
        super(IToolButton, self).__init__(parent)
        self.__info = info
        #self.clicked.connect(self.__sendinfo)

    def mouseDoubleClickEvent(self, e):
        info = self.__info
        if not isinstance(info, str):
            info = json.dumps(info)
        self.__sig_send.emit(info)

    def bindClicked(self, func):
        self.__sig_send.connect(func)

class IFrame(QFrame):
    __sig_send = pyqtSignal(str, name='sig_send')
    __sig_send_1 = pyqtSignal(str, name='sig_send')
    __sig_leave = pyqtSignal(name='sig_leave')
    def __init__(self, parent=None, window_id="IFrame"):
        super(IFrame, self).__init__(parent)
        self.__window_id = window_id

    def closeEvent(self, e):
        self.__sig_send.emit(self.__window_id)

    '''
    def enterEvent(self, QEvent):
        self.__sig_send_1.emit(self.__window_id)
        pass

    def leaveEvent(self, QEvent):
        self.__sig_leave.emit()
    '''
    '''
    def bindLeaved(self, func):
        self.__sig_leave.connect(func)
    '''

    def bindClosed(self, func):
        self.__sig_send.connect(func)

    '''
    def bindEntered(self, func):
        self.__sig_send_1.connect(func)
    '''

class UITEST:
    def __init__(self):
        self.label = IToolButton(info="group")
        self.label.setGeometry(QRect(170, 340, 109, 35))
        self.label.setObjectName("ibtu")
        self.windows = {}

    def NewChat(self, args):
        if not isinstance(args, str):
            args = json.loads(args)
            window_id = args['window_id']
        else:
            window_id = args
        print('Set')
        print(window_id)
        chat_window = IFrame(info=window_id)
        chat_window.bindClosed(self.closeChat)
        chat_ui = Ui_GroupWindow()
        chat_ui.setupUi(chat_window)
        self.windows[window_id] = chat_window
        self.windows[window_id].show()

    def closeChat(self, window_id):
        print(self.windows.keys())
        if window_id in self.windows.keys():
            del self.windows[window_id]
        print(self.windows.keys())

    def show(self):
        self.label.show()
        self.label.bindClicked(self.NewChat)

    def closeChat(self, window_id):
        print(self.windows.keys())
        if window_id in self.windows.keys():
            del self.windows[window_id]
        print(self.windows.keys())

def Hello():
    print('Hello')

if __name__ == '__main__':
    def GetInfo(s):
        print('Get')
        print(s)

    app = QApplication(sys.argv)
    #IPushButton
    '''
    btu = IPushButton(info="SUSTECH")
    btu.setGeometry(QRect(170, 340, 109, 35))
    btu.setObjectName("ibtu")
    btu.bindClicked(GetInfo)
    btu.show()
    '''

    #ILabel
    ut = UITEST()
    ut.label.add_menu({'Hello':Hello})
    ut.show()
    app.exec_()