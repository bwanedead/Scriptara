# dashboard_ui.py

import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class CheckableComboBox(QComboBox):
    selection_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Use a standard item model to hold the items
        self.setModel(QStandardItemModel(self))
        # Connect the view's pressed signal to handle item selection
        self.view().pressed.connect(self.handle_item_pressed)
        # Make the combo box editable to display custom text
        self.setEditable(True)
        # Set the line edit to be read-only
        self.lineEdit().setReadOnly(True)
        # Placeholder text when no files are selected
        self.lineEdit().setPlaceholderText('Select Files...')
        # List to keep track of checked items
        self.checked_items = []
        # Tooltip to display selected files
        self.setToolTip('')
        # Dictionary to store colors for each item
        self.colors = {}
    
    def addItem(self, text, data=None):
        # Create a standard item
        item = QStandardItem(text)
        # Set the item to be enabled and checkable
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
        # Initialize the check state to checked (all files selected by default)
        item.setData(Qt.Checked, Qt.CheckStateRole)
        # Store additional data if provided
        if data is not None:
            item.setData(data, Qt.UserRole)
        # Assign a color to the item
        color = QColor.fromHsv(len(self.colors) * 36 % 360, 255, 200)
        self.colors[text] = color
        item.setData(color, Qt.DecorationRole)  # Set the color decoration
        # Add the item to the model
        self.model().appendRow(item)
        # Add the item to checked items
        self.checked_items.append(text)
        # Update the placeholder
        self.update_placeholder()
    
    def add_special_items(self):
        # Add "Select All" option
        select_all_item = QStandardItem("Select All")
        select_all_item.setFlags(Qt.ItemIsEnabled)
        self.model().insertRow(0, select_all_item)
        # Add "Deselect All" option
        deselect_all_item = QStandardItem("Deselect All")
        deselect_all_item.setFlags(Qt.ItemIsEnabled)
        self.model().insertRow(1, deselect_all_item)
    
    def handle_item_pressed(self, index):
        # Get the item that was pressed
        item = self.model().itemFromIndex(index)
        if item.text() == "Select All":
            self.select_all()
            return
        elif item.text() == "Deselect All":
            self.deselect_all()
            return
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
            # Remove the item from checked items
            self.checked_items.remove(item.text())
        else:
            item.setCheckState(Qt.Checked)
            # Add the item to checked items
            self.checked_items.append(item.text())
        # Update the placeholder and tooltip
        self.update_placeholder()
        # Emit signal to update the plot
        self.selection_changed.emit()
    
    def update_placeholder(self):
        selected_count = len(self.checked_items)
        if selected_count == 0:
            self.lineEdit().setText('Select Files...')
            self.setToolTip('')
        elif selected_count == 1:
            self.lineEdit().setText(self.checked_items[0])
            self.setToolTip(self.checked_items[0])
        else:
            self.lineEdit().setText(f'{selected_count} files selected')
            # Set tooltip with the list of selected files
            self.setToolTip('\n'.join(self.checked_items))
    
    def get_checked_items(self):
        # Return the list of checked items
        return self.checked_items
    
    def select_all(self):
        # Clear the list of checked items
        self.checked_items.clear()
        for index in range(2, self.model().rowCount()):  # Skip special items
            item = self.model().item(index)
            # Set each item's check state to checked
            item.setCheckState(Qt.Checked)
            # Add the item to checked items
            self.checked_items.append(item.text())
        # Update the placeholder and tooltip
        self.update_placeholder()
        # Emit signal to update the plot
        self.selection_changed.emit()
    
    def deselect_all(self):
        for index in range(2, self.model().rowCount()):  # Skip special items
            item = self.model().item(index)
            # Set each item's check state to unchecked
            item.setCheckState(Qt.Unchecked)
        # Clear the list of checked items
        self.checked_items.clear()
        # Update the placeholder and tooltip
        self.update_placeholder()
        # Emit signal to update the plot
        self.selection_changed.emit()

class DashboardWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        # Dictionary to keep track of line objects for highlighting
        self.line_objects = {}
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('Frequency Curves Dashboard')
        self.setGeometry(150, 150, 1000, 600)
    
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
    
        # Main layout is horizontal to have a sidebar and chart area
        main_layout = QHBoxLayout(central_widget)
    
        # Left sidebar for controls
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(5, 5, 5, 5)
        sidebar_layout.setSpacing(10)
    
        # Initialize the custom checkable combo box
        self.combo_box = CheckableComboBox()
        # Add special items ("Select All" and "Deselect All")
        self.combo_box.add_special_items()
        # Get the list of imported files from the controller
        self.file_list = list(self.controller.imported_files)
        for file in self.file_list:
            basename = os.path.basename(file)
            self.combo_box.addItem(basename, data=file)
    
        # Connect signals
        self.combo_box.selection_changed.connect(self.update_plot)
        self.combo_box.view().entered.connect(self.on_combo_hover)
    
        # Add widgets to the sidebar
        sidebar_layout.addWidget(QLabel("Select Files:"))
        sidebar_layout.addWidget(self.combo_box)
        sidebar_layout.addStretch()  # Push everything up
    
        # Add a frame to the sidebar for styling (optional)
        sidebar_frame = QFrame()
        sidebar_frame.setLayout(sidebar_layout)
        sidebar_frame.setFrameShape(QFrame.StyledPanel)
        sidebar_frame.setFixedWidth(350)  # Set the width of the sidebar
    
        # Chart area
        chart_layout = QVBoxLayout()
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        chart_layout.addWidget(self.canvas)
    
        # Add layouts to the main layout
        main_layout.addWidget(sidebar_frame)
        main_layout.addLayout(chart_layout)
    
        # Initial plot
        self.update_plot()
    
    def update_plot(self):
        # Get the list of selected files
        selected_files = []
        for index in range(2, self.combo_box.model().rowCount()):  # Skip special items
            item = self.combo_box.model().item(index)
            if item.checkState() == Qt.Checked:
                # Retrieve the full file path from self.file_list
                file = self.file_list[index - 2]  # Adjust index because of special items
                selected_files.append(file)
    
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_xlabel('Rank')
        ax.set_ylabel('Frequency')
        ax.set_title('Word Frequency Curves')
    
        # Clear previous line references
        self.line_objects.clear()
    
        for file in selected_files:
            frequencies = self.controller.word_frequencies.get(file, [])
            if frequencies:
                ranks = range(1, len(frequencies) + 1)
                basename = os.path.basename(file)
                color = self.combo_box.colors.get(basename, None)
                if color:
                    # Convert QColor to RGB tuple
                    rgb = color.getRgbF()
                    line_color = (rgb[0], rgb[1], rgb[2])
                    # Plot the line with the assigned color
                    line, = ax.plot(ranks, frequencies, label=basename, color=line_color)
                else:
                    # Default color if not found
                    line, = ax.plot(ranks, frequencies, label=basename)
                # Store the line object for highlighting
                self.line_objects[basename] = line
    
        # Remove the legend to prevent clutter
        # if selected_files:
        #     ax.legend()
        if not selected_files:
            ax.text(0.5, 0.5, 'No files selected', transform=ax.transAxes,
                    ha='center', va='center')
    
        ax.set_yscale('log')  # Use logarithmic scale for better visualization
        ax.set_xscale('log')
    
        self.canvas.draw()
    
    def on_combo_hover(self, index):
        # Get the item that is being hovered over
        item = self.combo_box.model().itemFromIndex(index)
        file_name = item.text()
        self.highlight_line(file_name)
    
    def highlight_line(self, file_name):
        # Reset all lines to normal width
        for line in self.line_objects.values():
            line.set_linewidth(1)
        # Highlight the selected line
        if file_name in self.line_objects:
            self.line_objects[file_name].set_linewidth(3)
            self.canvas.draw()
