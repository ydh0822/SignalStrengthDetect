#!/usr/bin/python3
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import *

import pyqtgraph as pg
import time
import random

global realtime_check
realtime_check = True

class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setLabel(text='Time(초)', units=None)
        self.enableAutoSIPrefix(False)

    def tickStrings(self, values, scale, spacing):
        """ override 하여, tick 옆에 써지는 문자를 원하는대로 수정함.
            values --> x축 값들   ; 숫자로 이루어진 Itarable data --> ex) List[int]
        """
        # print("--tickStrings valuse ==>", values)
        return [time.strftime("%H:%M:%S", time.localtime(local_time)) for local_time in values]

class ExampleWidget(QWidget):
    global realtime_check
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.pw = pg.PlotWidget(
            title="WiFi Signal Stregnth Detect",
            labels={'left': 'WiFi Signal Strength'},
            axisItems={'bottom': TimeAxisItem(orientation='bottom')}
        )

        self.setWindowTitle("H4uN : WiFi Signal Detect")
        self.setMinimumSize(800,800)
        button = QPushButton('Trace realtime', self)
        button.setCheckable(True)
        button.clicked.connect(self.btnRun_clicked)

        hbox = QVBoxLayout()
        hbox.addWidget(self.pw)
        hbox.addWidget(button)
        self.setLayout(hbox)

        self.pw.setYRange(-100, 0, padding=0)

        time_data = int(time.time())
        self.pw.setXRange(time_data - 10, time_data + 1)  # 생략 가능.

        self.pw.showGrid(x=True, y=True)
        # self.pw.enableAutoRange()
        self.pdi = self.pw.plot(pen='g')   # PlotDataItem obj 반환.

        self.plotData = {'x': [], 'y': []}

    def update_plot(self, new_time_data: int):
        data_sec = time.strftime("%S", time.localtime(new_time_data))
        # self.plotData['y'].append(-int(data_sec))
        Wifi_Signal_data = random.randint(-80, -20)
        self.plotData['y'].append(Wifi_Signal_data)
        self.plotData['x'].append(new_time_data)

        if (realtime_check):
            self.pw.setXRange(new_time_data - 80, new_time_data + 20, padding=0)   # 항상 x축 시간을 최근 범위만 보여줌.

        self.pdi.setData(self.plotData['x'], self.plotData['y'])

    def btnRun_clicked(self):
        global realtime_check
        QMessageBox.about(self, "message box", "Change Trace Mode!!!")
        realtime_check = not realtime_check

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    ex = ExampleWidget()

    def get_data():
        new_time_data = int(time.time())
        ex.update_plot(new_time_data)

    mytimer = QTimer()
    mytimer.start(500)  # 1초마다 갱신 위함...
    mytimer.timeout.connect(get_data)

    ex.show()
    sys.exit(app.exec_())