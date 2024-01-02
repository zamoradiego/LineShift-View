from PyQt5.QtWidgets import QWidget, QHBoxLayout, QDial, QSlider
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5 import QtCore


class SliderDialWidget(QWidget):
    send_number_signal = pyqtSignal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.number = 0

        self.dial = QDial(self)
        self.dial.setGeometry(QtCore.QRect(10, 10, 71, 81))
        self.dial.setNotchesVisible(True)
        self.dial.setWrapping(True)
        self.dial.setMinimum(0)
        self.dial.setMaximum(100) 

        self.dial.valueChanged.connect(self.dial_value_changed)

        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setGeometry(QtCore.QRect(90, 40, 101, 22))
        self.slider.setMinimum(0)
        self.slider.setMaximum(80)
        self.slider.valueChanged.connect(self.slider_value_changed)
        self.slider_value = 0

        layout = QHBoxLayout()
        layout.addWidget(self.dial)
        layout.addWidget(self.slider)

        self.dial_value = self.dial.value()
        self.dial_number = 0
        self.setLayout(layout)

    def get_number(self):
        return self.number

    def set_number(self, n):
        if n < 0 or n > 8:
            pass
        else:
            self.number = n
            #print(f'Number got and sent from dial/slider {n}')
            self.send_number(n)
            slider_number = n * 10
            self.slider.setValue(slider_number)

    def send_number(self, n):
        self.send_number_signal.emit(str(round(n, 5)))

    def dial_value_changed(self):
        dial_delta = self.dial.value() - self.dial_value
        self.slider.valueChanged.disconnect()
        if dial_delta == 1:
            new_number = self.number + 1/10000
            self.set_number(new_number)
        elif dial_delta == -1:
            new_number = self.number - 1/10000
            self.set_number(new_number)
        elif dial_delta == -100:
            new_number = self.number + 1/10000
            self.set_number(new_number)
        elif dial_delta == 99:
            new_number = self.number - 1/10000
            self.set_number(new_number)
        self.dial_value = self.dial.value()
        self.slider.valueChanged.connect(self.slider_value_changed)
        
    def slider_value_changed(self, value):
        #print(self.number)
        self.set_number(value / 10.000)
