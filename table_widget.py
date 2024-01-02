import sys
import numpy as np
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, QHBoxLayout, QCheckBox, QAbstractItemView, QColorDialog, QStyledItemDelegate, QHeaderView
from PyQt5.QtGui import QColor


class ColorButtonDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(ColorButtonDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        if index.column() == 3:  # Column 3 (color selection column)
            color = index.data(Qt.BackgroundRole)
            if color and isinstance(color, QColor):
                painter.save()
                painter.fillRect(option.rect, color)
                painter.restore()
        else:
            super(ColorButtonDelegate, self).paint(painter, option, index)

    def createEditor(self, parent, option, index):
        if index.column() == 3:  # Column 3 (color selection column)
            color_dialog = QColorDialog(parent)
            return color_dialog
        else:
            return super(ColorButtonDelegate, self).createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        if index.column() == 3:  # Column 3 (color selection column)
            color = index.data(Qt.BackgroundRole)
            if color and isinstance(color, QColor):
                editor.setCurrentColor(color)
        else:
            super(ColorButtonDelegate, self).setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        if index.column() == 3:  # Column 3 (color selection column)
            color = editor.currentColor()
            model.setData(index, color, Qt.BackgroundRole)
            model.setData(index, QSize(5, 5), Qt.SizeHintRole)  # Optional: Set the size of the color cell
        else:
            super(ColorButtonDelegate, self).setModelData(editor, model, index)


class CustomTableWidget(QTableWidget):
    # SIGNALS
    send_number_signal = pyqtSignal(float)
    send_number_graph_signal = pyqtSignal(float, float)
    delete_row_signal = pyqtSignal(int)
    checkbox_signal = pyqtSignal(int, bool)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    def initUI(self):
        self.setSelectionMode(QAbstractItemView.NoSelection)  # Disable row selection
        self.setColumnCount(4)  # 4 columns now, one for each checkbox, number, button, and color
        self.setHorizontalHeaderLabels(['Show', 'Redshift', 'Color', 'Delete'])
        delegate = ColorButtonDelegate(self)
        self.setItemDelegateForColumn(3, delegate)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.cellClicked.connect(self.cell_clicked)  # Connect cellClicked signal
        self.verticalHeader().setVisible(False)
        self.itemChanged.connect(self.item_changed)

    def add_row(self, number, color=QColor(*np.random.randint(50, 200, 3))):
        row_count = self.rowCount()
        self.setRowCount(row_count + 1)

        checkbox_widget = QCheckBox()
        checkbox_widget.setChecked(True)

        # Create a custom widget to center-align the checkbox
        checkbox_container = QWidget()
        checkbox_layout = QHBoxLayout(checkbox_container)
        checkbox_layout.addWidget(checkbox_widget)
        checkbox_layout.setAlignment(Qt.AlignCenter)

        # Set the custom widget as the cell widget
        self.setCellWidget(row_count, 0, checkbox_container)

        number_item = QTableWidgetItem()
        number_item.setData(Qt.DisplayRole, number)  # Default number value is 0

        button = QPushButton('Delete')
        button.clicked.connect(self.delete_row)

        color_item = QTableWidgetItem()  # Empty item for color selection
        color_item.setBackground(color)

        self.setItem(row_count, 1, number_item)
        self.setItem(row_count, 2, color_item)
        self.setCellWidget(row_count, 3, button)

        # Connect the stateChanged signal of the checkbox widget to the custom slot
        checkbox_widget.stateChanged.connect(lambda state, row=row_count: self.checkbox_state_changed(row, state))
    def delete_row(self):
        button = self.sender() # PROBLEM?
        row_number = self.indexAt(button.pos()).row()
        self.delete_row_signal.emit(row_number)
        if row_number >= 0:
            self.removeRow(row_number)

    def update_number(self, number):
        #print(f' Updating number to {number}')
        # Get the selected row
        current_row = self.currentRow()
        self.send_number_graph_signal.emit(float(number), current_row)

        if current_row >= 0:
            number_item = self.item(current_row, 1)
            if number_item:
                number_item.setData(Qt.DisplayRole, number)

    def checkbox_state_changed(self, row, state):
        checked = state == Qt.Checked
        self.checkbox_signal.emit(row, state)

    def cell_clicked(self, row, col):
        number_item = self.item(row, 1)
        number = float(number_item.data(Qt.DisplayRole))
        self.send_number_signal.emit(number)
        print(f'Cell clicked in row {row} number {number}')

    def item_changed(self, item):
        if item.column() == 1:  # Check if the changed item is in the "Number" column
            row = item.row()
            text = item.text()
            print(f'Item in row {row}, column 1 changed to: {text}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle('Testing')
    layout = QVBoxLayout(window)
        #TESTING BUTTON
    button = QPushButton('Add', window)
    table = CustomTableWidget(window)
    button.clicked.connect(table.add_row)

    layout.addWidget(table)
    layout.addWidget(button)

    window.show()
    sys.exit(app.exec_())

