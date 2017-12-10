import sys, time, os, json
import webbrowser
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QMessageBox, QPushButton, QAction, qApp, QFileDialog, QLabel
from PyQt5.QtGui import QIcon, QPen, QPainter, QColor, QImage, QPixmap
from PyQt5.QtCore import pyqtSlot, Qt, QThread, pyqtSignal
from PyQt5.uic import loadUi
from find_path import *

class ThreadPath(QThread): 
    pathSignal = pyqtSignal(list)
    costSignal = pyqtSignal(float)
    def __init__(self, size, history):
        super(ThreadPath,self).__init__()
        self.size = size
        self.history = history
    def run(self):
        back, cost = search_path(self.size, self.history)
        self.pathSignal.emit(back)
        self.costSignal.emit(cost)


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
        self.result = 0
        self.each = self.length/self.size
        self.path = []
        self.step = 0
        self.allpath = []
        self.step_time = 0.5
        self.start = 0
        self.raws = [[1,2], [1,-2], [2,1], [2,-1], [-1,2], [-1,-2], [-2,1], [-2,-1]]
        self.btn_import.clicked.connect(self.btn_import_onclick)
        self.btn_start.clicked.connect(self.btn_start_onclick)
        self.btn_onestep.clicked.connect(self.btn_onestep_onclick)
        self.btn_return.clicked.connect(self.btn_return_onclick)
        self.btn_restart.clicked.connect(self.btn_restart_onclick)
        self.spin_size.valueChanged.connect(self.changesize)
        self.slider_clock.valueChanged.connect(self.changeValue)
        self.btn_save.clicked.connect(self.btn_save_onclick)
        self.image_label = QLabel(self)  
        self.image = QPixmap('./horse.png')   
        self.image_label.setPixmap(self.image)
        self.image_label.setGeometry(0, 0, 0, 0)
        self.image_label.setScaledContents(True)

        self.actionHistory.triggered.connect(self.menuHistory)
        self.actionGetCode.triggered.connect(self.menuCode)
        self.actionAboutAuthor.triggered.connect(self.menuAuthor)
    
    # 绘图函数
    def drawLines(self, qp):
        pen = QPen(Qt.darkBlue, 2, Qt.SolidLine)
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
        if back:
            self.result = 1
            self.allpath = back
            self.btn_start.setEnabled(True)
            if self.start:
                self.btn_start.setText('暂停游戏')
                self.callbackClock()
            else:
                self.btn_start.setText('开始环游')
                self.btn_onestep.setEnabled(True)
                self.onestep()
        else:
            self.start = 0
            QMessageBox.warning(self, '提示', '没有路径啦！')

    # 用时回调函数
    def callbackCost(self, cost):
        print(cost)
        self.statusBar().showMessage('路径查找成功！用时：%s秒' % cost)

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
        # 动画模式
        if self.result:
            p = self.allpath
        else:
            p = self.path
        save = {
            'mode': self.result,
            'size': self.size,
            'step': self.step,
            'allpath': p,
            'step_time': self.step_time
        }
        return json.dumps(save)

    @pyqtSlot()
    # 绘图时触发
    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawLines(qp)
        if self.path:
            for i in self.path[0:-1]:
                self.drawRectangles(qp, i)
            self.drawRectanglesActive(qp, self.path[-1])
        qp.end()

    # 点击提示全部触发
    def btn_start_onclick(self):
        # 没获取过提示
        if not self.result:
            if not self.path:
                QMessageBox.warning(self, "提示", "请点击棋盘选择初始位置")
                return False
            self.start = 1
            self.allpath = []
            self.thread = ThreadPath(self.size, self.path)
            self.thread.pathSignal.connect(self.callbackPath)
            self.thread.costSignal.connect(self.callbackCost)
            self.thread.start()
            self.btn_start.setEnabled(False)
            self.btn_onestep.setEnabled(False)
            self.statusBar().showMessage('路径搜索中...')
        # 获取过提示，点击暂停
        elif self.start:
            self.start = 0
            self.btn_start.setText('继续环游')
            self.btn_onestep.setEnabled(True)
        # 获取过提示，点击继续
        else:
            self.start = 1
            self.callbackClock()
            self.btn_start.setText('暂停游戏')
            self.btn_onestep.setEnabled(False)
    
    # 点击单步执行触发
    def btn_onestep_onclick(self):
        # 没获取过提示
        if not self.result:
            self.btn_start_onclick()
            self.start = 0
        # 获取过提示
        else:
            self.onestep()

    # 点击悔棋触发
    def btn_return_onclick(self):
        # 非自动环游状态下
        if not self.start:
            # 如果当前步数为0
            if not self.step:
                QMessageBox.warning(self, "提示", "没有棋可退啦！")
                return False
            # 如果走过棋
            else:
                self.step -= 1
                self.path = self.path[:-1]
                self.btn_start.setText('继续环游')
                self.btn_start.setEnabled(True)
                self.btn_onestep.setEnabled(True)
                if not self.step:
                    self.image_label.setGeometry(0, 0, 0, 0)
                self.repaint()
        else:
            QMessageBox.warning(self, "提示", "自动环游中，请暂停后重试！")
            return False

    # 点击重新开始触发
    def btn_restart_onclick(self):
        self.result = 0
        self.step = 0
        self.path = []
        self.allpath = []
        self.repaint()
        self.start = 0
        self.btn_start.setEnabled(True)
        self.btn_onestep.setEnabled(True)
        self.btn_start.setText('提示全部')
        self.image_label.setGeometry(0, 0, 0, 0)

    # 点击保存路径触发
    def btn_save_onclick(self):
        if not self.allpath:
            QMessageBox.warning(self, "提示", "请先开始游戏以获取路径")
            return False
        result= QMessageBox.information(self, "路径导出", 
            "路径预览：\n\n棋盘尺寸：%d\n当前步数：%d\n当前路径：%s\n\n确定导出路径？" % (self.size, self.step, self.path[:300]),
            QMessageBox.Yes | QMessageBox.No)
        if result == QMessageBox.Yes:
            filepath, ok = QFileDialog.getSaveFileName(self, "文件保存", "C:/knight_%s_%s.json" % (self.size, self.step), "JSON Files (*.json);;ALL Files (*)")
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
        fileName, filetype = QFileDialog.getOpenFileName(self, "选取文件", "C:/", "JSON Files (*.json);;All Files (*)")
        if not fileName:
            return False
        if not fileName.endswith('.json'):
            QMessageBox.warning(self, "提示", "文件格式有误")
            return False
        try:
            with open(fileName, 'r') as f:
                content = json.loads(f.read())
                mode = content['mode']
                size = content['size']
                step = content['step']
                allpath = content['allpath']
                step_time = content['step_time']
            self.result = mode
            self.size = size
            self.step = step
            self.each = self.length/self.size
            self.allpath = allpath
            self.path = self.allpath[0:self.step]
            self.step_time = step_time
            self.slider_clock.setValue(self.step_time)
            self.spin_size.setValue(self.size)
            QMessageBox.warning(self, "提示", "历史导入成功！")
            self.repaint()
        except Exception as e:
            QMessageBox.warning(self, "提示", "文件格式错误！")
            return False

    # 改变棋盘大小触发
    def changesize(self):
        new_size = self.spin_size.value()
        if self.step > 1:
            self.spin_size.setValue(self.size)
            if new_size != self.size:
                QMessageBox.warning(self, "提示", "游戏进行中，请重新开始再切换棋盘！")
            return False
        self.size = new_size
        self.each = self.length/self.size
        self.path = []
        self.step = 0
        self.result = 0
        self.allpath = []
        self.repaint()
        self.start = 0
        self.image_label.setGeometry(0, 0, 0, 0)


    # 改变动画速度触发
    def changeValue(self, value):  
        self.step_time = self.slider_clock.value()/10
        self.label_clock.setText(str(self.step_time))

    # 鼠标点击触发
    def mousePressEvent(self, e):
        # 非自动环游开始状态下
        if not self.start:
            # 如果鼠标点击在棋盘范围内
            if e.x() >= 20 and e.x() <= 520 and e.y() >= 40 and e.y() <= 540:
                mouse_x = int((e.y()-40)/self.each)
                mouse_y = int((e.x()-20)/self.each)
                new_pos = [mouse_x, mouse_y]
                # 如果不是第一步，则判断是否可以这么走
                if self.step:
                    # 如果点击的位置没走过
                    if new_pos not in self.path:
                        x_ = new_pos[0] - self.path[-1][0]
                        y_ = new_pos[1] - self.path[-1][1]
                        if [x_, y_] in self.raws:
                            self.path.append(new_pos)
                            self.result = 0
                            self.step += 1
                # 如果是第一次，则不限制
                else:
                    self.path.append(new_pos)
                    self.step += 1
                self.repaint()

    # 关闭窗口时触发
    def closeEvent(self, event):
        reply = QMessageBox.question(self,'确认退出','你确定要退出么？', QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
    
    # 历史版本弹窗
    def menuHistory(self):
        reply = QMessageBox.information(self,'历代版本','''
2017-11-23 V0.1.0 项目启动
2017-11-24 V0.2.0 完成算法设计（find_path.py）
2017-11-24 V0.3.0 完成简单的界面
2017-11-25 V0.3.1 UI线程和工作线程分离
2017-11-27 V0.3.2 实现自动播放
2017-11-28 V0.3.3 实现改变速度
2017-11-28 V0.3.4 实现改变初始位置
2017-12-01 V0.4.0 重写部分逻辑，实现暂停和单步执行功能
2017-12-02 V0.5.0 导出功能，可将路径导出JSON文件
2017-12-05 V0.6.0 导入功能编写完成
2017-12-06 V0.6.1 路径导出前展现当前路径信息
2017-12-06 V0.6.2 加入马的图片
2017-12-06 V1.0.0 基本版完成
2017-12-06 V1.0.1 改变位置时可在棋盘上实时显示
2017-12-06 V1.1.0 初始位置可用鼠标点击选择
2017-12-06 V1.2.0 解决了部分电脑运行速度极慢的bug
2017-12-07 V1.2.1 完善菜单
2017-12-09 V1.2.2 继续完善菜单
2017-12-09 V1.2.3 棋盘大小可调节为6-30间任意偶数
2017-12-09 V1.2.4 路径查找后在底部显示运算时间
2017-12-09 V2.0.0 全新下棋模式上线
2017-12-10 V2.0.1 bug修复

点击Yes查看Github详情
        ''', QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            url = 'https://github.com/yuanyuanzijin/knight-gui/commits/master'
            webbrowser.open(url, new=0, autoraise=True)

    # 源代码获取弹窗
    def menuCode(self):
        reply = QMessageBox.information(self,'源代码获取','本项目已开源，地址\nhttps://github.com/yuanyuanzijin/knight-gui\n\n点击yes使用浏览器打开', QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            url = 'https://github.com/yuanyuanzijin/knight-gui'
            webbrowser.open(url, new=0, autoraise=True)

    # 关于作者弹窗
    def menuAuthor(self):
        reply = QMessageBox.information(self,'关于作者','''
金禄渊，男，22岁，现就读于大连理工大学控制科学与工程学院。
土生土长的大连人，业余时间喜欢弹钢琴，写歌，打羽毛球等等。
爱好编程，经常使用Python和Javascript，喜欢做网页和APP。

个人Github主页：https://github.com/yuanyuanzijin，点击Yes访问
        ''', QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            url = 'https://github.com/yuanyuanzijin'
            webbrowser.open(url, new=0, autoraise=True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())