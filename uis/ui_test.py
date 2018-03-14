from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys
from uis.ui_modules import IToolButton, IToolButton
import json
class A:
    def setA(self, x):
        if not isinstance(x, str):
            x = json.loads(x)
        self.x = x
        print('Set')
        print(self.x)
    
def GetInfo(s):
    print('Get')
    print(s)

app = QApplication(sys.argv)

btu = IToolButton(info=["SUSTECH", "Heieeee"])
btu.setGeometry(QRect(170, 340, 109, 35))
btu.setObjectName("ibtu")
a = A()
btu.bindClicked(a.setA)

btu.show()
app.exec_()