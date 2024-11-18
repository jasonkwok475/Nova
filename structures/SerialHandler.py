import serial
import serial.tools.list_ports
import bluetooth
from PyQt5.QtCore import QObject, pyqtSignal

class ComHandler:
  def __init__(self):
    self

class ComWorker(QObject):
  output = pyqtSignal(str)

  def __init__(self, parent, con_device, rate=9600):
    super().__init__()
    self.parent = parent
    self.con_device = con_device
    self.rate = rate

  def run(self):
    #Check if bluetooth connection is established before starting main window, if not send an error message
    #If it is established, log a message detailing the connection

    #https://stackoverflow.com/questions/21050671/how-to-check-if-device-is-connected-pyserial
    #https://www.dfrobot.com/blog-943.html
    #https://github.com/HyperMuffin12/ESP32-Bluetooth-Serial-Two-Way-Communication
    #https://people.csail.mit.edu/albert/bluez-intro/x502.html
    #https://people.csail.mit.edu/albert/bluez-intro/index.html

    myports = self.getDevices()
    con_port = [port for port in myports if self.con_device in port][0]

    serialPort = serial.Serial(
      port=self.con_device, baudrate=self.rate, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE
    )
    serialString = ""  # Used to hold data coming over UART
    while 1:
      myports = self.getDevices()

      if con_port not in myports:
        self.output.emit("Device has been disconnected from " + self.con_device)
        self.deleteLater
        break

      serialString = serialPort.readline()
      try:
        msg = serialString.decode("Ascii")
        if (msg != ""): self.output.emit(msg.strip()) #Strip removes leading/trailing whitespace and \n
      except:
        pass

  def getDevices():
    return [tuple(p) for p in list(serial.tools.list_ports.comports())]

class BluetoothServer:
  def __init__(self):
    self

class BluetoothClient:
  def __init__(self):
    self