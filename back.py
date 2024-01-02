from os.path import join
from astropy.io import ascii
from PyQt5.QtCore import QObject, pyqtSignal
from collections import defaultdict
from astropy.table import Table
import numpy as np


PATH = './files/'


def read_to_table(path, header_start=0, data_start=1):
    with open(path, 'r') as file:
        dictionary = defaultdict(list)
        for i, line in enumerate(file):
            if i == header_start:
                header = line.split()
            elif i >= data_start:
                line_list = line.split()
                for n, key in enumerate(header):
                    try:
                        entry = line_list[n]
                        try:
                            dictionary[key].append(float(entry))
                        except ValueError:
                            dictionary[key].append(entry)
                    except IndexError:
                        dictionary[key].append(np.nan)
    table = Table(dictionary)
    return table

class Processor(QObject):
    signal_specname = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.signal_coordinates = None
        self.signal_catalog = None
        self.signal_specname.connect(self.open_file)
        self.path = '/home/diego/Desktop/Taller/data/1d_spectra/SGAS1226/1d_spectra'
        self.lines_file = 'common_lines.dat'

    def open_file(self, file_name):
        spectrum = ascii.read(file_name)
        lam = list(spectrum.columns[0])
        flux = list(spectrum.columns[1])
        self.signal_coordinates.emit(lam, flux)





