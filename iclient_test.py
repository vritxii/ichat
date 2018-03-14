import sys
import json
import os
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtWebEngineWidgets, QtCore

from iclient import IClient
if __name__ == '__main__':
    Daemon = 'C'
    print(Daemon)
    app = QApplication(sys.argv)
    c = IClient()
    c.Start()
    sys.exit(app.exec_())
    #dump_config(DEFAULT_CONFIG[Daemon])