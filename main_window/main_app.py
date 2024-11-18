from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg

import logging
import serial
import serial.tools.list_ports
import bluetooth
import ast
import time

logging.basicConfig(level=logging.INFO)

graphPen = pg.mkPen(color=(2, 135, 195), width=2)

class MainWindow(QWidget):
  def __init__(self, con_type, con_device, con_address, serial_rate):
    super(MainWindow, self).__init__(None)

    self.con_type = con_type
    self.con_device = con_device
    self.con_address = con_address
    self.serial_rate = serial_rate

    self.data = []
    self.time = []

    self.resize(200,50)
    self.setWindowTitle("Nova")
    self.initUi()

    self.showMaximized()

    self.log("Successfully connected to " + con_device + ": " + con_address)

    self.initSerialReader()
    

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

    #Buttons!
    self.writeButton = QPushButton("LED Button")
    self.writeButton.clicked.connect(self.writeData)

    self.buttonsBox = QGroupBox("Buttons")
    self.buttons = QVBoxLayout()
    self.buttons.addWidget(self.writeButton)
    self.buttonsBox.setLayout(self.buttons)

    #Add widgets to display
    self.grid.addWidget(self.generatePlot(), 1, 1, 2, 1)
    self.grid.addWidget(QGroupBox("2D Plot Here"), 1, 2, 2, 1)
    self.grid.addWidget(QGroupBox("Buttons Here"), 1, 3)
    self.grid.addWidget(self.buttonsBox, 2, 3)
    self.grid.addWidget(self.loggingGroupBox, 3, 1, 1, 3)

    self.setLayout(self.grid)


  def initSerialReader(self):
    self.serialThread = QThread()
    self.serialWorker = SerialWorker(self)
    self.serialWorker.moveToThread(self.serialThread)

    self.serialThread.started.connect(self.serialWorker.run)
    self.serialWorker.output.connect(self.serialOutput)
    self.serialWorker.log.connect(self.log)
    self.serialThread.finished.connect(self.serialThread.deleteLater)

    self.serialThread.start()

  def serialOutput(self, data):
    data = ast.literal_eval(data)

    self.data.append(data.get('data'))
    self.time.append(data.get('time') / 1000)

    self.updatePlot()

  def generatePlot(self):
    self.timePlot = pg.PlotWidget()
    self.timePlot.setBackground("w")
    self.timePlot.setTitle("Potentiometer Output", color="k")
    self.timePlot.setLabel("left", "Output")
    self.timePlot.setLabel("bottom", "Time")

    self.timeLine = self.timePlot.plot(self.time, self.data, pen=graphPen)

    return self.timePlot
  
  def updatePlot(self):
    self.timeLine.setData(self.time, self.data)

  def writeData(self):
    self.serialWorker.write("L")


class QTextEditLogger(logging.Handler):
  def __init__(self, parent):
    super().__init__()
    self.widget = QPlainTextEdit(parent)
    self.widget.setReadOnly(True) 

  def emit(self, record):
    msg = self.format(record)
    self.widget.appendPlainText(msg)


class SerialWorker(QObject):
  output = pyqtSignal(str)
  log = pyqtSignal(str)

  def __init__(self, parent):
    super().__init__()
    self.parent = parent

    self.serialPort = serial.Serial(
        port=self.parent.con_device, baudrate=self.parent.serial_rate, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE
      )

  def write(self, byte):
    self.serialPort.write(bytes(byte, 'utf-8'))

  def startProgram(self):
    time.sleep(5) #Serial takes around 3 seconds to connect
    self.write("S")
    self.log.emit("Sent start code to connected board")

  def run(self):
    #Tell the arduino to start

    #Check if bluetooth connection is established before starting main window, if not send an error message
    #If it is established, log a message detailing the connection

    #https://stackoverflow.com/questions/21050671/how-to-check-if-device-is-connected-pyserial
    #https://www.dfrobot.com/blog-943.html
    #https://github.com/HyperMuffin12/ESP32-Bluetooth-Serial-Two-Way-Communication
    #https://people.csail.mit.edu/albert/bluez-intro/x502.html
    #https://people.csail.mit.edu/albert/bluez-intro/index.html

    if (self.parent.con_type == "Bluetooth"): 
      return
    else:
      myports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
      con_port = [port for port in myports if self.parent.con_device in port][0]

      self.startProgram()
      
      serialString = ""  # Used to hold data coming over UART
      while 1:
        myports = [tuple(p) for p in list(serial.tools.list_ports.comports())]

        if con_port not in myports:
          self.log.emit("Device has been disconnected from " + self.parent.con_device)
          self.deleteLater
          break

        serialString = self.serialPort.readline()
        try:
          msg = serialString.decode("Ascii")
          if (msg != ""): self.output.emit(msg.strip())
        except:
          pass