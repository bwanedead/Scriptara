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
from tests.assurance_tests import (
    independent_total_word_count,
    independent_unique_word_count,
    independent_percentage_sum,
    independent_rank_count,
    independent_total_from_counts
)
from model.corpora import Corpus  # Add this import
from model.corpus_report_manager import CorpusReportManager  # Add this import


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
        # New multi-corpus structure
        self.corpora = {}
        self.active_corpus = None
        # Add the report manager
        self.report_manager = CorpusReportManager()

    def connect_signals(self):
        self.view.import_files_signal.connect(self.import_files)
        self.view.remove_files_signal.connect(self.remove_files)
        self.view.run_analysis_signal.connect(self.run_analysis)
        self.view.next_report_signal.connect(self.next_report)
        self.view.previous_report_signal.connect(self.previous_report)
        self.view.dashboard_signal.connect(self.launch_dashboard)
        self.view.load_sample_corpus_signal.connect(self.load_sample_corpus)
        self.view.rename_corpus_signal.connect(self.rename_default_corpus)

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
                
                # Wrap imported files into the default corpus
                if "Default Corpus" not in self.corpora:
                    # Create a new corpus with the files
                    default_corpus = Corpus(name="Default Corpus", file_paths=list(new_files))
                    self.corpora["Default Corpus"] = default_corpus
                    self.active_corpus = default_corpus
                else:
                    # Add files to existing corpus
                    default_corpus = self.corpora["Default Corpus"]
                    for file in new_files:
                        default_corpus.add_file(file)
                logging.info(f"Imported files stored in Default Corpus: {default_corpus}")
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
        """Run analysis on files from the active corpus."""
        try:
            logging.info("Starting analysis...")
            
            # Use the active corpus's files if available; otherwise fallback.
            if self.active_corpus is not None:
                files_to_analyze = self.active_corpus.get_files()
                corpus_name = self.active_corpus.name
                logging.info(f"Active corpus: {corpus_name}")
            else:
                files_to_analyze = list(self.imported_files)
                corpus_name = "Default Corpus"
                logging.info("No active corpus; using all imported files.")
            
            if not files_to_analyze:
                self.view.display_report("No files available for analysis.")
                return False
            
            # Clear previous analysis data.
            self.file_reports.clear()
            self.reports_list = []
            self.word_frequencies.clear()
            self.percentage_frequencies.clear()
            self.z_scores.clear()
            master_word_counts = Counter()
            
            # Process each file in the active corpus.
            for file in files_to_analyze:
                try:
                    words, _ = read_and_preprocess_file(file)
                    word_counts = calculate_word_frequencies(words)
                    stats = get_text_statistics(word_counts)
                    logging.debug(f"Word Stats for {file}: {stats['word_stats']}")
                    
                    self.file_reports[file] = {
                        'data': stats,
                        'title': f"Report for {os.path.basename(file)}"
                    }
                    self.word_frequencies[file] = [count for _, count, _, _, _ in stats['word_stats']]
                    self.percentage_frequencies[file] = [perc for _, _, perc, _, _ in stats['word_stats']]
                    self.z_scores[file] = [z for _, _, _, z, _ in stats['word_stats']]
                    master_word_counts.update(word_counts)
                    
                    # Run assurance tests for each file.
                    assurance_results, all_tests_passed = self.run_assurance_tests(stats)
                    self.file_reports[file]['assurance'] = {
                        'results': assurance_results,
                        'all_passed': all_tests_passed
                    }
                    
                    logging.debug(f"Processed file: {file}")
                except Exception as e:
                    logging.error(f"Error processing file {file}: {str(e)}")
                    continue
            
            # Build the master report.
            if master_word_counts:
                master_stats = get_text_statistics(master_word_counts)
                self.file_reports["Master Report"] = {
                    'data': master_stats,
                    'title': "Master Report"
                }
                logging.debug(f"Master Word Stats: {master_stats['word_stats']}")
                assurance_results, all_tests_passed = self.run_assurance_tests(master_stats)
                self.file_reports["Master Report"]['assurance'] = {
                    'results': assurance_results,
                    'all_passed': all_tests_passed
                }
                
                # Update the reports list.
                self.reports_list = ["Master Report"] + files_to_analyze
                self.current_report_index = 0
                self.generate_report(master_stats, "Master Report")
                self.view.display_assurance_results(assurance_results, all_tests_passed, "Master Report")
            else:
                logging.warning("No data to analyze")
                self.view.display_report("No data available for analysis")
                return False
                
            # Store the report in the report manager (moved outside the if block)
            self.report_manager.update_report_for_corpus(corpus_name, self.file_reports)
                
            # Update any open dashboard
            if hasattr(self, 'dashboard_controller'):
                self.dashboard_controller.refresh_visualizations()
            
            logging.info("Analysis completed successfully")
            return True
            
        except Exception as e:
            logging.error(f"Analysis failed: {str(e)}")
            self.view.display_report(f"Analysis error: {str(e)}")
            return False

    def generate_report(self, stats, report_title):
        """Generates a report including title, total word count, and formatted table."""
        total_word_count = stats['total_word_count']
        word_stats = stats['word_stats']
        # Sort word_stats by count in descending order (frequency rank)
        word_stats.sort(key=lambda x: x[1], reverse=True)

        # Pass the formatted report details to the view
        self.view.display_report(word_stats, report_title, total_word_count)

    def next_report(self):
        try:
            if not self.file_reports:
                self.view.display_report("No reports available.")
                return

            # Move to the next report
            self.current_report_index = (self.current_report_index + 1) % len(self.reports_list)
            current_report_key = self.reports_list[self.current_report_index]
            report_data = self.file_reports[current_report_key]['data']
            report_title = self.file_reports[current_report_key]['title']

            # Generate the report for the new context (the current file or master report)
            self.generate_report(report_data, report_title)

            # Display the corresponding assurance results
            assurance_info = self.file_reports[current_report_key]['assurance']
            self.view.display_assurance_results(
                assurance_info['results'],
                assurance_info['all_passed'],
                report_title
            )

        except Exception as e:
            logging.error(f"An error occurred while cycling reports: {str(e)}")
            self.view.display_report(f"An error occurred: {str(e)}")

    def previous_report(self):
        try:
            if not self.file_reports:
                self.view.display_report("No reports available.")
                return

            # Move to the previous report (circularly)
            self.current_report_index = (self.current_report_index - 1) % len(self.reports_list)
            current_report_key = self.reports_list[self.current_report_index]
            report_data = self.file_reports[current_report_key]['data']
            report_title = self.file_reports[current_report_key]['title']

            # Generate the report for the new context (the current file or master report)
            self.generate_report(report_data, report_title)

            # Display the corresponding assurance results
            assurance_info = self.file_reports[current_report_key]['assurance']
            self.view.display_assurance_results(
                assurance_info['results'],
                assurance_info['all_passed'],
                report_title
            )

        except Exception as e:
            logging.error(f"An error occurred while moving to the previous report: {str(e)}")
            self.view.display_report(f"An error occurred: {str(e)}")

    def run_assurance_tests(self, stats):
        """Runs independent assurance tests and returns the results."""
        # Extract data needed for assurance tests from stats
        total_word_count = stats['total_word_count']
        unique_word_count = stats['unique_word_count']
        word_stats = stats['word_stats']

        # Prepare data for assurance functions
        word_counts = {word: count for word, count, _, _, _ in word_stats}
        words_list = [word for word, count in word_counts.items() for _ in range(count)]

        # Perform independent assurance calculations
        ind_total_word_count = independent_total_word_count(words_list)
        ind_unique_word_count = independent_unique_word_count(words_list)
        ind_percentage_sum = independent_percentage_sum(word_counts)
        ind_rank_count = independent_rank_count(word_stats)
        ind_total_from_counts = independent_total_from_counts(word_counts)

        # Prepare assurance results
        assurance_results = {
            'Total Word Count': {
                'Expected': total_word_count,
                'Actual': ind_total_word_count,
                'Passed': total_word_count == ind_total_word_count
            },
            'Unique Word Count': {
                'Expected': unique_word_count,
                'Actual': ind_unique_word_count,
                'Passed': unique_word_count == ind_unique_word_count
            },
            'Sum of Percentages': {
                'Expected': 100.0,
                'Actual': ind_percentage_sum,
                'Passed': abs(ind_percentage_sum - 100.0) < 0.01  # Allow for small floating point errors
            },
            'Number of Ranks': {
                'Expected': unique_word_count,
                'Actual': ind_rank_count,
                'Passed': unique_word_count == ind_rank_count
            },
            'Total from Counts': {
                'Expected': total_word_count,
                'Actual': ind_total_from_counts,
                'Passed': total_word_count == ind_total_from_counts
            }
        }

        # Determine overall pass/fail status
        all_tests_passed = all(result['Passed'] for result in assurance_results.values())

        return assurance_results, all_tests_passed

    def launch_dashboard(self):
        # Initialize the dashboard controller if it doesn't exist
        if not hasattr(self, 'dashboard_controller'):
            self.dashboard_controller = DashboardController(self)

        # Call show() on the dashboard_controller to create and display the dashboard
        self.dashboard_controller.show()

    def rename_default_corpus(self, new_name):
        """Rename the default corpus based on user input."""
        if "Default Corpus" in self.corpora:
            old_corpus = self.corpora.pop("Default Corpus")
            old_corpus.name = new_name
            self.corpora[new_name] = old_corpus
            self.active_corpus = old_corpus
            logging.info(f"Default Corpus renamed to: {new_name}")
        else:
            logging.warning("No Default Corpus exists to rename.")

    def add_corpus(self, corpus_name):
        """Add a new corpus to the controller."""
        if not hasattr(self, 'corpora'):
            self.corpora = {}
        
        if corpus_name not in self.corpora:
            new_corpus = Corpus(name=corpus_name)
            self.corpora[corpus_name] = new_corpus
            print(f"[DEBUG] Added new corpus: {corpus_name}")
        else:
            print(f"[DEBUG] Corpus {corpus_name} already exists.")

    def add_files_to_corpus(self, corpus_name):
        """Add files to a specific corpus."""
        if corpus_name in self.corpora:
            options = QFileDialog.Options()
            files, _ = QFileDialog.getOpenFileNames(
                self.view, 
                f"Import Files for {corpus_name}", 
                "",
                "Text Files (*.txt);;All Files (*)",
                options=options
            )
            if files:
                corpus = self.corpora[corpus_name]
                for file in files:
                    corpus.add_file(file)
                print(f"[DEBUG] Added files to corpus {corpus_name}: {files}")
                
                # Check if this is the active corpus
                if self.active_corpus and self.active_corpus.name == corpus_name:
                    # Re-run analysis to update reports with new files
                    print(f"[DEBUG] Running analysis after adding files to active corpus")
                    self.run_analysis()
                
                # If we have a dashboard open, refresh its tree
                if hasattr(self, 'dashboard_controller') and \
                   hasattr(self.dashboard_controller.view, 'populate_corpora_tree'):
                    self.dashboard_controller.view.populate_corpora_tree()
            else:
                print(f"[DEBUG] Corpus {corpus_name} not found.")
        else:
            print(f"[DEBUG] Corpus {corpus_name} not found.")

    def remove_corpus(self, corpus_name):
        """Remove a corpus from the controller."""
        if corpus_name in self.corpora:
            del self.corpora[corpus_name]
            # Also remove its report data
            self.report_manager.remove_corpus_report(corpus_name)
            print(f"[DEBUG] Removed corpus: {corpus_name}")
        else:
            print(f"[DEBUG] Corpus {corpus_name} not found.")

    def set_active_corpus(self, corpus_name):
        """Set the active corpus and trigger analysis update."""
        if corpus_name in self.corpora:
            self.active_corpus = self.corpora[corpus_name]
            print(f"[DEBUG] Active corpus set to: {corpus_name}")
            # Re-run analysis with new active corpus
            self.run_analysis()
        else:
            print(f"[DEBUG] Corpus {corpus_name} not found.")

    def get_report_for_corpus(self, corpus_name):
        """Get the analysis report for a specific corpus."""
        return self.report_manager.get_report_for_corpus(corpus_name)
    
    def generate_report_for_corpus(self, corpus_name):
        """
        Run analysis for a specific corpus and store its report.
        
        This allows generating reports without changing the active corpus.
        """
        if corpus_name not in self.corpora:
            logging.error(f"Cannot generate report: corpus '{corpus_name}' not found")
            return False
            
        # Store the current active corpus
        previous_active = self.active_corpus
        
        # Temporarily set the requested corpus as active
        self.active_corpus = self.corpora[corpus_name]
        
        # Run the analysis
        success = self.run_analysis()
        
        # Restore the original active corpus
        self.active_corpus = previous_active
        
        # If we had an active corpus before, restore its report to file_reports
        if previous_active:
            self.file_reports = self.report_manager.get_report_for_corpus(previous_active.name)
            
        return success

