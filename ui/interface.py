
import os
import logging
from PyQt5.QtWidgets import (
    QMainWindow, QListWidget, QVBoxLayout, QWidget,
    QPushButton, QHBoxLayout, QTextEdit, QAction
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from ui.styles import dark_mode_stylesheet, light_mode_stylesheet
from PyQt5.QtWidgets import QListWidgetItem


# Initialize logging to ensure warnings show up
logging.basicConfig(level=logging.WARNING)


class MainWindow(QMainWindow):
    # Define signals to communicate with the Controller
    import_files_signal = pyqtSignal()
    remove_files_signal = pyqtSignal()
    run_analysis_signal = pyqtSignal()
    display_report_signal = pyqtSignal(str)
    update_file_list_signal = pyqtSignal(list)
    next_report_signal = pyqtSignal()
    previous_report_signal = pyqtSignal()
    dashboard_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()
        # Variables to store the current report index and reports list
        self.current_report_index = 0  # Start at the first report
        self.file_reports_list = []  # Will store the individual reports
        self.connect_signals()

    def init_ui(self):
        self.setWindowTitle('Scriptara - Word Frequency Analyzer')
        self.setGeometry(100, 100, 800, 600)
        
        icon_path = 'path/to/icon.png'
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            logging.warning(f"Icon not found at {icon_path}. Using default icon.")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # Left pane
        file_layout = QVBoxLayout()
        self.import_list = QListWidget()
        self.import_list.setSelectionMode(QListWidget.MultiSelection)
        file_layout.addWidget(self.import_list)

        self.import_button = QPushButton('Import Files')
        self.remove_button = QPushButton('Remove Files')

        # Connect buttons to signals
       # Corrected signal-slot connections
        # init_ui() in MainWindow
        self.import_button.clicked.connect(self.import_files_signal.emit)

        self.remove_button.clicked.connect(self.remove_files_signal.emit)


        file_layout.addWidget(self.import_button)
        file_layout.addWidget(self.remove_button)

        # Right pane
        report_layout = QVBoxLayout()
        self.report_box = QTextEdit()
        self.report_box.setPlaceholderText("Report will be shown here...")
        report_layout.addWidget(self.report_box)

        # Initialize the button layout for Previous and Next buttons
        button_layout = QHBoxLayout()

        # Previous/Next buttons
        self.previous_report_button = QPushButton('Previous Report')
        self.previous_report_button.clicked.connect(self.previous_report_signal.emit)

        self.next_report_button = QPushButton('Next Report')
        self.next_report_button.clicked.connect(self.next_report_signal.emit)

        # Add the buttons in the correct order (Previous, then Next)
        button_layout.addWidget(self.previous_report_button)
        button_layout.addWidget(self.next_report_button)

        # Add the button layout (Previous/Next) above the Lexical and Dashboard buttons
        report_layout.addLayout(button_layout)

        # Analysis and Dashboard buttons
        self.run_button = QPushButton('Lexical Deconstruction')
        self.dashboard_button = QPushButton('Dashboard')
        report_button_layout = QHBoxLayout()
        report_button_layout.addWidget(self.run_button)
        report_button_layout.addWidget(self.dashboard_button)

        report_layout.addLayout(report_button_layout)

        self.run_button.clicked.connect(self.run_analysis_signal.emit)

         # Connect the dashboard button to the dashboard signal
        self.dashboard_button.clicked.connect(self.dashboard_signal.emit)

        # Add layouts to the main layout
        main_layout.addLayout(file_layout)
        main_layout.addLayout(report_layout)

        self.create_menu_bar()
        self.enable_light_mode()

    
    def connect_signals(self):
        # This method will be called by the Controller to connect signals
        pass

    def create_menu_bar(self):
        menubar = self.menuBar()
        view_menu = menubar.addMenu('View')
        for mode, slot in [('Dark Mode', self.enable_dark_mode), ('Light Mode', self.enable_light_mode)]:
            action = QAction(mode, self)
            action.triggered.connect(slot)
            view_menu.addAction(action)

    def enable_dark_mode(self):
        self.setStyleSheet(dark_mode_stylesheet)

    def enable_light_mode(self):
        self.setStyleSheet(light_mode_stylesheet)

    # Slot to display the report
    def display_report(self, report):
        self.report_box.setPlainText(report)

    # Slot to update the file list in the UI
    def update_file_list(self, files):
        self.import_list.clear()
        for file in files:
            item = QListWidgetItem(os.path.basename(file))
            item.setToolTip(file)
            self.import_list.addItem(item)
    

    # Method to get selected files from the list
    def get_selected_files(self):
        return [item.toolTip() for item in self.import_list.selectedItems()]
    


