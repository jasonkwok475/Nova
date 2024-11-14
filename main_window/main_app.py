import logging
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

logging.basicConfig(level=logging.INFO)

class MainWindow(QWidget):
  def __init__(self, model):
    super(MainWindow, self).__init__(None)

    self.model = model

    self.resize(200,50)
    self.setWindowTitle("Nova")
    self.initUi()

    self.showMaximized()

  def log(self):
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

class QTextEditLogger(logging.Handler):
  def __init__(self, parent):
      super().__init__()
      self.widget = QPlainTextEdit(parent)
      self.widget.setReadOnly(True) 