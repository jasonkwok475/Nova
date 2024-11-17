from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from main_window.main_app import MainWindow
import serial.tools.list_ports as port_list

import bluetooth

serial = ["9600", "19200", "38400", "57600", "115200"]
ports = ["Bluetooth"]
hwidList = []
portList = port_list.comports()

for port, desc, hwid in sorted(portList):
  ports.append(port)
  hwidList.append(hwid)

class ComWindow(QDialog):
  def __init__(self):
    super().__init__(None)

    self.initUi()
    self.refreshBluetoothWidget()
    self.exec_()


  def initUi(self):
    self.setWindowTitle('Nova')
    self.resize(300, 230)

    self.grid = QGridLayout()
    self.form = QFormLayout()
    self.formPort = QFormLayout()

    self.startButton = QPushButton("Start Program")
    self.startButton.clicked.connect(self.start)

    self.devices = QComboBox()
    self.devices.addItem("Searching for devices...")
    self.devices.setEnabled(False)

    self.port = QComboBox()
    self.port.addItems(ports)
    self.formPort.addRow(self.tr("&Port:"), self.port)
    self.port.currentIndexChanged.connect(self.comSelect)

    self.refreshButton = QPushButton("Refresh Devices")
    self.refreshButton.clicked.connect(self.refreshBluetoothWidget)
    self.refreshButton.setEnabled(False)

    self.bluetoothGroupBox = QGroupBox("Select ESP32 Connection")
    self.vboxBluetooth = QVBoxLayout()
    self.vboxBluetooth.addLayout(self.formPort)
    self.vboxBluetooth.addWidget(self.devices)
    self.vboxBluetooth.addWidget(self.refreshButton)
    self.bluetoothGroupBox.setLayout(self.vboxBluetooth)

    self.serial = QComboBox()
    self.serial.addItems(serial)
    self.serial.setCurrentIndex(4)

    self.form.addRow(self.tr("&Serial:"), self.serial)

    self.grid.addWidget(self.bluetoothGroupBox, 1, 1)
    self.grid.addLayout(self.form, 2, 1)
    self.grid.addWidget(self.startButton, 3, 1)

    self.setLayout(self.grid)


  def generateBlueToothWidget(self):
    self.devices = QComboBox()
    self.devices.addItems(self.getBluetoothList())

    return self.devices
  
  def refreshBluetoothWidget(self):
    self.trainingThread = QThread()
    self.worker = Worker(self)
    self.worker.moveToThread(self.trainingThread)

    self.trainingThread.started.connect(self.worker.run)
    self.worker.finished.connect(self.trainingThread.quit)
    self.worker.finished.connect(self.worker.deleteLater)
    self.trainingThread.finished.connect(self.trainingThread.deleteLater)

    self.trainingThread.start()


  def _refreshBluetooth(self):
    self.devices.clear()

    self.devices.addItem("Searching for devices...")
    self.devices.setEnabled(False)
    self.refreshButton.setEnabled(False)

    self.devices.clear()
    self.devices.addItems(self.getBluetoothList())


  def getBluetoothList(self):
    devices = bluetooth.discover_devices(lookup_names=True)

    devices_list = []
    for item in devices:
      devices_list.append(item)
      
    addresses, device = zip(*devices_list)

    #save to global
    self.devices_arr = device
    self.addresses_arr = addresses
    
    self.refreshButton.setEnabled(True)
    self.devices.setEnabled(True)

    return device
  

  def comSelect(self):
    if (str(self.port.currentText()) == "Bluetooth"):
      self.devices.show()
      self.refreshButton.show()
    else:
      self.devices.hide()
      self.refreshButton.hide()


  def start(self):
    #Check if bluetooth connection is established before starting main window, if not send an error message
    #If it is established, log a message detailing the connection

    #Start main window
    if (str(self.port.currentText()) == "Bluetooth"):
      i = self.devices.currentIndex()
      self.mainWindow = MainWindow("Bluetooth", str(self.devices_arr[i]), str(self.addresses_arr[i]), int(self.serial.currentText()))
    else:
      self.mainWindow = MainWindow("COM", str(self.port.currentText()), str(hwidList[self.port.currentIndex() - 1]), int(self.serial.currentText()))


    self.close()


class Worker(QObject):
  finished = pyqtSignal()

  def __init__(self, parent):
    super().__init__()
    self.parent = parent

  def run(self):
      self.parent._refreshBluetooth()
      self.finished.emit()