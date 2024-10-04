from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import QObject
from model.word_analyzer import read_and_preprocess_file, calculate_word_frequencies, get_text_statistics, get_sorted_word_frequencies
from collections import Counter
import pandas as pd
from tabulate import tabulate
from controller.dashboard_controller import DashboardController

import logging

class MainController(QObject):
    def __init__(self, view):
        super().__init__()
        self.view = view
        self.imported_files = set()
        self.file_reports = {}
        self.connect_signals()
        self.current_report_index = -1  # Track the current report
        self.reports_list = []  # Store the order of reports (master + individual)

    def connect_signals(self):
        self.view.import_files_signal.connect(self.import_files)
        self.view.remove_files_signal.connect(self.remove_files)
        self.view.run_analysis_signal.connect(self.run_analysis)
        self.view.next_report_signal.connect(self.next_report)
        self.view.previous_report_signal.connect(self.previous_report)
        self.view.display_report_signal.connect(self.view.display_report)
        self.view.dashboard_signal.connect(self.launch_dashboard)


    def import_files(self):
        print("import_files method called in MainController")
        try:
            logging.debug("Import Files button clicked.")
            options = QFileDialog.Options()
            files, _ = QFileDialog.getOpenFileNames(self.view, "Import Text Files", "",
                                                    "Text Files (*.txt);;All Files (*)",
                                                    options=options)
            if files:
                logging.debug(f"Files selected: {files}")
            else:
                logging.debug("No files selected.")
            new_files = set(files) - self.imported_files
            self.imported_files.update(new_files)
            self.view.update_file_list(list(self.imported_files))

        except Exception as e:
            logging.error(f"An error occurred in import_files: {str(e)}")
            QMessageBox.critical(self.view, "Error", f"An error occurred while importing files:\n{str(e)}")

    def remove_files(self):
        selected_files = self.view.get_selected_files()
        self.imported_files -= set(selected_files)
        self.view.update_file_list(list(self.imported_files))
    

    def run_analysis(self):
        try:
            logging.info("Starting analysis...")

            if not self.imported_files:
                self.view.display_report_signal.emit("No files imported.")
                return

            # Clear previous reports and word frequencies
            self.file_reports.clear()
            self.reports_list = []  # Reset report list
            self.word_frequencies = {}  # New dictionary to store sorted frequencies for each file

            # Initialize a master word counter
            master_word_counts = Counter()

            # Analyze each file and update master counts
            for file in self.imported_files:
                words = read_and_preprocess_file(file)
                word_counts = calculate_word_frequencies(words)
                
                # Get statistics (total words, unique words, and word frequencies)
                stats = get_text_statistics(word_counts)
                
                # Generate a formatted report using the statistics
                report = self.generate_report(stats)  # Only pass the stats dictionary

                self.file_reports[file] = report  # Store individual report
                master_word_counts.update(word_counts)  # Update master counts

                # Store sorted word frequencies for the dashboard
                sorted_frequencies = get_sorted_word_frequencies(word_counts)  # Sort by frequency
                self.word_frequencies[file] = sorted_frequencies  # Save in the word_frequencies dictionary

            # Generate the master report (combined word frequencies across all files)
            master_stats = get_text_statistics(master_word_counts)
            master_report = self.generate_report(master_stats)  # Only pass the stats dictionary
            self.file_reports["Master Report"] = master_report

            # Prepare the order of reports for display (Master + Individual files)
            self.reports_list.append("Master Report")
            self.reports_list.extend(self.imported_files)

            # Display the master report initially
            self.view.display_report_signal.emit(master_report)
            self.current_report_index = 0

        except Exception as e:
            logging.error(f"An error occurred during analysis: {str(e)}")
            self.view.display_report_signal.emit(f"An error occurred: {str(e)}")


    def generate_report(self, stats):
        """Generates a clean report using tabs for column alignment."""

        # Total word count
        total_word_count = stats['total_word_count']

        # Word statistics (list of tuples with (word, count, percentage))
        word_stats = stats['word_stats']

        # Header for the table
        headers = "Word\t\tCount\tPercentage (%)"

        # Format each row using tab characters for column separation
        rows = []
        for word, count, percentage in word_stats:
            row = f"{word}\t\t{count}\t{percentage:.2f}"
            rows.append(row)

        # Combine the headers and rows into the final report
        table = "\n".join(rows)
        report = f"Total Words: {total_word_count}\n\n{headers}\n{table}"
        
        return report

    def next_report(self):
        """Move to the next report in the list."""
        try:
            # Only return if there are no reports
            if not self.file_reports:
                self.view.display_report_signal.emit("No reports available.")
                return  # This return applies only to the empty reports case

            # Move to the next report
            self.current_report_index = (self.current_report_index + 1) % len(self.reports_list)
            current_report_key = self.reports_list[self.current_report_index]
            current_report = self.file_reports[current_report_key]
            self.view.display_report_signal.emit(f"{current_report_key}:\n\n{current_report}")

        except Exception as e:
            logging.error(f"An error occurred while cycling reports: {str(e)}")
            self.view.display_report_signal.emit(f"An error occurred: {str(e)}")

    def previous_report(self):
        """Moves to the previous report (Master and individual)."""
        try:
            if not self.reports_list:
                self.view.display_report_signal.emit("No reports available to display.")
                return

        # Move to the previous report
            self.current_report_index = (self.current_report_index - 1) % len(self.reports_list)
            current_report_key = self.reports_list[self.current_report_index]
            current_report = self.file_reports[current_report_key]
            self.view.display_report_signal.emit(f"{current_report_key}:\n\n{current_report}")

        except Exception as e:
            logging.error(f"An error occurred while moving to the previous report: {str(e)}")
            self.view.display_report_signal.emit(f"An error occurred: {str(e)}")


    def launch_dashboard(self):
        if not hasattr(self, 'word_frequencies') or not self.word_frequencies:
            QMessageBox.warning(self.view, "No Data", "Please run the analysis before opening the dashboard.")
            return
        if not hasattr(self, 'dashboard_controller'):
            self.dashboard_controller = DashboardController(self)
        self.dashboard_controller.show()
