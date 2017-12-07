import sys, time, os, json
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QMessageBox, QPushButton, QAction, qApp, QFileDialog, QLabel
from PyQt5.QtGui import QIcon, QPen, QPainter, QColor, QImage, QPixmap
from PyQt5.QtCore import pyqtSlot, Qt, QThread, pyqtSignal
from PyQt5.uic import loadUi
from find_path import *

class ThreadPath(QThread): 
    pathSignal = pyqtSignal(list)
    def __init__(self, size, history):
        super(ThreadPath,self).__init__()
        self.size = size
        self.history = history
    def run(self):
        result = search_path(self.size, self.history)
        self.pathSignal.emit(result)


class ThreadClock(QThread):
    clockSignal = pyqtSignal()
    def __init__(self, step_time):
        super(ThreadClock,self).__init__()
        self.step_time = step_time

    def run(self):
        time.sleep(self.step_time)
        self.clockSignal.emit()    


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('knight.ui', self)
        self.initUI()
    
    # 初始化函数
    def initUI(self):
        self.init_x = 20
        self.init_y = 40
        self.length = 500
        self.size = 8
        self.init_position = [0,0]
        self.each = self.length/self.size
        self.path = []
        self.step = 1
        self.allpath = []
        self.step_time = 0.5
        self.start = 0
        self.btn_import.clicked.connect(self.btn_import_onclick)
        self.btn_start.clicked.connect(self.btn_start_onclick)
        self.btn_onestep.clicked.connect(self.btn_onestep_onclick)
        self.btn_restart.clicked.connect(self.btn_restart_onclick)
        self.spin_x.valueChanged.connect(self.pos_changed)
        self.spin_y.valueChanged.connect(self.pos_changed)
        self.choices = [self.radio_6, self.radio_8, self.radio_10, self.radio_12]
        self.radio_6.clicked.connect(lambda:self.changesize(6))
        self.radio_8.clicked.connect(lambda:self.changesize(8))
        self.radio_10.clicked.connect(lambda:self.changesize(10))
        self.radio_12.clicked.connect(lambda:self.changesize(12))
        self.slider_clock.valueChanged.connect(self.changeValue)
        self.btn_save.clicked.connect(self.btn_save_onclick)
        self.image_label = QLabel(self)  
        self.image = QPixmap('./horse.png')   
        self.image_label.setPixmap(self.image)
        self.image_label.setGeometry(0, 0, 0, 0)
        self.image_label.setScaledContents(True)
        self.image_label.setGeometry(self.init_x, self.init_y, self.each-1, self.each-1)

        self.actionGetCode.triggered.connect(self.menuCode)
    
    # 绘图函数
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
        self.image_label.setGeometry(self.init_x+pos[1]*self.each, self.init_y+pos[0]*self.each, self.each-1, self.each-1)

    # 获取路径子线程执行后的回调函数
    def callbackPath(self, back):
        print(back)
        self.allpath = back
        self.btn_start.setEnabled(True)
        if self.start:
            self.btn_start.setText('暂停游戏')
            self.callbackClock()
        else:
            self.btn_start.setText('开始环游')
            self.btn_onestep.setEnabled(True)
            self.onestep()

    # 开启计时线程
    def clock(self):
        self.thread_time = ThreadClock(self.step_time)
        self.thread_time.clockSignal.connect(self.callbackClock)
        self.thread_time.start()
    
    # 计时子线程执行后的回调函数 & 自动环游执行显示函数
    def callbackClock(self):
        if self.start:
            if self.step < self.size*self.size:
                self.step += 1
                self.path = self.allpath[0:self.step]
                self.repaint()
                self.clock()
            else:
                self.start = 0
                self.btn_start.setText('游戏结束')
                self.btn_start.setEnabled(False)
                self.btn_onestep.setEnabled(False)

    # 单步执行显示函数
    def onestep(self):
        if self.step < self.size*self.size:
            self.step += 1
            self.path = self.allpath[0:self.step]
            self.repaint()
        if self.step >= self.size*self.size:
            self.start = 0
            self.btn_start.setText('游戏结束')
            self.btn_start.setEnabled(False)
            self.btn_onestep.setEnabled(False)

    # 获取保存内容函数
    def get_save_content(self):
        save = {
            'size': self.size,
            'step': self.step,
            'allpath': self.allpath,
            'step_time': self.step_time
        }
        return json.dumps(save)

    @pyqtSlot()
    # 绘图时触发
    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawLines(qp)
        if self.allpath:
            for i in self.path[0:-1]:
                self.drawRectangles(qp, i)
            self.drawRectanglesActive(qp, self.path[-1])
        qp.end()

    # 点击开始游戏触发
    def btn_start_onclick(self):
        if self.step == 1:
            self.start = 1
            self.path = []
            self.allpath = []
            init_X = self.spin_x.value()-1
            init_Y = self.spin_y.value()-1
            self.init_position = [init_X, init_Y]
            self.path.append(self.init_position)
            self.thread = ThreadPath(self.size, self.path)
            self.thread.pathSignal.connect(self.callbackPath)
            self.thread.start()
            self.btn_start.setText('搜索路径中...')
            self.btn_start.setEnabled(False)
            self.btn_onestep.setEnabled(False)
        elif self.start:
            self.start = 0
            self.btn_start.setText('继续环游')
            self.btn_onestep.setEnabled(True)
        else:
            self.start = 1
            self.callbackClock()
            self.btn_start.setText('暂停游戏')
            self.btn_onestep.setEnabled(False)
    
    # 点击单步执行触发
    def btn_onestep_onclick(self):
        if self.step == 1:
            self.btn_start_onclick()
            self.start = 0
        else:
            self.onestep()

    # 点击重新开始触发
    def btn_restart_onclick(self):
        self.step = 1
        self.path = []
        self.allpath = []
        self.repaint()
        self.start = 0
        init_X = self.spin_x.value()-1
        init_Y = self.spin_y.value()-1
        self.init_position = [init_X, init_Y]
        self.btn_start.setEnabled(True)
        self.btn_onestep.setEnabled(True)
        self.btn_start.setText('开始环游')
        self.image_label.setGeometry(self.init_x+self.init_position[1]*self.each, self.init_y+self.init_position[0]*self.each, self.each-1, self.each-1)

    # 点击保存路径触发
    def btn_save_onclick(self):
        if not self.allpath:
            QMessageBox.warning(self, "提示", "请先开始游戏以获取路径")
            return False
        result= QMessageBox.information(self, "路径导出", 
            "路径预览：\n\n棋盘尺寸：%d\n当前步数：%d\n当前路径：%s\n\n确定导出路径？" % (self.size, self.step, self.path),
            QMessageBox.Yes | QMessageBox.No)
        if result == 16384:
            filepath, ok = QFileDialog.getSaveFileName(self, "文件保存", "C:/", "JSON Files (*.json)")
            if not filepath:
                return False
            save_content = self.get_save_content()
            with open(filepath, 'w') as f:
                f.write(save_content)
            QMessageBox.warning(self, "提示", "路径保存成功！")
        else:
            return False

    # 点击导入路径触发
    def btn_import_onclick(self):
        if self.step > 1:
            QMessageBox.warning(self, "提示", "游戏进行中，请点击重新开始后再导入")
            return False
        fileName, filetype = QFileDialog.getOpenFileName(self, "选取文件", "C:/", "JSON Files (*.json)")
        if not fileName:
            return False
        if not fileName.endswith('.json'):
            QMessageBox.warning(self, "提示", "文件格式有误")
            return False
        try:
            with open(fileName, 'r') as f:
                content = json.loads(f.read())
                size = content['size']
                step = content['step']
                allpath = content['allpath']
                step_time = content['step_time']
            self.size = size
            self.step = step
            self.each = self.length/self.size
            self.allpath = allpath
            self.path = self.allpath[0:self.step]
            self.step_time = step_time
            self.slider_clock.setValue(self.step_time)
            if size == 6:
                self.radio_6.setChecked(True)
            elif size == 8:
                self.radio_8.setChecked(True)
            elif size == 10:
                self.radio_10.setChecked(True)
            else:
                self.radio_12.setChecked(True)
            self.init_position = allpath[0]
            self.spin_x.setValue(self.init_position[0] + 1)
            self.spin_y.setValue(self.init_position[1] + 1)
            self.spin_x.setMaximum(size)
            self.spin_y.setMaximum(size)
            QMessageBox.warning(self, "提示", "历史导入成功！")
            self.repaint()
        except Exception as e:
            QMessageBox.warning(self, "提示", "文件格式错误！")
            print(e)
            return False

    # 改变棋盘大小触发
    def changesize(self, size):
        if self.step > 1:
            QMessageBox.warning(self, "提示", "游戏进行中，请重新开始再切换棋盘！")
            return False
        self.size = size
        self.each = self.length/self.size
        self.path = []
        self.step = 1
        self.allpath = []
        self.repaint()
        self.start = 0
        self.spin_x.setMaximum(size)
        self.spin_y.setMaximum(size)
        self.pos_changed()

    # 改变动画速度触发
    def changeValue(self, value):  
        self.step_time = self.slider_clock.value()/10
        self.label_clock.setText(str(self.step_time))

    # 修改起始位置触发
    def pos_changed(self):
        init_X = self.spin_x.value()-1
        init_Y = self.spin_y.value()-1
        self.init_position = [init_X, init_Y]
        self.image_label.setGeometry(self.init_x+self.init_position[1]*self.each, self.init_y+self.init_position[0]*self.each, self.each-1, self.each-1)

    # 鼠标点击触发
    def mousePressEvent(self, e):
        if self.step <= 1:
            if e.x() >= 20 and e.x() <= 520 and e.y() >= 40 and e.y() <= 540:
                mouse_x = int((e.y()-40)/self.each)
                mouse_y = int((e.x()-20)/self.each)
                self.init_position = [mouse_x, mouse_y]
                self.spin_x.setValue(mouse_x+1)
                self.spin_y.setValue(mouse_y+1)

    # 关闭窗口时触发
    def closeEvent(self, event):
        reply = QMessageBox.question(self,'确认退出','你确定要退出么？', QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
    
    # 源代码获取弹窗
    def menuCode(self):
        mcode = QMessageBox()
        mcode.setWindowTitle("获取源代码")
        mcode.setTextFormat(self, "本项目已开源，地址\nhttps://github.com/yuanyuanzijin/knight-gui")
        mcode.setStyleSheet("font: 15pt; background-color:rgb(255, 255, 255)")
        mcode.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())