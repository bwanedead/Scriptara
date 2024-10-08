import os
import logging
from PyQt5.QtWidgets import (
    QMainWindow, QListWidget, QVBoxLayout, QWidget,
    QPushButton, QHBoxLayout, QTextEdit, QAction, 
    QMessageBox, 
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QListWidgetItem
from ui.styles import dark_mode_stylesheet, light_mode_stylesheet


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
    load_sample_corpus_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()
        # Variables to store the current report index and reports list
        self.current_report_index = 0  # Start at the first report
        self.file_reports_list = []  # Will store the individual reports
        self.connect_signals()

    def connect_signals(self):
        # Connect buttons to signals
        self.import_button.clicked.connect(self.import_files_signal.emit)
        self.remove_button.clicked.connect(self.remove_files_signal.emit)
        self.sample_corpus_button.clicked.connect(self.load_sample_corpus_signal.emit)
        self.run_button.clicked.connect(self.run_analysis_signal.emit)
        self.dashboard_button.clicked.connect(self.dashboard_signal.emit)

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

        # Buttons: Import Files, Remove Files, Sample Corpus
        self.import_button = QPushButton('Import Files')
        self.remove_button = QPushButton('Remove Files')
        self.sample_corpus_button = QPushButton('Load Sample Corpus')

        # Add the buttons to the layout
        file_layout.addWidget(self.import_button)
        file_layout.addWidget(self.remove_button)
        file_layout.addWidget(self.sample_corpus_button)

        # Right pane
        report_layout = QVBoxLayout()
        self.report_box = QTextEdit()
        self.report_box.setPlaceholderText("Report will be shown here...")
        report_layout.addWidget(self.report_box)

        # Initialize the button layout for Previous and Next buttons
        button_layout = QHBoxLayout()

        # Previous/Next buttons
        self.previous_report_button = QPushButton('Previous Report')
        self.next_report_button = QPushButton('Next Report')

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

        # Add layouts to the main layout
        main_layout.addLayout(file_layout)
        main_layout.addLayout(report_layout)

        self.create_menu_bar()
        self.enable_light_mode()


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

    # Method to load the sample corpus files
    def load_sample_corpus(self):
        # Define the path to the sample corpus directory
        sample_corpus_dir = os.path.join(os.getcwd(), 'sample_corpus')  # Adjust path if necessary

        # Check if the sample corpus directory exists
        if os.path.exists(sample_corpus_dir) and os.path.isdir(sample_corpus_dir):
            # Get all text files in the sample corpus directory
            sample_files = [os.path.join(sample_corpus_dir, f) for f in os.listdir(sample_corpus_dir) if f.endswith('.txt') and os.path.isfile(os.path.join(sample_corpus_dir, f))]

            # If there are sample files, add them to the imported files set
            if sample_files:
                new_files = set(sample_files) - self.imported_files  # Only add new files
                self.imported_files.update(new_files)  # Update imported files
                logging.info(f"Sample corpus loaded with files: {sample_files}")

                # Update the file list in the UI
                self.view.update_file_list(list(self.imported_files))
            else:
                logging.warning("No text files found in the sample corpus directory.")
                QMessageBox.warning(self.view, "Error", "No text files found in the sample corpus directory.")
        else:
            logging.error(f"Sample corpus directory not found at: {sample_corpus_dir}")
            QMessageBox.warning(self.view, "Error", f"Sample corpus directory not found at {sample_corpus_dir}.")

