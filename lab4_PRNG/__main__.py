# Packages needed: PyQt5, pyQt5-stubs, qdarkstyle
import sys

from PyQt5 import QtCore
from PyQt5.QtCore import QRect, QSize, QPoint
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtWidgets import QApplication, QStyle, QVBoxLayout, QPushButton, QGridLayout, QGroupBox, QRadioButton
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QStatusBar
from PyQt5.QtWidgets import QToolBar
from qdarkstyle import load_stylesheet

# TODO Implement logger

class Window(QMainWindow):
    font_toolbar = QFont("Times", weight=QFont.Bold, pointSize=14)
    actions      = ['Galois', 'Stop & Go', 'Shrinking']

    def __init__(self, parent=None):
        """Initializer."""
        super(Window, self).__init__(parent)
        self.setWindowTitle('Pseudo Random Number Generator')
        # self.setCentralWidget(QLabel("I'm the Central Widget"))

        group1 = QGroupBox("Example 1")
        radio1 = QRadioButton("&Radio pizza")

        vbox = QVBoxLayout()
        vbox.addWidget(radio1)
        vbox.addStretch(1)
        group1.setLayout(vbox)

        grid = QGridLayout()
        grid.addWidget(group1, 0, 0)
        grid.addWidget(group1, 1, 0)
        grid.addWidget(group1, 0, 1)
        grid.addWidget(group1, 1, 1)

        self.setLayout(grid)

        # groupbox.setGeometry(QRect(40, 40, 40, 40))

        #params:  move x, y size: x, y
        self.setStyleSheet(load_stylesheet(qt_api='pyqt5'))
        self.setGeometry(1200, 400, 600, 400)
        self.setFixedSize(600, 400)
        self._createMenu()
        self._createToolBar()
        self._createStatusBar()
    #

    def _createMenu(self):
        self.menu = self.menuBar().addMenu("&Menu")
        self.menuBar().addMenu("&About")
        self.menu.addAction('&Exit', self.close)
    #

    def _createToolBar(self):
        tools = QToolBar()
        Galois = tools.addAction(Window.actions[0], self.close)
        Galois.setToolTip("Galois Random Number Generator")
        Galois.setFont(Window.font_toolbar)
        tools.addSeparator()
        StopGo = tools.addAction(Window.actions[1], self.close)
        StopGo.setToolTip("Stop & Go Random Number Generator")
        StopGo.setFont(Window.font_toolbar)
        tools.addSeparator()
        Shrinking = tools.addAction(Window.actions[2], self.close)
        Shrinking.setToolTip("Shrinking Random Number Generator")
        Shrinking.setFont(Window.font_toolbar)
        self.addToolBar(tools)

    #

    def _createStatusBar(self):
        status = QStatusBar()
        status.showMessage("Widget here")
        self.setStatusBar(status)
        # it appears for a sec and then disappears
        # it disappears after moving onto main menu!
    #
#


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Window()
    # 4. Show your application's GUI
    win.show()
    # 5. Run your application's event loop (or main loop)
    sys.exit(app.exec_())