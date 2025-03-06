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
        # Corpus state tracking
        self.single_active_corpus = None   # Name of the single active corpus
        self.multi_active_corpora = set()  # Set of multi-active corpus names
        
        # Set first corpus as active if any exist
        if self.corpora:
            first_corpus = next(iter(self.corpora))
            self.single_active_corpus = first_corpus
            self.active_corpus = self.corpora[first_corpus]
            logging.info(f"Set initial single active corpus: {first_corpus}")

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
                    
                    # Ensure this becomes the active corpus if none is set
                    if self.single_active_corpus is None:
                        self.single_active_corpus = "Default Corpus"
                        self.active_corpus = default_corpus
                        logging.info("Set Default Corpus as single active corpus")
                else:
                    # Add files to existing corpus
                    default_corpus = self.corpora["Default Corpus"]
                    for file in new_files:
                        default_corpus.add_file(file)
                        
                    # Ensure Default Corpus is active if no corpus is active
                    if self.single_active_corpus is None:
                        self.single_active_corpus = "Default Corpus"
                        self.active_corpus = default_corpus
                        logging.info("Set Default Corpus as single active corpus")
                        
                logging.info(f"Imported files stored in Default Corpus: {default_corpus}")
                
                # Update any open dashboard UI
                if hasattr(self, 'dashboard_controller') and self.dashboard_controller.view:
                    self.dashboard_controller.view.update_corpus_indicators()
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
                print(f"[DEBUG] Running analysis for corpus: {corpus_name} with {len(files_to_analyze)} files")
            else:
                files_to_analyze = list(self.imported_files)
                corpus_name = "Default Corpus"
                logging.info("No active corpus; using all imported files.")
                print(f"[DEBUG] Running analysis for Default Corpus with {len(files_to_analyze)} files")
            
            if not files_to_analyze:
                self.view.display_report("No files available for analysis.")
                print(f"[ERROR] No files available for analysis in corpus: {corpus_name}")
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
                print(f"[ERROR] No data to analyze for corpus: {corpus_name}")
                return False
                
            # Store the report in the report manager
            print(f"[DEBUG] Storing report for corpus: {corpus_name} with {len(self.file_reports)} entries")
            self.report_manager.update_report_for_corpus(corpus_name, self.file_reports)
            
            # Verify the report was stored
            stored_report = self.report_manager.get_report_for_corpus(corpus_name)
            if stored_report:
                print(f"[DEBUG] Verified report stored for corpus: {corpus_name}, keys: {list(stored_report.keys())}")
            else:
                print(f"[ERROR] Failed to store report for corpus: {corpus_name}")
                
            # Update any open dashboard
            if hasattr(self, 'dashboard_controller'):
                self.dashboard_controller.refresh_visualizations()
            
            logging.info("Analysis completed successfully")
            return True
            
        except Exception as e:
            logging.error(f"Analysis failed: {str(e)}")
            self.view.display_report(f"Analysis error: {str(e)}")
            print(f"[ERROR] Analysis failed for corpus: {corpus_name}: {str(e)}")
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
            # Create a new corpus
            new_corpus = Corpus(name=corpus_name)
            self.corpora[corpus_name] = new_corpus
            
            # Set as default single active corpus if none exists
            if not hasattr(self, 'single_active_corpus') or self.single_active_corpus is None:
                self.single_active_corpus = corpus_name
                self.active_corpus = new_corpus  # For backward compatibility
                logging.info(f"Set {corpus_name} as default single active corpus")
                
            # Update the UI
            if hasattr(self, 'dashboard_controller') and self.dashboard_controller.view:
                self.dashboard_controller.view.populate_corpora_tree()
                self.dashboard_controller.view.update_corpus_indicators()  # Ensure UI reflects
                
            return new_corpus
        else:
            logging.warning(f"Corpus {corpus_name} already exists.")
            return self.corpora[corpus_name]

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

    def set_active_corpus(self, corpus_name, mode="single"):
        """
        Set a corpus as active in single or multi mode.
        
        Args:
            corpus_name (str): The name of the corpus to set as active
            mode (str): 'single' or 'multi' indicating activation mode
        """
        if corpus_name not in self.corpora:
            logging.warning(f"Corpus {corpus_name} not found.")
            return
        
        if mode == "single":
            # Only update if changing to a different corpus - no toggle off
            if self.single_active_corpus != corpus_name:
                # Deactivate previous single active corpus
                if self.single_active_corpus:
                    logging.info(f"Switching single active from {self.single_active_corpus} to {corpus_name}")
                self.single_active_corpus = corpus_name
                self.active_corpus = self.corpora[corpus_name]  # For backward compatibility
                logging.info(f"Set {corpus_name} as single active corpus")
                
                # Use targeted update instead of full repopulation
                if hasattr(self, 'dashboard_controller') and self.dashboard_controller.view:
                    self.dashboard_controller.view.update_corpus_indicators()
            else:
                logging.info(f"Corpus {corpus_name} already single active, no change")
        elif mode == "multi":
            # Toggle multi-active state
            self.toggle_multi_corpus(corpus_name)
        else:
            logging.error(f"Unknown corpus activation mode: {mode}")

    def toggle_multi_corpus(self, corpus_name):
        """
        Toggle a corpus's multi-active state.
        
        Args:
            corpus_name (str): The name of the corpus to toggle
        """
        if corpus_name not in self.corpora:
            logging.warning(f"Corpus {corpus_name} not found.")
            return
            
        if corpus_name in self.multi_active_corpora:
            self.multi_active_corpora.remove(corpus_name)
            logging.info(f"Removed {corpus_name} from multi-active corpora")
        else:
            self.multi_active_corpora.add(corpus_name)
            logging.info(f"Added {corpus_name} to multi-active corpora: {self.multi_active_corpora}")
        
        # Use targeted update instead of full repopulation
        if hasattr(self, 'dashboard_controller') and self.dashboard_controller.view:
            self.dashboard_controller.view.update_corpus_indicators()

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
        previous_reports = self.file_reports.copy() if hasattr(self, 'file_reports') else {}
        
        # Temporarily set the requested corpus as active
        self.active_corpus = self.corpora[corpus_name]
        
        # Run the analysis - this will update file_reports and store in report_manager
        print(f"[DEBUG] Generating report for corpus: {corpus_name}")
        success = self.run_analysis()
        
        if success:
            # Explicitly ensure the report is stored in the report manager
            # This is redundant with run_analysis but ensures it's definitely stored
            if hasattr(self, 'report_manager'):
                print(f"[DEBUG] Explicitly storing report for corpus: {corpus_name}")
                self.report_manager.update_report_for_corpus(corpus_name, self.file_reports)
                
                # Verify the report was stored
                stored_report = self.report_manager.get_report_for_corpus(corpus_name)
                if stored_report:
                    print(f"[DEBUG] Verified report stored for corpus: {corpus_name}, keys: {list(stored_report.keys())}")
                else:
                    print(f"[ERROR] Failed to store report for corpus: {corpus_name}")
        
        # Restore the original active corpus
        self.active_corpus = previous_active
        
        # Restore the previous file_reports to avoid confusion
        if previous_active:
            print(f"[DEBUG] Restoring previous active corpus: {previous_active.name}")
            self.file_reports = previous_reports
            
        return success

    def has_report_for_corpus(self, corpus_name):
        """
        Check if a report already exists for the specified corpus.
        
        Args:
            corpus_name (str): The name of the corpus to check
            
        Returns:
            bool: True if a report exists, False otherwise
        """
        if hasattr(self, 'report_manager'):
            return self.report_manager.has_report_for_corpus(corpus_name)
        return False

    def debug_report_status(self, corpus_name=None):
        """
        Print debug information about report status for a corpus or all corpora.
        
        Args:
            corpus_name (str, optional): The name of the corpus to check. If None, check all corpora.
        """
        if not hasattr(self, 'report_manager'):
            print("[ERROR] No report manager available")
            return
            
        if corpus_name:
            # Check a specific corpus
            if corpus_name not in self.corpora:
                print(f"[ERROR] Corpus '{corpus_name}' not found")
                return
                
            has_report = self.report_manager.has_report_for_corpus(corpus_name)
            print(f"[DEBUG] Report status for corpus '{corpus_name}': {'Available' if has_report else 'Not available'}")
            
            if has_report:
                report = self.report_manager.get_report_for_corpus(corpus_name)
                print(f"[DEBUG] Report keys for corpus '{corpus_name}': {list(report.keys())}")
                
                # Check if there's a Master Report
                if "Master Report" in report:
                    master_data = report["Master Report"]
                    if "data" in master_data and "word_stats" in master_data["data"]:
                        word_stats = master_data["data"]["word_stats"]
                        print(f"[DEBUG] Master Report for corpus '{corpus_name}' has {len(word_stats)} word stats")
                    else:
                        print(f"[DEBUG] Master Report for corpus '{corpus_name}' has no word stats")
                else:
                    print(f"[DEBUG] No Master Report for corpus '{corpus_name}'")
                    
                # Count individual file reports
                file_reports = [k for k in report.keys() if k != "Master Report"]
                print(f"[DEBUG] Corpus '{corpus_name}' has {len(file_reports)} individual file reports")
        else:
            # Check all corpora
            available_reports = self.report_manager.list_available_reports()
            print(f"[DEBUG] Available reports: {available_reports}")
            
            for corpus_name in self.corpora:
                has_report = corpus_name in available_reports
                print(f"[DEBUG] Report status for corpus '{corpus_name}': {'Available' if has_report else 'Not available'}")
                
                if has_report:
                    report = self.report_manager.get_report_for_corpus(corpus_name)
                    print(f"[DEBUG] Report keys for corpus '{corpus_name}': {list(report.keys())}")
                    
                    # Count individual file reports
                    file_reports = [k for k in report.keys() if k != "Master Report"]
                    print(f"[DEBUG] Corpus '{corpus_name}' has {len(file_reports)} individual file reports")

