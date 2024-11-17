from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import logging
import serial

logging.basicConfig(level=logging.INFO)

class MainWindow(QWidget):
  def __init__(self, con_type, con_device, con_address, serial_rate):
    super(MainWindow, self).__init__(None)

    self.con_type = con_type
    self.con_device = con_device
    self.con_address = con_address
    self.serial_rate = serial_rate

    self.resize(200,50)
    self.setWindowTitle("Nova")
    self.initUi()

    self.showMaximized()

    self.log("Successfully connected to " + con_device + ": " + con_address)

    self.initSerialReader()
    
      
    # s = serial.Serial(btdevice)
    # res = s.read()
    # print(res)

  def log(self, str):
    logging.info(str)

  def initUi(self):
    logTextBox = QTextEditLogger(self)
    logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s --- %(message)s'))
    logging.getLogger().addHandler(logTextBox)

    self.grid = QGridLayout()
    self.grid.setRowStretch(1,2) 
    self.grid.setRowStretch(2,2) 
    self.grid.setColumnStretch(1,2) 
    self.grid.setColumnStretch(2,1) 
    self.grid.setColumnStretch(3,1) 

    #Program Logs
    self.loggingGroupBox = QGroupBox("Network Logs")
    self.vboxLog = QVBoxLayout()
    self.vboxLog.addWidget(logTextBox.widget)
    self.loggingGroupBox.setLayout(self.vboxLog)

    #Add widgets to display
    self.grid.addWidget(QGroupBox("3D Plot Here"), 1, 1, 2, 1)
    self.grid.addWidget(QGroupBox("2D Plot Here"), 1, 2, 2, 1)
    self.grid.addWidget(QGroupBox("Buttons Here"), 1, 3)
    self.grid.addWidget(QGroupBox("Buttons Here"), 2, 3)
    self.grid.addWidget(self.loggingGroupBox, 3, 1, 1, 3)

    self.setLayout(self.grid)


  def initSerialReader(self):
    self.serialThread = QThread()
    self.serialWorker = SerialWorker(self)
    self.serialWorker.moveToThread(self.serialThread)

    self.serialThread.started.connect(self.serialWorker.run)
    self.serialWorker.output.connect(self.log)
    self.serialThread.finished.connect(self.serialThread.deleteLater)

    self.serialThread.start()


class QTextEditLogger(logging.Handler):
  def __init__(self, parent):
    super().__init__()
    self.widget = QPlainTextEdit(parent)
    self.widget.setReadOnly(True) 

  def emit(self, record):
    msg = self.format(record)
    self.widget.appendPlainText(msg)


class SerialWorker(QObject):
  output = pyqtSignal()

  def __init__(self, parent):
    super().__init__()
    self.parent = parent

  def run(self):
    if (self.parent.con_type == "Bluetooth"): return
    serialPort = serial.Serial(
      port=self.parent.con_device, baudrate=9600, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE
    )
    serialString = ""  # Used to hold data coming over UART
    while 1:
      # Read data out of the buffer until a carraige return / new line is found
      serialString = serialPort.readline()

      # Print the contents of the serial data
      try:
        msg = serialString.decode("Ascii")
        if (msg != ""):
          self.parent.log(msg)
      except:
        pass