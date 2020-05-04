# Packages needed: PyQt5, pyQt5-stubs, qdarkstyle
import sys
from collections import namedtuple


from PyQt5.QtCore import QRect, QSize, QPoint
from PyQt5 import QtCore
import PyQt5.QtCore as pqtc
from PyQt5.QtGui import QFont, QPalette, QColor, QPixmap
from PyQt5.QtWidgets import QApplication, QStyle, QVBoxLayout, QPushButton, QGridLayout, QGroupBox, QRadioButton, \
    QWidget, QHBoxLayout, QFrame, QLineEdit, QComboBox, QSpinBox, QCheckBox, QProgressBar, QDialog
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QStatusBar
from PyQt5.QtWidgets import QToolBar
from qdarkstyle import load_stylesheet
# TODO Implement logger
# TODO add info to status bar i.e. "generating output..." at the bottom!



class Window(QMainWindow):
    # Create groups that will be visible as sections in main window
    font_toolbar = QFont("Times", weight=QFont.Bold, pointSize=14)
    actions      = ['Geffe', 'Stop and Go', 'Shrinking']
    window_size  = (900, 550)
    window_pos   = (1000, 400)
    generator_buttons = {"lfsr" : [{"name" : "&LFSR-1", "ref" : None},
                                   {"name" : "&LFSR-2", "ref" : None},
                                   {"name" : "&LFSR-3", "ref" : None}], "generate": "&Generate"}
    test_types = {"Monobit": {"Name" : "Monobit", "Range": (9725, 10275)},
                  "Poker" : {"Name" : "Poker", "Range": (2.16, 46.17)} ,
                  "Long runs" : {"Name" : "Long runs", "Range": (26)}}
    lsfr_items = ["Galois", "Fibonacci", "XORSHIFT"]

    def __init__(self, parent=None):
        """Initializer."""
        super(Window, self).__init__(parent)
        self.setWindowTitle('Pseudo Random Number Generator')
        #params:  move x, y size: x, y
        self.setStyleSheet(load_stylesheet(qt_api='pyqt5'))
        self.setGeometry(*Window.window_pos, *Window.window_size)
        self.setFixedSize(*Window.window_size)
        self._createMenu()
        self._createToolBar()
        self._createStatusBar()
        self._setCentralLayout()
    #

    def _createMenu(self):
        self.menu = self.menuBar().addMenu("&Menu")
        self.menuBar().addMenu("&Theme")
        self.menuBar().addMenu("&About")
        self.menu.addAction('&Exit', self.close)
    #

    def _createToolBar(self):
        tools = QToolBar()
        Galois = tools.addAction(Window.actions[0], self._change_lfsr3_state)
        Galois.setToolTip("Galois Random Number Generator")
        Galois.setFont(Window.font_toolbar)
        tools.addSeparator()
        StopGo = tools.addAction(Window.actions[1], self._change_lfsr3_state)
        StopGo.setToolTip("Stop&Go Random Number Generator")
        StopGo.setFont(Window.font_toolbar)
        tools.addSeparator()
        Shrinking = tools.addAction(Window.actions[2], self._change_lfsr3_state)
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

    def _change_lfsr3_state(self):
        lfsr3_button = Window.generator_buttons["lfsr"][2]["ref"]
        if lfsr3_button.isEnabled():
            lfsr3_button.setDisabled(True)
        else:
            lfsr3_button.setEnabled(True)


    def _lsfr_dialog(self):
        # Initial settings for dialog
        d = QDialog()
        d.setStyleSheet(load_stylesheet(qt_api='pyqt5'))
        pos = self.pos()
        d.move(pos.x() + 100, pos.y() + 200)
        d.setWindowTitle("Dialog")
        d.setWindowModality(pqtc.Qt.ApplicationModal)
        #
        lfsr_grid = QGridLayout()
        # Size of register contents and tapmask
        size_label = QLabel("Size")
        size_box   = QSpinBox()
        size_box.setRange(1, 30)
        size_box.setValue(4)
        # Contents
        register_label = QLabel("Register contents")
        tapmask_label  = QLabel("Tapmask")
        register_cont  = QLineEdit() # maximum size of chosen size box!!!!
        tapmask_cont   = QLineEdit()
        register_gen   = QPushButton("Random")
        # # TODO: Random Primary Polynomial and check if primary
        tapmask_gen    = QPushButton("Random")
        #
        # # Type
        type_label     = QLabel("Type")
        type_box       = QComboBox()
        type_box.addItems(["Galois", "Fibonacci", "XORSHIFT"])
        # #
        b1 = QPushButton("&Confirm")
        #
        lfsr_grid.addWidget(size_label, *(0,0))
        lfsr_grid.addWidget(size_box, *(0,1))
        lfsr_grid.addWidget(register_label, *(2,0))
        lfsr_grid.addWidget(register_cont, *(3,0))
        lfsr_grid.addWidget(register_gen, *(3,1))
        lfsr_grid.addWidget(tapmask_label, *(4,0))
        lfsr_grid.addWidget(tapmask_cont, *(5,0))
        lfsr_grid.addWidget(tapmask_gen, *(5,1))
        lfsr_grid.addWidget(type_label, *(6,0))
        lfsr_grid.addWidget(type_box, *(6,1))
        lfsr_grid.addWidget(b1, *(7,1))


        d.setLayout(lfsr_grid)
        d.exec_()
    #

    def _setCentralLayout(self):
        grid = QGridLayout()
        centralWidget = QWidget()

        # nr_bits_box     = QComboBox()
        # nr_bits_box.addItems(['123', '123', '123'])

        def generator_group():
            widgets_view = []
            # Frame that will hold horizontal buttons layout
            lfsr_button_frame = QFrame()

            # Add label "LFSR: "
            widgets_view.append(QLabel("LFSR: "))
            # Create horizontal layout
            horzlay = QHBoxLayout()
            # horzlay.setGeometry(QRect(20, 20, 20, 20))
            # Append LFSR buttons to it
            for bt in Window.generator_buttons["lfsr"]:
                button = QPushButton(bt["name"])
                button.clicked.connect(self._lsfr_dialog)
                button.setToolTip("Click to set properties for register " + bt["name"].lstrip("&"))
                horzlay.addWidget(button)
                bt["ref"] = button
            horzlay.addStretch()
            # Add layout to frame
            lfsr_button_frame.setLayout(horzlay)
            # Append frame to widgets
            widgets_view.append(lfsr_button_frame)

            # Append second "Parameters: " label to widgets
            # Create grid for Parameters region
            widgets_view.append(QLabel("Parameters: "))
            params_grid = QGridLayout()

            # First parameter - number of bits to generate by generator
            nr_bits_box       = QSpinBox()
            nr_bits_box.setRange(10, 10000)
            count_bits_label = QLabel("Bits count")
            nr_bits_box.setToolTip("Number of bits to generate")

            # Second param - display these bits every n bits generated
            display_every_box = QSpinBox()
            display_every_label = QLabel("Bits (shown) interval")
            display_every_box.setRange(10, 10000) # Should it have any special range?
            display_every_box.setToolTip("After how many bits should the tool display output")

            # Second param - display these bits every n bits generated
            display_last_box = QSpinBox()
            display_last_label = QLabel("Last (shown) bits")
            display_last_box.setRange(10, 10000)  # Should it have any special range?
            display_last_box.setToolTip("Display n last bits of output")

            # Third section - add to file, animate etc. - aux options
            save_to_file_box = QCheckBox()
            save_to_file_box.setText("Save to file")
            save_to_file_box.setToolTip("Click to save to file (dialog will appear after Generate button clicked)")
            animate_check = QCheckBox()
            animate_box   = QSpinBox()
            animate_check.setText("Animate (ms)")
            animate_box.setToolTip("Animation interval in milliseconds")
            animate_box.setRange(0, 10000)  # Should it have any special range?
            animate_box.setValue(100)

            # Add all sections to the grid
            params_grid.addWidget(count_bits_label, *(0,0))
            params_grid.addWidget(nr_bits_box, *(0, 1))

            params_grid.addWidget(display_every_label, *(1,0))
            params_grid.addWidget(display_every_box, *(1, 1))

            params_grid.addWidget(display_last_label, *(2, 0))
            params_grid.addWidget(display_last_box, *(2, 1))

            params_grid.addWidget(save_to_file_box, *(3, 0))

            params_grid.addWidget(animate_check, *(4, 0))
            params_grid.addWidget(animate_box, *(4, 1))
            # Add all sections to the grid

            # Create frame and add grid to it, next add frame to widgets
            f3 = QFrame()
            f3.setLayout(params_grid)
            widgets_view.append(f3)

            # Append third "Out: " layout to widgets
            gen_lay = QHBoxLayout()
            gen_lay.addWidget(QLabel("Output: "))
            gen_lay.addWidget(QPushButton(Window.generator_buttons['generate']))
            f4 = QFrame()
            f4.setLayout(gen_lay)
            widgets_view.append(f4)

            # Append Fourth section "Generated output holder" to widgets
            generated_output = QLineEdit()
            generated_output.setMinimumHeight(50)
            generated_output.setMaximumHeight(50)
            generated_output.setToolTip("Right click on window and Select All / Copy to get output to clipboard")
            generated_output.setReadOnly(True)
            horzlay_out = QHBoxLayout()
            horzlay_out.addWidget(generated_output)

            # Append frame to widgets
            f2 = QFrame()
            f2.setLayout(horzlay_out)
            widgets_view.append(f2)

            # Fifth section
            # Does not work now!
            progress_bar = QProgressBar()
            progress_bar.setValue(0)
            progress_bar.setTextVisible(True)
            progress_txt = "%p%".format(0)
            progress_bar.setFormat(progress_txt)
            progress_bar.setAlignment(pqtc.Qt.AlignCenter)
            widgets_view.append(progress_bar)

            return widgets_view
        #

        # TODO: Call with parameter - type of test passed???
        def test_group():
            widgets_view = []
            test_frame = QFrame()

            # Create horizontal layout
            test_param_box = QGridLayout()
            # Type of test
            type_label     = QLabel("Type")
            type_box       = QComboBox()
            type_box.addItems([type for type in Window.test_types.keys()])

            # Parameters of the test - range of values
            param_label = QLabel("Test range")
            # Minimum value
            param_from = QSpinBox()
            param_from.setToolTip("Minimum value for the test to pass")
            param_from.setRange(-100000, 100000)
            param_from.setValue(Window.test_types['Monobit']['Range'][0]) # Window.test_types['Monobit']['Range'][1]
            param_separator = QLabel(" - ")
            # Maximum value
            param_to = QSpinBox()
            param_to.setToolTip("Minimum value for the test to pass")
            param_to.setRange(-100000, 100000)
            param_to.setValue(Window.test_types['Monobit']['Range'][1])
            #

            # Test value and status
            ret_label = QLabel("Test value")
            status_label = QLabel("Test status")
            returned_status = QLabel()
            returned_status.setPixmap(QPixmap("pass.png").scaled(50, 400, pqtc.Qt.KeepAspectRatio))
            # Test value returned
            test_val = QLineEdit()
            test_val.setFixedSize(60, 20)
            test_val.setToolTip("Right click on window and Select All / Copy to get output to clipboard")
            test_val.setReadOnly(True)
            #

            # Add type of test
            test_param_box.addWidget(type_label, *(0,0))
            test_param_box.addWidget(type_box,   *(0,1))
            # Add test parameters and range
            test_param_box.addWidget(param_label,*(1,0))
            test_param_box.addWidget(param_from,*(1,1))
            test_param_box.addWidget(param_separator,*(1,2))
            test_param_box.addWidget(param_to,*(1,3))
            # Test status and value
            test_param_box.addWidget(status_label, *(2, 0))
            test_param_box.addWidget(returned_status,*(2,1))
            test_param_box.addWidget(ret_label, *(3, 0))
            test_param_box.addWidget(test_val, *(3, 1))

            test_frame.setLayout(test_param_box)
            widgets_view.append(test_frame)


            test_progress = QProgressBar()
            test_progress.setValue(0)
            test_progress.setTextVisible(True)
            progress_txt = "%p%".format(0)
            test_progress.setFormat(progress_txt)
            widgets_view.append(test_progress)

            return widgets_view
        #

        # group structure template
        gt = namedtuple("Group", ["box", "layout", "widgets", "pos"])
        groups = (gt(box=QGroupBox("Generator"), layout=QVBoxLayout(), widgets=[], pos=(0, 0)),
                  gt(box=QGroupBox("Tests"), layout=QVBoxLayout(), widgets=[], pos=(0, 1)))

        # Assign widgets to Generator section
        groups[0].widgets.extend(generator_group())
        groups[1].widgets.extend(test_group())

        # Define widgets and layouts for each group
        # Assign all groups to a grid
        for g in groups:
            for w in g.widgets:
                g.layout.addWidget(w)
            g.layout.addStretch()
            g.box.setLayout(g.layout)
            grid.addWidget(g.box, *g.pos)

        centralWidget.setLayout(grid)
        self.setCentralWidget(centralWidget)
    #
#


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())