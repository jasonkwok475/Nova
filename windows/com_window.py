from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from main_window.main_app import MainWindow

class ComWindow(QDialog):
  def __init__(self):
    super().__init__(None)

    self.initUi()
    self.exec_()

  def initUi(self):
    self.setWindowTitle('Nova')
    self.resize(300, 230)

    self.grid = QGridLayout()
    self.form = QFormLayout()

    self.startButton = QPushButton("Start Program")
    self.startButton.clicked.connect(self.start)

    self.models = QComboBox()
    self.models.addItems(['New Trained Model','Model 1'])

    self.form.addRow(self.tr("&Model:"), self.models)

    self.grid.addLayout(self.form, 1, 1)
    self.grid.addWidget(self.startButton,2,1)

    self.setLayout(self.grid)

  def start(self):
    #Start main window
    self.mainWindow = MainWindow(str(self.models.currentText()))

    self.close()