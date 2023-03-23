from PyQt5 import QtWidgets
from fbs_runtime.application_context.PyQt5 import ApplicationContext
import sys

from Dialog import Ui_Dialog

if __name__ == "__main__":

   appctxt = ApplicationContext()
   # app = QtWidgets.QApplication(sys.argv)
   Dialog = QtWidgets.QDialog()
   ui = Ui_Dialog()
   ui.setupUi(Dialog)
   Dialog.show()
   exit_code = appctxt.app.exec_()
   sys.exit(exit_code)