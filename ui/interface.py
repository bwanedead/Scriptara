import os
import logging
from PyQt5.QtWidgets import (
    QMainWindow, QListWidget, QVBoxLayout, QWidget,
    QPushButton, QHBoxLayout, QTextEdit, QAction, 
    QMessageBox, QTableWidget, QTableWidgetItem, 
    QAbstractItemView, QHeaderView, QLabel, QListWidgetItem
)
from PyQt5.QtCore import Qt, pyqtSignal, QEvent
from PyQt5.QtGui import QIcon, QColor, QBrush
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
        self.next_report_button.clicked.connect(self.next_report_signal.emit)
        self.previous_report_button.clicked.connect(self.previous_report_signal.emit)


    def init_ui(self):
        self.setWindowTitle('Scriptara - Scriptara - Word Frequency Analyzer')
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

        # Assurance toggle button
        self.assurance_toggle_button = QPushButton("Assurance Details")
        self.assurance_toggle_button.setCheckable(True)
        self.assurance_toggle_button.setChecked(True)  # Expanded by default
        self.assurance_toggle_button.toggled.connect(self.toggle_assurance_details)
        report_layout.addWidget(self.assurance_toggle_button)

        # Assurance details container
        self.assurance_container = QWidget()
        assurance_layout = QVBoxLayout(self.assurance_container)
        self.assurance_label = QLabel()
        self.assurance_label.setWordWrap(True)
        self.assurance_label.setAlignment(Qt.AlignCenter)
        self.assurance_label.setStyleSheet("margin: 10px;")  # Optional styling
        assurance_layout.addWidget(self.assurance_label)
        report_layout.addWidget(self.assurance_container)

        # Report table
        self.report_table = QTableWidget()
        self.report_table.setColumnCount(5)
        self.report_table.setHorizontalHeaderLabels(["Word", "Count", "Percentage (%)", "Z-Score", "Log Z-Score"])
        self.report_table.horizontalHeader().setStretchLastSection(True)
        self.report_table.setAlternatingRowColors(True)
        self.report_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.report_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.report_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        report_layout.addWidget(self.report_table)

        # Enable mouse tracking and install event filter for hover highlighting
        self.report_table.setMouseTracking(True)
        self.report_table.viewport().installEventFilter(self)

        # Initialize the button layout for Previous and Next buttons
        button_layout = QHBoxLayout()
        self.previous_report_button = QPushButton('Previous Report')
        self.next_report_button = QPushButton('Next Report')
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

    def display_report(self, report_data, report_title, total_word_count):
        if isinstance(report_data, str):
            QMessageBox.information(self, "Information", report_data)
            return

        # Set the header of the report with the report title and total word count
        header_text = f"<h3>{report_title}</h3><p>Total Words: {total_word_count}</p>"
        self.setWindowTitle(header_text)  # Or you can set this text in a label in the UI

        # Clear any existing rows
        self.report_table.setRowCount(0)

        # Set the rows and columns based on report data
        self.report_table.setRowCount(len(report_data))

        for row, data in enumerate(report_data):
            for col, value in enumerate(data):
                # Format numerical data to two decimal places if needed
                if isinstance(value, float):
                    item = QTableWidgetItem(f"{value:.2f}")
                else:
                    item = QTableWidgetItem(str(value))
                
                item.setTextAlignment(Qt.AlignCenter)
                self.report_table.setItem(row, col, item)

        # Set fixed column widths for consistency across reports
        self.report_table.setColumnWidth(0, 150)  # Word column width
        self.report_table.setColumnWidth(1, 100)  # Count column width
        self.report_table.setColumnWidth(2, 120)  # Percentage column width
        self.report_table.setColumnWidth(3, 120)  # Z-Score column width
        self.report_table.setColumnWidth(4, 120)  # Log Z-Score column width

        # Disable auto resizing based on content
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

        # Set alternating row colors with more contrast
        for row in range(self.report_table.rowCount()):
            for col in range(self.report_table.columnCount()):
                item = self.report_table.item(row, col)
                if item:
                    if row % 2 == 0:
                        # Lighter row (default)
                        item.setBackground(self.report_table.palette().base())
                    else:
                        # Darker row (muted soft purple)
                        item.setBackground(QColor(220, 210, 255))  # Adjust color as needed for contrast

        # Enable horizontal scrolling to prevent column wrapping
        self.report_table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.report_table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        # Implement hover highlighting
        self.report_table.setMouseTracking(True)
        self.report_table.viewport().installEventFilter(self)


    def display_assurance_results(self, assurance_results, all_tests_passed, report_title):
        """Displays the assurance results in the assurance box above the report table."""
        # Build the HTML content for the assurance box
        assurance_html = f"<h2>Assurance Tests for {report_title}</h2>"
        assurance_html += "<table border='1' cellpadding='5' cellspacing='0' style='margin: 10px auto; border-collapse: collapse;'>"
        assurance_html += "<tr><th>Metric</th><th>Expected</th><th>Actual</th><th>Status</th></tr>"

        for metric, result in assurance_results.items():
            status_color = "green" if result['Passed'] else "red"
            status_text = "Pass" if result['Passed'] else "Fail"
            actual_value = f"{result['Actual']:.2f}" if isinstance(result['Actual'], float) else result['Actual']
            assurance_html += f"<tr>"
            assurance_html += f"<td>{metric}</td>"
            assurance_html += f"<td>{result['Expected']}</td>"
            assurance_html += f"<td>{actual_value}</td>"
            assurance_html += f"<td style='color: {status_color};'>{status_text}</td>"
            assurance_html += f"</tr>"
        assurance_html += "</table>"

        # Overall test result message
        if all_tests_passed:
            overall_status = "<p style='color: green;'><strong>All assurance tests passed.</strong></p>"
        else:
            overall_status = "<p style='color: red;'><strong>Some assurance tests failed. Please review the discrepancies highlighted above.</strong></p>"

        # Set the text in the assurance label
        self.assurance_label.setText(assurance_html + overall_status)

    def toggle_assurance_details(self, checked):
        """Show or hide the assurance details based on the toggle button state."""
        self.assurance_container.setVisible(checked)

    
    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseMove and source == self.report_table.viewport():
            index = self.report_table.indexAt(event.pos())
            if index.isValid():
                self.highlightRow(index.row())
        return super(MainWindow, self).eventFilter(source, event)

    def highlightRow(self, row):
        for i in range(self.report_table.rowCount()):
            for j in range(self.report_table.columnCount()):
                item = self.report_table.item(i, j)
                if item:
                    if i == row:
                        item.setBackground(QColor(220, 220, 255))  # Highlight color
                    else:
                        # Restore alternating row colors
                        if i % 2 == 0:
                            item.setBackground(QColor(245, 245, 255))  # Light purple/white
                        else:
                            item.setBackground(QColor(225, 225, 245))  # Muted purple

