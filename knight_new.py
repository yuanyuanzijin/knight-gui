import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QMessageBox, QPushButton, QAction, qApp
from PyQt5.QtGui import QIcon, QPen, QPainter, QColor
from PyQt5.QtCore import pyqtSlot, Qt, QThread, pyqtSignal
from PyQt5.uic import loadUi
from path import *

class ThreadPath(QThread): 
    pathSignal = pyqtSignal(list)  
    def __init__(self, size, history):  
        super(ThreadPath,self).__init__()  
        self.size = size
        self.history = history
    def run(self):  
        result = search_path(self.size, self.history)
        self.pathSignal.emit(result)
        

class App(QMainWindow):
    
    def __init__(self):
        super().__init__()
        loadUi('knight.ui', self)
        self.initUI()
        self.init_x = 20
        self.init_y = 40
        self.length = 400
        self.size = 8
        self.init_position = [4,5]
        self.each = self.length/self.size
        self.path = []
        self.step = 0
        self.allpath = []
        
    def initUI(self):
        self.btn_start.clicked.connect(self.btn_start_onclick)
        self.btn_restart.clicked.connect(self.btn_restart_onclick)
        self.choices = [self.radio_6, self.radio_8, self.radio_10, self.radio_12]
        self.radio_6.clicked.connect(lambda:self.changesize(6))
        self.radio_8.clicked.connect(lambda:self.changesize(8))
        self.radio_10.clicked.connect(lambda:self.changesize(10))
        self.radio_12.clicked.connect(lambda:self.changesize(12))

    @pyqtSlot()
    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawLines(qp)
        if self.path:
            for i in self.path[0:-1]:
                self.drawRectangles(qp, i)
            self.drawRectanglesActive(qp, self.path[-1])
        qp.end()

    def drawLines(self, qp):
        pen = QPen(Qt.black, 2, Qt.SolidLine)
        qp.setPen(pen)
        x = self.init_x
        y = self.init_y
        for i in range(self.size+1):
            qp.drawLine(x, y, x+self.length, y)
            y += self.each
        x = self.init_x
        y = self.init_y
        for i in range(self.size+1):
            qp.drawLine(x, y, x, y+self.length)
            x += self.each

    def drawRectangles(self, qp, pos):
        col = QColor(0, 0, 0)
        qp.setPen(col)
        qp.setBrush(QColor(100, 100, 100))
        qp.drawRect(self.init_x+pos[1]*self.each, self.init_y+pos[0]*self.each, self.each, self.each)

    def drawRectanglesActive(self, qp, pos):
        col = QColor(0, 0, 0)
        qp.setPen(col)
        qp.setBrush(QColor(147, 112, 219))
        qp.drawRect(self.init_x+pos[1]*self.each, self.init_y+pos[0]*self.each, self.each, self.each)

    def getpath(self):
        if not self.path:
            self.path.append(self.init_position)
        self.thread = ThreadPath(self.size, self.path)
        self.thread.pathSignal.connect(self.callbackPath)
        self.thread.start()  

    def callbackPath(self, back):    
        self.allpath = back

    def btn_start_onclick(self):
        self.step += 1
        self.path = self.allpath[0:self.step]
        self.repaint()
    
    def btn_restart_onclick(self):
        self.step = 0
        self.path = []
        self.repaint()

    def changesize(self, size):
        self.size = size
        self.each = self.length/self.size
        self.path = []
        self.step = 0
        self.allpath = []
        self.repaint()
        self.getpath()

    def closeEvent(self, event):
        reply = QMessageBox.question(self,'确认退出','你确定要退出么？', QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())