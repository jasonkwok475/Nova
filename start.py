import sys
from PyQt5.QtWidgets import QApplication
from windows.com_window import ComWindow

def main():
  app = QApplication(sys.argv)
  ex = ComWindow()
  #ex.show()

  sys.exit(app.exec_())

  #https://www.dfrobot.com/blog-944.html
  #https://techtutorialsx.com/2018/03/26/esp32-arduino-bluetooth-finding-the-device-with-python/

if __name__ == '__main__':
  main()