#!/usr/bin/env python3
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import *
from scapy.all import *

import pyqtgraph as pg
import time
import random
import sys

rssi = -100
mac = ""
interface =""
realtime_check = True

class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setLabel(text='Time(Seconds)', units=None)
        self.enableAutoSIPrefix(False)

    def tickStrings(self, values, scale, spacing):
        return [time.strftime("%H:%M:%S", time.localtime(local_time)) for local_time in values]

class ExampleWidget(QWidget):
    global realtime_check
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.pw = pg.PlotWidget(
            title="interface : "+str(interface) + "  |  WiFi mac : " + str(mac),
            labels={'left': str(mac)+' Signal Strength'},
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
        self.pw.setXRange(time_data - 10, time_data + 1)

        self.pw.showGrid(x=True, y=True)
        self.pdi = self.pw.plot(pen='g')   # PlotDataItem obj return

        self.plotData = {'x': [], 'y': []}

    def update_plot(self, new_time_data: int):
        data_sec = time.strftime("%S", time.localtime(new_time_data))
        # Wifi_Signal_data = random.randint(-80, -20) # set data
        sniff(iface=interface, prn = PacketHandler, count = 10)
        Wifi_Signal_data = rssi
        self.plotData['y'].append(Wifi_Signal_data)
        self.plotData['x'].append(new_time_data)

        if (realtime_check):
            self.pw.setXRange(new_time_data - 80, new_time_data + 20, padding=0)   # always show X Line.

        self.pdi.setData(self.plotData['x'], self.plotData['y'])

    def btnRun_clicked(self):
        global realtime_check
        QMessageBox.about(self, "message box", "Change Trace Mode!!!")
        realtime_check = not realtime_check

def PacketHandler(pkt) :
    global rssi
    if pkt.haslayer(Dot11) :
        if pkt.type == 0 and pkt.subtype == 8 :
            if pkt.haslayer(Dot11Beacon) or pkt.haslayer(Dot11ProbeResp):
                if pkt.addr2 == mac :
                    try:
                        rssi = -(256-pkt.notdecoded[0])
                    except:
                        rssi = -100
                    # print ("WiFi signal strength:", rssi, "dBm of", pkt.addr2, pkt.info)

if __name__ == "__main__":
    import os

    if len(sys.argv) != 3:
        print("Wrong factor")
        sys.exit()
    
    interface = sys.argv[1]
    mac = sys.argv[2]
    os.system("sudo ifconfig "+str(interface)+" down")
    os.system("sudo iwconfig "+str(interface)+" mode monitor")
    os.system("sudo ifconfig "+str(interface)+" up")
    print("input Channel : ", end = "")
    CH = input()
    os.system("sudo iwconfig "+interface+" channel "+CH)
    # sniff(iface=interface, prn = PacketHandler, count = 10)

    app = QApplication(sys.argv)
    ex = ExampleWidget()
    def get_data():
        new_time_data = int(time.time())
        ex.update_plot(new_time_data)

    mytimer = QTimer()
    mytimer.start(500)  # 0.5 seconds refresh
    mytimer.timeout.connect(get_data)

    ex.show()
    sys.exit(app.exec_())

