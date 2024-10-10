import os
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QTextEdit, QScrollBar
from PyQt5.QtCore import QObject, Qt, QEvent
from PyQt5.QtGui import QTextCharFormat, QColor, QTextCursor, QPalette, QTextFormat
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
        # Initialize the instance variables
        self.word_frequencies = {}
        self.percentage_frequencies = {}
        self.z_scores = {}

    def connect_signals(self):
        self.view.import_files_signal.connect(self.import_files)
        self.view.remove_files_signal.connect(self.remove_files)
        self.view.run_analysis_signal.connect(self.run_analysis)
        self.view.next_report_signal.connect(self.next_report)
        self.view.previous_report_signal.connect(self.previous_report)
        self.view.dashboard_signal.connect(self.launch_dashboard)
        self.view.load_sample_corpus_signal.connect(self.load_sample_corpus)

    def import_files(self, sample_corpus=False):
        """Handles importing files from the UI or loading the sample corpus."""
        try:
            logging.debug("Import Files button clicked.")
            
            if sample_corpus:
                # Load from the predefined sample corpus folder
                sample_corpus_dir = os.path.join(os.path.dirname(__file__), '../sample_corpus')

                # Verify that the directory exists
                if os.path.exists(sample_corpus_dir) and os.path.isdir(sample_corpus_dir):
                    files = [os.path.join(sample_corpus_dir, f) for f in os.listdir(sample_corpus_dir)
                            if os.path.isfile(os.path.join(sample_corpus_dir, f))]
                    logging.debug(f"Sample corpus loaded: {files}")
                else:
                    logging.error("Sample corpus directory not found.")
                    QMessageBox.critical(self.view, "Error", "Sample corpus directory does not exist.")
                    return
            else:
                # Normal file import from user selection
                options = QFileDialog.Options()
                files, _ = QFileDialog.getOpenFileNames(self.view, "Import Text Files", "",
                                                        "Text Files (*.txt);;All Files (*)",
                                                        options=options)

            # Update the imported files list
            if files:
                new_files = set(files) - self.imported_files
                self.imported_files.update(new_files)
                self.view.update_file_list(list(self.imported_files))
            else:
                logging.debug("No files selected or sample corpus is empty.")
        
        except Exception as e:
            logging.error(f"An error occurred in import_files: {str(e)}")
            QMessageBox.critical(self.view, "Error", f"An error occurred while importing files:\n{str(e)}")

    def remove_files(self):
        selected_files = self.view.get_selected_files()
        self.imported_files -= set(selected_files)
        self.view.update_file_list(list(self.imported_files))

    def load_sample_corpus(self):
        """Handles the loading of sample corpus files."""
        self.import_files(sample_corpus=True)  # Call the import method with the sample_corpus flag

    def run_analysis(self):
        try:
            logging.info("Starting analysis...")
            logging.debug(f"Imported files at start of analysis: {self.imported_files}")

            if not self.imported_files:
                self.view.display_report("No files imported.")
                return

            # Clear previous reports and word frequencies
            self.file_reports.clear()
            self.reports_list = []  # Reset report list
            self.word_frequencies.clear()          # Clear raw frequencies
            self.percentage_frequencies.clear()    # Clear percentage frequencies
            self.z_scores.clear()                  # Clear Z-scores

            # Initialize a master word counter
            master_word_counts = Counter()

            # Analyze each file and update master counts
            for file in self.imported_files:
                words = read_and_preprocess_file(file)
                word_counts = calculate_word_frequencies(words)

                # Get statistics (total words, unique words, word frequencies, Z-scores)
                stats = get_text_statistics(word_counts)

                # Generate report data using the statistics
                report_data = self.generate_report(stats)

                self.file_reports[file] = report_data  # Store individual report data
                master_word_counts.update(word_counts)  # Update master counts

                # Extract counts, percentages, and Z-scores from the stats
                frequencies = [count for word, count, _, _, _ in stats['word_stats']]
                percentages = [perc for word, _, perc, _, _ in stats['word_stats']]
                z_scores = [z for word, _, _, z, _ in stats['word_stats']]

                self.word_frequencies[file] = frequencies
                self.percentage_frequencies[file] = percentages
                self.z_scores[file] = z_scores

            # Generate the master report
            master_stats = get_text_statistics(master_word_counts)
            master_report_data = self.generate_report(master_stats)
            self.file_reports["Master Report"] = master_report_data

            # Prepare the order of reports for display
            self.reports_list.append("Master Report")
            self.reports_list.extend(self.imported_files)

            # Display the master report initially
            self.view.display_report(master_report_data)
            self.current_report_index = 0

        except Exception as e:
            logging.error(f"An error occurred during analysis: {str(e)}")
            self.view.display_report(f"An error occurred: {str(e)}")



    def generate_report(self, stats):
        """Prepares the report data for display in the table."""
        total_word_count = stats['total_word_count']
        word_stats = stats['word_stats']
        # Sort word_stats by count in descending order (frequency rank)
        word_stats.sort(key=lambda x: x[1], reverse=True)
        return word_stats

    def next_report(self):
        try:
            if not self.file_reports:
                self.view.display_report("No reports available.")
                return

            self.current_report_index = (self.current_report_index + 1) % len(self.reports_list)
            current_report_key = self.reports_list[self.current_report_index]
            current_report_data = self.file_reports[current_report_key]
            self.view.display_report(current_report_data)

        except Exception as e:
            logging.error(f"An error occurred while cycling reports: {str(e)}")
            self.view.display_report(f"An error occurred: {str(e)}")

    def previous_report(self):
        try:
            if not self.file_reports:
                self.view.display_report("No reports available.")
                return

            self.current_report_index = (self.current_report_index - 1) % len(self.reports_list)
            current_report_key = self.reports_list[self.current_report_index]
            current_report_data = self.file_reports[current_report_key]
            self.view.display_report(current_report_data)

        except Exception as e:
            logging.error(f"An error occurred while moving to the previous report: {str(e)}")
            self.view.display_report(f"An error occurred: {str(e)}")


    def launch_dashboard(self):
        if not hasattr(self, 'word_frequencies') or not self.word_frequencies:
            QMessageBox.warning(self.view, "No Data", "Please run the analysis before opening the dashboard.")
            return
        if not hasattr(self, 'dashboard_controller'):
            self.dashboard_controller = DashboardController(self)
        self.dashboard_controller.show()