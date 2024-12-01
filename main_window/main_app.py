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
import traceback

logging.basicConfig(level=logging.INFO)

graphPenX = pg.mkPen(color=(2, 135, 195), width=2)
graphPenY = pg.mkPen(color=(255, 95, 31), width=2)
graphPenZ = pg.mkPen(color=(49, 117, 70), width=2)

ADDRESS = "10:06:1C:F2:37:2A"

class MainWindow(QWidget):
  def __init__(self, con_type, con_device, con_address, serial_rate):
    super(MainWindow, self).__init__(None)

    self.con_type = con_type
    self.con_device = con_device
    self.con_address = con_address
    self.serial_rate = serial_rate

    self.gyro_timeX = []
    self.gyro_timeY = []
    self.gyro_timeZ = []
    self.gyroX = []
    self.gyroY = []    
    self.gyroZ = []

    self.resize(200,50)
    self.setWindowTitle("Nova")
    self.initUi()

    self.showMaximized()    

    self.initSerialReader()
    

  def log(self, str):
    logging.info(str)

  def error(self, str):
    logging.error(str)

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
    self.grid.addWidget(self.generateGyro(), 1, 1, 2, 1)
    self.grid.addWidget(QGroupBox("2D Plot Here"), 1, 2, 2, 1)
    self.grid.addWidget(QGroupBox("Buttons Here"), 1, 3)
    self.grid.addWidget(self.buttonsBox, 2, 3)
    self.grid.addWidget(self.loggingGroupBox, 3, 1, 1, 3)

    self.setLayout(self.grid)


  def initSerialReader(self):
    self.serialThread = QThread()
    self.serialWorker = SerialWorker(self)
    self.serialWorker.moveToThread(self.serialThread)

    self.serialThread.started.connect(self.serialWorker.init)
    self.serialWorker.output.connect(self.serialOutput)
    self.serialWorker.log.connect(self.log)
    self.serialWorker.error.connect(self.error)
    self.serialWorker.gyro.connect(self.gyroData)
    self.serialThread.finished.connect(self.serialThread.deleteLater)

    self.serialThread.start()

  def serialOutput(self, data):
    data = ast.literal_eval(data)

    self.data.append(data.get('data'))
    self.time.append(data.get('time') / 1000)

    self.updatePlot()

  def generateGyro(self):
    #https://stackoverflow.com/questions/40577104/how-to-plot-two-real-time-data-in-one-single-plot-in-pyqtgraph
    gyroPlot = pg.PlotWidget()
    gyroPlot.setBackground("w")
    gyroPlot.setTitle("Gyroscope Output", color="k")
    gyroPlot.setLabel("left", "Rotation [rad/s]")
    gyroPlot.setLabel("bottom", "Time [s]")

    self.gyroLineX = gyroPlot.plot(self.gyro_timeX, self.gyroX, pen=graphPenX)
    self.gyroLineY = gyroPlot.plot(self.gyro_timeY, self.gyroY, pen=graphPenY)
    self.gyroLineZ = gyroPlot.plot(self.gyro_timeZ, self.gyroZ, pen=graphPenZ)
    self.gyroPlot = gyroPlot

    return gyroPlot
  
  def updateGyro(self):
    self.gyroLineX.setData(self.gyro_timeX, self.gyroX)
    self.gyroLineY.setData(self.gyro_timeY, self.gyroY)
    self.gyroLineZ.setData(self.gyro_timeZ, self.gyroZ)

  def writeData(self):
    self.serialWorker.write("L")

  def gyroData(self, data):
    self.gyroX.append(data.get('x'))
    self.gyroY.append(data.get('y'))
    self.gyroZ.append(data.get('z'))
    self.gyro_timeX.append(data.get('time') / 1000)
    self.gyro_timeY.append(data.get('time') / 1000)
    self.gyro_timeZ.append(data.get('time') / 1000)

    if (len(self.gyro_timeX) > 100):
      self.gyroX = self.gyroX[1:]
      self.gyroY = self.gyroY[1:]
      self.gyroZ = self.gyroZ[1:]
      self.gyro_timeX = self.gyro_timeX[1:] 
      self.gyro_timeY = self.gyro_timeY[1:] 
      self.gyro_timeZ = self.gyro_timeZ[1:] 

    self.updateGyro()


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
  error = pyqtSignal(str)
  
  gyro = pyqtSignal(dict)

  def __init__(self, parent):
    super().__init__()
    self.parent = parent

    self.connected = False
    self.con_device = self.parent.con_device
    self.con_address = self.parent.con_address
    self.con_type = self.parent.con_type
    self.serial_rate = self.parent.serial_rate  

  def write(self, byte):
    if self.con_type == "Bluetooth":
      self.sock.send(bytes(byte, 'utf-8'))
    else:
      self.serialPort.write(bytes(byte, 'utf-8'))

  def startProgram(self):
    time.sleep(5) #Serial takes around 3 seconds to connect
    self.write("S")
    self.log.emit("Sent start code to connected board")

  def init(self):
    try:
      self.log.emit("Connecting to \"{}\" on {}".format(self.con_device, self.con_address))
      if self.con_type == "Bluetooth":
        service_matches = bluetooth.find_service(address=self.con_address)
        if len(service_matches) == 0: raise Exception("Couldn't find device matching address " + self.con_address)

        self.port = service_matches[0]["port"]
        self.name = service_matches[0]["name"]
        self.host = service_matches[0]["host"]

        #https://www.esp32.com/viewtopic.php?t=31250#:~:text=Rewritten%20the%20code%20to%20fit,maybe%2010%20in%20open%20field.

        self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.sock.connect((self.host, self.port))

        self.sock.send("Hello!")

      else:
        self.serialPort = serial.Serial(
            port=self.con_device, baudrate=self.serial_rate, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE
          )

      self.log.emit("Successfully connected to " + self.con_device + ": " + self.con_address)
      self.connected = True

    except Exception as e:
      self.log.emit("Failed to connect to " + self.con_device + ": " + self.con_address)
      self.error.emit(traceback.format_exc())

    self.run()


  def run(self):
    #Tell the arduino to start

    #Check if bluetooth connection is established before starting main window, if not send an error message
    #If it is established, log a message detailing the connection

    #https://stackoverflow.com/questions/21050671/how-to-check-if-device-is-connected-pyserial
    #https://www.dfrobot.com/blog-943.html
    #https://github.com/HyperMuffin12/ESP32-Bluetooth-Serial-Two-Way-Communication
    #https://people.csail.mit.edu/albert/bluez-intro/x502.html
    #https://people.csail.mit.edu/albert/bluez-intro/index.html

    self.startProgram()

    if (self.con_type == "Bluetooth"): 
      while self.connected:
        try: 
          self.sock.getpeername()
          self.connected = True
        except:
          #!Put this into another function in the class
          self.log.emit("Device has been disconnected from {}".format(self.con_device))
          self.deleteLater
          self.connected = False
          break
            
        data = self.sock.recv(1024)
        if data != "":
          data = ast.literal_eval(data.decode("Ascii"))
          print(data)
          if data.get("type") == 1: #Gyro data
            self.gyro.emit(ast.literal_eval(data.get("data")))

    else:
      myports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
      con_port = [port for port in myports if self.con_device in port][0]
      
      serialString = ""  # Used to hold data coming over UART
      while self.connected:
        myports = [tuple(p) for p in list(serial.tools.list_ports.comports())]

        if con_port not in myports:
          self.log.emit("Device has been disconnected from {}".format(self.con_device))
          self.deleteLater
          self.connected = False
          break

        serialString = self.serialPort.readline()
        try:
          msg = serialString.decode("Ascii")
          if (msg != ""): self.output.emit(msg.strip())
        except:
          pass