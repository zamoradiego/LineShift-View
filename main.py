from specvis_test2 import Ui_MainWindow
from PyQt5.QtWidgets import QFileDialog, QAbstractItemView, QHeaderView, QTableWidgetItem, QTableView, QListView, QListWidgetItem, QApplication, QMainWindow, QSlider, QLineEdit, QPushButton, QListWidget, QVBoxLayout, QHBoxLayout, QLabel, QMenu, QAction
from PyQt5.QtCore import QRect, Qt, pyqtSignal, QAbstractTableModel
from PyQt5.QtGui import QColor, QStandardItemModel, QStandardItem, QBrush
import pyqtgraph as pg
import os
import numpy as np
from back import Processor
from collections import defaultdict
from os.path import join
from astropy.io import ascii
PATH = './files/'

import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QAction, QInputDialog

import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QAction, QMenu, QInputDialog

class CustomPlotWidget(pg.PlotWidget):
    def __init__(self, parent=None, **kargs):
        super().__init__(parent, **kargs)

    def contextMenuEvent(self, event):
        # Create a custom context menu
        context_menu = QMenu(self)

        # Add the actions from the default context menu
        for action in self.getViewBox().menu.actions():
            context_menu.addAction(action)

        # Add a separator
        context_menu.addSeparator()

        # Add a new action for "Add System"
        add_system_action = QAction("Add System", self)
        add_system_action.triggered.connect(self.add_system)
        context_menu.addAction(add_system_action)

        # Show the context menu at the cursor position
        context_menu.exec_(event.globalPos())

    def add_system(self):
        # List of system options
        systems = ["System 1", "System 2", "System 3"]

        # Display a list of options using QInputDialog
        selected_system, ok = QInputDialog.getItem(
            self, "Select System", "Select a system:", systems, 0, False
        )

        if ok and selected_system:
            print(f"Adding system: {selected_system}")

class MyWidget(QMainWindow, Ui_MainWindow):

    signal_coordinates = pyqtSignal(list, list)
    signal_addlines = pyqtSignal(str, list, list)

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.signal_specname = None
        self.signal_coordinates.connect(self.update_plot)
        self.signal_addlines.connect(self.add_lines)

        # GRAPH
        self.spectrum_plot = None
        # self.lineEdit.setText('10')
        # self.lineEdit_2.setText('-10')
        # self.lineEdit.textChanged.connect(self.set_ymax)
        # self.lineEdit_2.textChanged.connect(self.set_ymin)
        self.setup_graph()
        self.setStyleSheet("background:grey")

        # SPECTRUM
        self.pushButton.clicked.connect(lambda: self.open_browser())

        # ADD LINE
        self.addsystem_line = self.lineEdit_4
        self.pushButton_2.clicked.connect(self.add_lines)

        self.table_redshift.send_number_signal.connect(self.slider_dial_widget.set_number)
        self.table_redshift.send_number_graph_signal.connect(self.update_lines)
        self.table_redshift.delete_row_signal.connect(self.remove_lines)
        self.table_redshift.checkbox_signal.connect(self.checkbox_lines)
        self.slider_dial_widget.send_number_signal.connect(self.table_redshift.update_number)
        # self.setup_table()

        self.list_lines = defaultdict(dict)

        self.path = '/home/diego/Desktop/Taller/data/1d_spectra/SGAS1226/1d_spectra'
        self.lines_file = 'common_lines.dat'
        self.init_lines()

        #self.setFixedSize(self.size())
        self.setFixedSize(1250, 370)

    def init_lines(self):
        lines = ascii.read(join(PATH, self.lines_file))
        self.line_names = list(lines['col1'])
        self.line_lams = list(lines['col2'])

    def setup_graph(self):
        self.graph = CustomPlotWidget(self.frame)
        pg.setConfigOptions(antialias=True)
        self.graph.plotItem.enableAutoRange(axis='y')
        self.graph.plotItem.setMouseEnabled(y=False)
        self.graph.setLabel('left', "Flux")
        self.graph.setLabel('bottom', "Wavelength", units='A')
        self.graph.setGeometry(QRect(10, 10, 981, 281))

    def open_browser(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _= QFileDialog.getOpenFileName(self,"Select spectrum", "","All Files (*);;Python Files (*.py)", options=options)
        if file_name:
            self.send_filename(file_name)

    def send_filename(self, file_name):
        if self.signal_specname:
            self.signal_specname.emit(file_name)

    def update_plot(self, x, y):
        self.graph.removeItem(self.spectrum_plot)
        self.spectrum_plot = self.graph.plot(x, y)
        xmin, xmax = np.min(x), np.max(x)
        self.graph.setXRange(xmin, xmax)
        self.graph.getViewBox().setLimits(xMin=xmin, xMax=xmax)

    def set_range(self):
        print(self.lineEdit.text(), 'asdf')
        self.graph.setYRange(float(self.lineEdit.text()), float(self.lineEdit_2.text()))

    def add_lines(self):
        redshift = self.addsystem_line.text()
        color = QColor(*np.random.randint(50, 200, 3))
        self.table_redshift.add_row(redshift, color)
        row_number = self.table_redshift.rowCount() - 1
        #print(f'Row coun when added {row_number}')

        system_lines = {}
        z = float(redshift)
        for name, lam in zip(self.line_names, self.line_lams):
            lam = float(lam)
            obs_lam = lam * (1 + z)
            line = pg.InfiniteLine(movable=False, angle=90, label=name, pos=obs_lam, pen=color,
                       labelOpts={'rotateAxis': [1, 0], 'position':0.2, 'color': color, 'movable': True})
            self.graph.addItem(line)
            system_lines[name] = line
        self.list_lines[row_number] = system_lines

    def update_lines(self, redshift, row_number):
        z = float(redshift)
        for name, lam in zip(self.line_names, self.line_lams):
            obs_lam = lam * (1 + z)
            self.list_lines[row_number][name].setPos(obs_lam)

    def remove_lines(self, row_number):
        for line in list(self.list_lines[row_number].values()):
            self.graph.removeItem(line)
        # Get number of rows
        del self.list_lines[row_number]
        self.update_row_numbers()

    def update_row_numbers(self):
        old_key_list = list(self.list_lines.keys())
        new_key_list = np.argsort(list(self.list_lines.keys()))
        key_mapping = dict(zip(old_key_list, new_key_list))
        new_lines = {}
        for old_key in old_key_list:
            new_lines[key_mapping[old_key]] = self.list_lines[old_key]
        self.list_lines = new_lines

    def checkbox_lines(self, row_number, state):
        for line in list(self.list_lines[row_number].values()):
            line.setVisible(state)

    # def autoscale(self):
    #     self.graph.setYRange(np.min(y), np.max(y))

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    app.setStyle('Windows')
    widget = MyWidget()
    widget.show()

    # Signals
    processor = Processor()
    processor.signal_coordinates = widget.signal_coordinates
    widget.signal_specname = processor.signal_specname

    sys.exit(app.exec_())