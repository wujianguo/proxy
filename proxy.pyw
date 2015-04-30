#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
import sys, os.path
import pac_server
import shadowsocks.local

class Window(QtGui.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setWindowTitle(u"proxy")
        self.setGeometry(300,300,400,400)
        root_dir = sys.path[0]
        if not os.path.isdir(root_dir):
            root_dir = os.path.split(root_dir)[0]
        png_path = os.path.join(root_dir, "leave.ico")
        icon = QtGui.QIcon(png_path)
        self.setWindowIcon(icon)
        self.isTopLevel()
        self.trayIcon = QtGui.QSystemTrayIcon(self)
        self.trayIcon.setIcon(icon)
        self.trayIcon.show()
        # self.trayIcon.activated.connect(self.trayClick) #点击托盘 
        self.trayIcon.setToolTip(u"proxy") #托盘信息
        self.Menu() #右键菜单
    
    def Menu(self):
        # self.quitAction = QtGui.QAction(u"Exit", self,triggered=QtGui.qApp.quit)
        self.quitAction = QtGui.QAction(u"Exit", self,triggered=self.onQuit)
        self.trayIconMenu = QtGui.QMenu(self)
        self.trayIconMenu.addAction(self.quitAction)
        self.trayIcon.setContextMenu(self.trayIconMenu) #右击托盘 

    def onQuit(self):
        pac_server.asyncStop()
        shadowsocks.local.asyncStop()
        QtGui.qApp.quit()

    def closeEvent(self, event):
        if self.trayIcon.isVisible():
            self.hide()
#              self.trayIcon.setVisible(False)
            event.ignore()

    # def trayClick(self,reason):
    #     if reason==QtGui.QSystemTrayIcon.DoubleClick: #双击
    #         self.showNormal()
    #     elif reason==QtGui.QSystemTrayIcon.MiddleClick: #中击
    #         self.showMessage()
    #     else:
    #         pass
    def showMessage(self, msg):
        icon=QtGui.QSystemTrayIcon.Information
        self.trayIcon.showMessage("proxy", msg, icon)

def main():
    app = QtGui.QApplication(sys.argv)
    frm = Window()
    # frm.show()
    pac_server.asyncStart()
    shadowsocks.local.asyncStart()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()