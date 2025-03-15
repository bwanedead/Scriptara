# cell_layout.py
from visualizations.metric_visualizations import FrequencyReportsAggregator
import os
import math
import pyqtgraph as pg
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
                            QHBoxLayout, QPushButton, QHeaderView, QComboBox, QToolButton, QDialog, QListWidget, QScrollArea, QCheckBox
                            )
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QBrush, QPalette
from pyqtgraph import PlotWidget, BarGraphItem, mkPen
import numpy as np


# Standardized table styling function for consistent appearance across all tables
def apply_standard_table_styling(table_widget):
    """Apply standardized styling to any table widget to ensure visual consistency"""
    # Set base table styling
    table_widget.setStyleSheet("""
        QTableWidget {
            background-color: #2b2b2b;
            color: white;
            gridline-color: #3a3a3a;  /* Softer grid lines */
            border: none;
        }
        QTableWidget::item {
            padding: 4px;
            border: none;
        }
        QTableWidget::item:selected {
            background-color: #3d3d3d;
        }
        QHeaderView::section {
            background-color: #3a3a3a;  /* Softer header background */
            color: white;
            padding: 4px;
            border: 1px solid #444;  /* Softer border */
            font-weight: bold;
        }
        QTableCornerButton::section {
            background-color: #3a3a3a;
            border: 1px solid #444;
        }
    """)
    
    # Configure table behavior
    table_widget.setEditTriggers(QTableWidget.NoEditTriggers)  # Read-only
    table_widget.setAlternatingRowColors(True)
    table_widget.setSelectionBehavior(QTableWidget.SelectRows)
    table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    table_widget.verticalHeader().setVisible(False)  # Hide row numbers
    
    # Use dotted grid lines for a softer appearance
    table_widget.setShowGrid(True)
    table_widget.setGridStyle(Qt.DotLine)  # Dotted lines instead of solid
    
    # Set row height
    table_widget.verticalHeader().setDefaultSectionSize(30)  # Match original BO table row height
    
    # Set alternating row colors with more noticeable but still gentle contrast
    palette = table_widget.palette()
    palette.setColor(QPalette.AlternateBase, QColor(50, 50, 50))  # Lighter for alternating rows
    palette.setColor(QPalette.Base, QColor(35, 35, 35))          # Darker for main rows
    table_widget.setPalette(palette)


class BaseMetricLayout:
    def __init__(self, vis):
        self.vis = vis
        self.layout_widget = None
        self.corpus_label = None  # Add reference to update corpus indicator later

    def generate_layout(self):
        """Generate the base layout with refresh and manage corpora functionality."""
        self.layout_widget = QWidget()
        layout = QVBoxLayout(self.layout_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # Header with title, corpus indicator, refresh, and manage buttons
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel(self.get_title())
        title_label.setStyleSheet("color: #fff; font-size: 14px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        # Add corpus indicator, updated for multiple corpora
        if hasattr(self.vis, 'corpus_ids') and self.vis.corpus_ids:
            if len(self.vis.corpus_ids) == 1:
                corpus_text = f"Corpus: {self.vis.corpus_ids[0]}"
            else:
                corpus_text = f"Corpora: {len(self.vis.corpus_ids)} selected"
            self.corpus_label = QLabel(corpus_text)
            self.corpus_label.setStyleSheet("color: #aaa; font-size: 12px;")
            header_layout.addWidget(self.corpus_label)
        # Fallback to single corpus_id if corpus_ids isn't set yet
        elif hasattr(self.vis, 'corpus_id') and self.vis.corpus_id:
            self.corpus_label = QLabel(f"Corpus: {self.vis.corpus_id}")
            self.corpus_label.setStyleSheet("color: #aaa; font-size: 12px;")
            header_layout.addWidget(self.corpus_label)
        
        header_layout.addStretch()
        
        # Existing refresh button (unchanged)
        refresh_btn = QToolButton()
        refresh_btn.setText("⟳")
        refresh_btn.setToolTip("Refresh visualization")
        refresh_btn.setStyleSheet("""
            QToolButton {
                color: #888888;
                border: none;
                font-size: 16px;
                padding: 4px;
            }
            QToolButton:hover {
                color: #ffffff;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_visualization)
        header_layout.addWidget(refresh_btn)
        
        # New "Manage" button for CorpusSelector
        manage_btn = QToolButton()
        manage_btn.setText("Corpus Manager")
        manage_btn.setToolTip("Select Corpora to Display")
        manage_btn.setStyleSheet("""
            QToolButton {
                color: #888888;
                border: none;
                font-size: 16px;
                padding: 4px;
            }
            QToolButton:hover {
                color: #ffffff;
            }
        """)
        manage_btn.clicked.connect(self.open_corpus_selector)
        header_layout.addWidget(manage_btn)
        
        layout.addLayout(header_layout)
        
        # Add content area
        self.add_content(layout)
        
        return self.layout_widget

    def get_title(self):
        """Override in subclasses to provide specific titles."""
        return "Metric Visualization"

    def add_content(self, layout):
        """Override in subclasses to add specific visualization content."""
        pass

    def refresh_visualization(self):
        """Universal refresh method that works with all visualization types."""
        print(f"[DEBUG] BaseMetricLayout.refresh_visualization for corpus: {getattr(self.vis, 'corpus_id', 'unknown')}")
        
        # First update the data source (BaseVisualization method)
        if hasattr(self.vis, 'update_data_source'):
            print(f"[DEBUG] Calling update_data_source on {type(self.vis).__name__}")
            self.vis.update_data_source()
        
        # Then update the data (for BO score visualizations)
        if hasattr(self.vis, 'update_data'):
            print(f"[DEBUG] Calling update_data on {type(self.vis).__name__}")
            self.vis.update_data()
        
        # Finally update the plot (for frequency distribution)
        if hasattr(self.vis, 'update_plot'):
            print(f"[DEBUG] Calling update_plot on {type(self.vis).__name__}")
            self.vis.update_plot()
            
        print(f"[DEBUG] Visualization refreshed for corpus: {getattr(self.vis, 'corpus_id', 'unknown')}")

    def open_corpus_selector(self):
        """Open the CorpusSelector dialog to manage corpora selection."""
        if not hasattr(self.vis, 'controller'):
            print("[ERROR] Visualization has no controller")
            return
            
        # Get available corpora from controller
        available_corpora = []
        if hasattr(self.vis.controller, 'get_available_corpora'):
            available_corpora = self.vis.controller.get_available_corpora()
        elif hasattr(self.vis.controller, 'corpora'):
            # Fallback to using corpora dictionary keys
            available_corpora = list(self.vis.controller.corpora.keys())
        
        if not available_corpora:
            print("[WARNING] No available corpora found")
            return
            
        # Get currently selected corpora
        current_selection = []
        if hasattr(self.vis, 'corpus_ids') and self.vis.corpus_ids:
            current_selection = self.vis.corpus_ids
        elif hasattr(self.vis, 'corpus_id') and self.vis.corpus_id:
            current_selection = [self.vis.corpus_id]
            
        selector = CorpusSelector(self.layout_widget)
        selector.corpus_changed.connect(self.on_corpus_selection_changed)
        selector.open_selector(available_corpora, current_selection)

    def on_corpus_selection_changed(self, selected_corpora):
        """Update the visualization's corpus_ids and refresh the display."""
        self.vis.set_corpus_ids(selected_corpora)
        if self.corpus_label:
            if len(selected_corpora) == 1:
                self.corpus_label.setText(f"Corpus: {selected_corpora[0]}")
            else:
                self.corpus_label.setText(f"Corpora: {len(selected_corpora)} selected")
        self.refresh_visualization()


class FrequencyDistributionLayout(BaseMetricLayout):
    def get_title(self):
        return "Frequency Distribution"

    def add_content(self, layout):
        plot_wid = self.vis.widget()
        layout.addWidget(plot_wid)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)

        controls_layout.addWidget(QLabel("Distribution:"))
        mode_combo = QComboBox()
        mode_combo.addItems(["nominal", "percentage", "z_score"])
        mode_combo.setCurrentText(self.vis.current_mode)
        mode_combo.currentIndexChanged.connect(lambda: self.vis.set_mode(mode_combo.currentText()))
        controls_layout.addWidget(mode_combo)

        x_log_btn = QToolButton()
        x_log_btn.setCheckable(True)
        x_log_btn.setText("X Log")
        x_log_btn.toggled.connect(self.vis.set_x_log)
        controls_layout.addWidget(x_log_btn)

        y_log_btn = QToolButton()
        y_log_btn.setCheckable(True)
        y_log_btn.setText("Y Log")
        y_log_btn.toggled.connect(self.vis.set_y_log)
        controls_layout.addWidget(y_log_btn)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

    def refresh_visualization(self):
        """Refresh the frequency distribution plot."""
        print(f"[DEBUG] FrequencyDistributionLayout.refresh_visualization called for corpus: {getattr(self.vis, 'corpus_id', 'unknown')}")
        # First make sure we have the latest data
        if hasattr(self.vis, 'update_data_source'):
            self.vis.update_data_source()
        
        # Then update the plot
        if hasattr(self.vis, 'update_plot'):
            self.vis.update_plot()
        
        print(f"[DEBUG] Frequency distribution refreshed for corpus: {getattr(self.vis, 'corpus_id', 'unknown')}")


class FrequencyReportsLayout(QWidget):
    def __init__(self, controller, corpus_id=None, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.corpus_id = corpus_id
        self.aggregated_list = []
        self.current_index = 0
        
        print(f"[DEBUG] FrequencyReportsLayout initialized with corpus_id: {corpus_id}")
        
        # Set dark background to match application theme
        self.setStyleSheet("background-color: #2b2b2b; color: white;")
        
        # Create the layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)  # Tighter margins
        main_layout.setSpacing(5)  # Reduce spacing
        
        # Create header with report title (use exact same title layout as BO table)
        self.title_label = QLabel("Frequency Reports")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
        main_layout.addWidget(self.title_label)
        
        # Create top navigation row (like BO table)
        top_nav = QHBoxLayout()
        top_nav.setContentsMargins(0, 0, 0, 0)
        
        # Previous button
        self.prev_button = QPushButton("← Previous")
        self.prev_button.setFixedWidth(100)
        self.prev_button.setStyleSheet("background-color: #444; color: white; border: none; padding: 4px 8px;")
        self.prev_button.clicked.connect(self.show_previous_report)
        
        # Navigation counter
        self.report_label = QLabel("Report: 1 of 1")
        self.report_label.setAlignment(Qt.AlignCenter)
        self.report_label.setStyleSheet("color: #aaa; font-size: 12px;")
        
        # Next button
        self.next_button = QPushButton("Next →")
        self.next_button.setFixedWidth(100)
        self.next_button.setStyleSheet("background-color: #444; color: white; border: none; padding: 4px 8px;")
        self.next_button.clicked.connect(self.show_next_report)
        
        top_nav.addWidget(self.prev_button)
        top_nav.addStretch(1)
        top_nav.addWidget(self.report_label)
        top_nav.addStretch(1)
        top_nav.addWidget(self.next_button)
        
        main_layout.addLayout(top_nav)
        
        # Stats label for total/unique words
        self.stats_label = QLabel()
        self.stats_label.setAlignment(Qt.AlignCenter)
        self.stats_label.setStyleSheet("color: #ddd; font-size: 12px; margin-top: 2px; margin-bottom: 2px;")
        main_layout.addWidget(self.stats_label)
        
        # Create table with matching style to BO Score Table
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(6)  # Add columns as requested
        self.table_widget.setHorizontalHeaderLabels([
            "Rank", "Word", "Count", "Percentage", "Z-Score", "Log Z-Score"
        ])
        
        # Apply standardized table styling
        apply_standard_table_styling(self.table_widget)
        
        # Match the corpus indicator styling and position from BO Score Table
        corpus_layout = QHBoxLayout()
        corpus_layout.setContentsMargins(0, 0, 0, 0)
        corpus_layout.addStretch(1)
        self.corpus_label = QLabel(f"Corpus: {corpus_id}")
        self.corpus_label.setStyleSheet("color: #aaa; font-size: 12px;")
        corpus_layout.addWidget(self.corpus_label)
        
        main_layout.addWidget(self.table_widget)
        main_layout.addLayout(corpus_layout)
        
        # Disable buttons until we have data
        self.prev_button.setEnabled(False)
        self.next_button.setEnabled(False)
        
        # Update with data if we have a corpus_id
        if self.corpus_id:
            self.update_data_source()
        else:
            print(f"[ERROR] FrequencyReportsLayout has no corpus_id, cannot fetch data")

    def update_data_source(self):
        """
        Fetch and update the data source using the controller and corpus_id.
        """
        try:
            print(f"[DEBUG] FrequencyReportsLayout updating data source for corpus_id: {self.corpus_id}")
            
            # Reset existing data
            self.aggregated_list = []
            self.current_index = 0
            
            if not self.controller:
                print(f"[ERROR] FrequencyReportsLayout has no controller reference")
                return
                
            if not self.corpus_id:
                print(f"[ERROR] FrequencyReportsLayout has no corpus_id")
                return
            
            # Update corpus indicator  
            self.corpus_label.setText(f"Corpus: {self.corpus_id}")
                
            # Check if report exists for this corpus
            has_report = False
            if hasattr(self.controller, 'has_report_for_corpus'):
                has_report = self.controller.has_report_for_corpus(self.corpus_id)
                print(f"[DEBUG] FrequencyReportsLayout checking for report: {has_report}")
                
            # Generate report if needed
            if not has_report and hasattr(self.controller, 'generate_report_for_corpus'):
                print(f"[DEBUG] FrequencyReportsLayout generating report for corpus: {self.corpus_id}")
                success = self.controller.generate_report_for_corpus(self.corpus_id)
                if not success:
                    print(f"[ERROR] FrequencyReportsLayout failed to generate report")
                    return
                    
            # Get the reports for this corpus
            if hasattr(self.controller, 'get_report_for_corpus'):
                file_reports = self.controller.get_report_for_corpus(self.corpus_id)
                if file_reports:
                    print(f"[DEBUG] FrequencyReportsLayout got report with {len(file_reports)} entries")
                    # Build the aggregated list
                    self._build_aggregated_list(file_reports)
                    # Update the table with the first report
                    if self.aggregated_list:
                        self.update_table()
                        # Enable navigation if we have multiple reports
                        self.prev_button.setEnabled(len(self.aggregated_list) > 1)
                        self.next_button.setEnabled(len(self.aggregated_list) > 1)
                        print(f"[DEBUG] FrequencyReportsLayout loaded {len(self.aggregated_list)} reports")
                    else:
                        print(f"[ERROR] FrequencyReportsLayout got empty aggregated list")
                else:
                    print(f"[ERROR] FrequencyReportsLayout got empty report")
            else:
                print(f"[ERROR] Controller has no get_report_for_corpus method")
                
        except Exception as e:
            import traceback
            print(f"[ERROR] FrequencyReportsLayout update_data_source failed: {e}")
            traceback.print_exc()

    def _build_aggregated_list(self, file_reports):
        """
        Build a list of reports from the file_reports dictionary.
        Put "Master Report" first if it exists.
        """
        try:
            self.aggregated_list = []
            
            # Add Master Report first if it exists
            if "Master Report" in file_reports:
                self.aggregated_list.append({
                    "title": "Master Report",
                    "data": file_reports["Master Report"]["data"]
                })
                print(f"[DEBUG] Added Master Report to aggregated list")
            
            # Add individual file reports
            for key, report in file_reports.items():
                if key != "Master Report":
                    # For file paths, just show the filename
                    display_name = key
                    if '/' in key or '\\' in key:
                        display_name = os.path.basename(key)
                        
                    self.aggregated_list.append({
                        "title": display_name,
                        "data": report["data"]
                    })
                    
            print(f"[DEBUG] Built aggregated list with {len(self.aggregated_list)} reports")
            
            # Update report counter display
            self.report_label.setText(f"Report: 1 of {len(self.aggregated_list)}")
            
        except Exception as e:
            import traceback
            print(f"[ERROR] FrequencyReportsLayout _build_aggregated_list failed: {e}")
            traceback.print_exc()
            
    def update_table(self):
        """
        Update the table with the current report data.
        """
        try:
            if not self.aggregated_list:
                print(f"[ERROR] No aggregated list data to display")
                return
                
            if self.current_index < 0 or self.current_index >= len(self.aggregated_list):
                print(f"[ERROR] Invalid current_index: {self.current_index}")
                return
                
            # Get the current report
            report = self.aggregated_list[self.current_index]
            
            # Update the report title
            self.title_label.setText(f"Frequency Reports: {report['title']}")
            
            # Update the report counter
            self.report_label.setText(f"Report: {self.current_index + 1} of {len(self.aggregated_list)}")
            
            # Get the report data
            if 'data' not in report:
                print(f"[ERROR] No data in report at index {self.current_index}")
                return
                
            report_data = report['data']
            if 'word_stats' not in report_data:
                print(f"[ERROR] No word_stats in report data at index {self.current_index}")
                return
                
            word_stats = report_data['word_stats']
            
            # Update the stats label
            total_words = report_data.get('total_word_count', 0)
            unique_words = report_data.get('unique_word_count', 0)
            self.stats_label.setText(f"Total Words: {total_words} | Unique Words: {unique_words}")
            
            # Sort word stats by count in descending order (if not already sorted)
            word_stats.sort(key=lambda x: x[1], reverse=True)
            
            # Block signals during updates to improve performance
            self.table_widget.blockSignals(True)
            
            # Clear the table first to avoid any leftover data
            self.table_widget.clearContents()
            
            # Set the number of rows
            self.table_widget.setRowCount(len(word_stats))
            
            for row, stats in enumerate(word_stats):
                # Each stats entry is (word, count, percentage, z_score, bucket)
                word, count, percentage, z_score, bucket = stats
                
                # Calculate log z-score (avoid log of negative values)
                log_z_score = 0
                if z_score > 0:
                    log_z_score = round(math.log10(z_score), 2)
                elif z_score < 0:
                    log_z_score = -round(math.log10(abs(z_score)), 2)
                
                # Add rank (row + 1)
                rank_item = QTableWidgetItem(str(row + 1))
                rank_item.setTextAlignment(Qt.AlignCenter)
                self.table_widget.setItem(row, 0, rank_item)
                
                # Add word - left align text for better readability
                word_item = QTableWidgetItem(word)
                self.table_widget.setItem(row, 1, word_item)
                
                # Add count - center align all numeric values
                count_item = QTableWidgetItem(str(count))
                count_item.setTextAlignment(Qt.AlignCenter)
                self.table_widget.setItem(row, 2, count_item)
                
                # Add percentage (format to 2 decimal places)
                percentage_item = QTableWidgetItem(f"{percentage:.2f}")
                percentage_item.setTextAlignment(Qt.AlignCenter)
                self.table_widget.setItem(row, 3, percentage_item)
                
                # Add z-score (format to 2 decimal places)
                z_score_item = QTableWidgetItem(f"{z_score:.2f}")
                z_score_item.setTextAlignment(Qt.AlignCenter)
                self.table_widget.setItem(row, 4, z_score_item)
                
                # Add log z-score
                log_z_item = QTableWidgetItem(f"{log_z_score:.2f}")
                log_z_item.setTextAlignment(Qt.AlignCenter)
                self.table_widget.setItem(row, 5, log_z_item)
            
            # Enable signals again
            self.table_widget.blockSignals(False)
            
            print(f"[DEBUG] Updated table with {len(word_stats)} rows for report {self.current_index + 1}")
            
        except Exception as e:
            import traceback
            print(f"[ERROR] FrequencyReportsLayout update_table failed: {e}")
            traceback.print_exc()

    def show_previous_report(self):
        """
        Show the previous report in the list.
        """
        if self.aggregated_list and self.current_index > 0:
            self.current_index -= 1
            self.update_table()
            print(f"[DEBUG] Showing previous report, now at index {self.current_index}")

    def show_next_report(self):
        """
        Show the next report in the list.
        """
        if self.aggregated_list and self.current_index < len(self.aggregated_list) - 1:
            self.current_index += 1
            self.update_table()
            print(f"[DEBUG] Showing next report, now at index {self.current_index}")

    def refresh(self):
        """
        Refresh the data and update the display.
        """
        print(f"[DEBUG] FrequencyReportsLayout refresh called")
        # First get fresh data
        self.update_data_source()
        # Then update the table
        if self.aggregated_list:
            self.current_index = 0  # Reset to first report
            self.update_table()
            print(f"[DEBUG] FrequencyReportsLayout refreshed with {len(self.aggregated_list)} reports")
        else:
            print(f"[ERROR] FrequencyReportsLayout refresh found no reports")


class BOScoreBarLayout:
    """
    Renders a bar chart using pyqtgraph for BOn1 and BOn2 data.
    Includes toggle buttons to show/hide each dataset and limit view to top words.
    """

    def __init__(self, vis):
        self.vis = vis  # Instance of BOScoreBarVisualization
        self.plot_widget = None

        # Toggles for visibility
        self.show_bon1 = True  # Default to showing BOn1
        self.show_bon2 = False  # Default to hiding BOn2
        self.show_top_only = True  # Default to showing only top words
        self.max_bars = 50  # Default number of bars to show

        # Store references to prevent garbage collection
        self.widgets = {}
        print("[DEBUG] BOScoreBarLayout initialized.")

    def generate_layout(self):
        layout_widget = QWidget()
        layout = QVBoxLayout(layout_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # Header layout with title, corpus indicator and refresh button
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title_label = QLabel("BO Score Bar Chart")
        title_label.setStyleSheet("color: #fff; font-size:16px;")
        header_layout.addWidget(title_label)
        
        # Add corpus indicator if available
        if hasattr(self.vis, 'corpus_ids') and self.vis.corpus_ids:
            if len(self.vis.corpus_ids) == 1:
                corpus_text = f"Corpus: {self.vis.corpus_ids[0]}"
            else:
                corpus_text = f"Corpora: {len(self.vis.corpus_ids)} selected"
            corpus_label = QLabel(corpus_text)
            corpus_label.setStyleSheet("color: #aaa; font-size: 12px;")
            header_layout.addWidget(corpus_label)
            
        header_layout.addStretch()
        
        # Add refresh button
        refresh_btn = QToolButton()
        refresh_btn.setText("⟳")
        refresh_btn.setToolTip("Refresh visualization")
        refresh_btn.setStyleSheet("""
            QToolButton {
                color: #888888;
                border: none;
                font-size: 16px;
                padding: 4px;
            }
            QToolButton:hover {
                color: #ffffff;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_visualization)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)

        # Controls for toggling visibility
        controls_layout = QHBoxLayout()

        # Toggle BOn1 button - USING ORIGINAL SIGNAL APPROACH
        bon1_btn = QToolButton()
        bon1_btn.setText("Toggle BOn1")
        bon1_btn.setCheckable(True)
        bon1_btn.setChecked(self.show_bon1)
        bon1_btn.clicked.connect(
            lambda: print("[DEBUG] bon1_btn clicked (signal emitted)") or self.on_bon1_toggle_click()
        )
        bon1_btn.setFocusPolicy(Qt.ClickFocus)  # Ensure it can receive focus
        controls_layout.addWidget(bon1_btn)
        self.widgets['bon1_button'] = bon1_btn  # Prevent GC
        print("[DEBUG] Connected bon1_btn clicked signal.")

        # Toggle BOn2 button - USING ORIGINAL SIGNAL APPROACH
        bon2_btn = QToolButton()
        bon2_btn.setText("Toggle BOn2")
        bon2_btn.setCheckable(True)
        bon2_btn.setChecked(self.show_bon2)
        bon2_btn.clicked.connect(
            lambda: print("[DEBUG] bon2_btn clicked (signal emitted)") or self.on_bon2_toggle_click()
        )
        bon2_btn.setFocusPolicy(Qt.ClickFocus)  # Ensure it can receive focus
        controls_layout.addWidget(bon2_btn)
        self.widgets['bon2_button'] = bon2_btn  # Prevent GC
        print("[DEBUG] Connected bon2_btn clicked signal.")

        # Toggle for showing top 50 vs all - USING ORIGINAL SIGNAL APPROACH
        top_only_btn = QToolButton()
        top_only_btn.setText("Top 50 Only")
        top_only_btn.setCheckable(True)
        top_only_btn.setChecked(self.show_top_only)
        top_only_btn.clicked.connect(
            lambda: print("[DEBUG] top_only_btn clicked (signal emitted)") or self.on_top_only_toggle_click()
        )
        top_only_btn.setFocusPolicy(Qt.ClickFocus)  # Ensure it can receive focus
        controls_layout.addWidget(top_only_btn)
        self.widgets['top_only_button'] = top_only_btn  # Prevent GC
        print("[DEBUG] Connected top_only_btn clicked signal.")

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # Plot widget
        self.plot_widget = PlotWidget()
        self.plot_widget.setBackground('k')
        self.plot_widget.getPlotItem().setLabel("left", "BO Score")
        layout.addWidget(self.plot_widget)

        # Draw bars initially
        self.update_plot()

        self.widgets['layout_widget'] = layout_widget  # Prevent GC
        return layout_widget

    def update_plot(self):
        print(f"[DEBUG] update_plot called. show_bon1={self.show_bon1}, show_bon2={self.show_bon2}, show_top_only={self.show_top_only}")
        bon1_data, bon2_data = self.vis.get_data()
        print(f"[DEBUG] BOn1={len(bon1_data)}, BOn2={len(bon2_data)}")

        # Clear the plot
        self.plot_widget.clear()
        plot_item = self.plot_widget.getPlotItem()
        
        # Determine how many bars to show
        max_bars = self.max_bars if self.show_top_only else max(len(bon1_data), len(bon2_data))
        
        # Set up the bottom axis
        bottom_axis = plot_item.getAxis('bottom')
        bottom_axis.setLabel("Rank")
        
        # Plot BOn1 bars in red if enabled
        if self.show_bon1 and bon1_data:
            # Limit to max_bars
            limited_bon1_data = bon1_data[:max_bars]
            x_vals = [i + 1 for i in range(len(limited_bon1_data))]
            y_vals = [score for (_, score) in limited_bon1_data]
            bar_item = BarGraphItem(x=x_vals, height=y_vals, width=0.3, brush='r')
            plot_item.addItem(bar_item)

        # Plot BOn2 bars in green if enabled
        if self.show_bon2 and bon2_data:
            # Limit to max_bars
            limited_bon2_data = bon2_data[:max_bars]
            x_vals2 = [i + 1 + 0.4 for i in range(len(limited_bon2_data))]
            y_vals2 = [score for (_, score) in limited_bon2_data]
            bar_item2 = BarGraphItem(x=x_vals2, height=y_vals2, width=0.3, brush='g')
            plot_item.addItem(bar_item2)
        
        # Add word labels if showing top words
        if self.show_top_only:
            # Determine which dataset to use for labels
            label_data = None
            if self.show_bon1 and bon1_data:
                label_data = bon1_data[:max_bars]
            elif self.show_bon2 and bon2_data:
                label_data = bon2_data[:max_bars]
            
            if label_data:
                # Create simple numeric ticks with words
                ticks = []
                for i, (word, _) in enumerate(label_data):
                    # Only show every few labels to avoid overcrowding
                    if max_bars <= 20 or i % 3 == 0:
                        # Truncate long words
                        display_word = word if len(word) <= 8 else word[:6] + '..'
                        ticks.append((i + 1, display_word))
                
                # Apply the ticks to the bottom axis
                bottom_axis.setTicks([ticks])
                
                # Make the labels horizontal but small
                bottom_axis.setStyle(tickFont=pg.QtGui.QFont('Arial', 8))
                bottom_axis.setRotation(0)  # Horizontal text
                
                # Set the x-axis range to show all bars with some padding
                plot_item.setXRange(0.5, max_bars + 0.5)
        else:
            # For "show all" mode, use default numeric ticks
            bottom_axis.setTicks(None)
            
            # Set the x-axis range to show all bars with some padding
            plot_item.setXRange(0.5, max_bars + 0.5)
        
        # Auto-scale y-axis
        plot_item.enableAutoRange(axis='y')

    def on_bon1_toggle_click(self):
        print("[DEBUG] on_bon1_toggle_click called")
        self.show_bon1 = not self.show_bon1
        self.update_plot()
        print(f"[DEBUG] on_bon1_toggle_click -> show_bon1: {self.show_bon1}")

    def on_bon2_toggle_click(self):
        print("[DEBUG] on_bon2_toggle_click called")
        self.show_bon2 = not self.show_bon2
        self.update_plot()
        print(f"[DEBUG] on_bon2_toggle_click -> show_bon2: {self.show_bon2}")
    
    def on_top_only_toggle_click(self):
        print("[DEBUG] on_top_only_toggle_click called")
        self.show_top_only = not self.show_top_only
        self.update_plot()
        print(f"[DEBUG] on_top_only_toggle_click -> show_top_only: {self.show_top_only}")
        
    def refresh_visualization(self):
        """Refresh visualization data from its anchored corpus."""
        print(f"[DEBUG] BOScoreBarLayout.refresh_visualization called")
        if hasattr(self.vis, 'update_data'):
            self.vis.update_data()
            print(f"[DEBUG] Updated BO Score Bar data for corpus: {getattr(self.vis, 'corpus_ids', 'unknown')}")
            self.update_plot()
        else:
            print("[WARNING] BOScoreBarVisualization lacks update_data method")


class BOScoreLineLayout:
    """
    Renders a line graph using pyqtgraph for BOn1 and BOn2 data.
    Includes toggle buttons to show/hide each dataset and scale options.
    """

    def __init__(self, vis):
        self.vis = vis  # Instance of BOScoreBarVisualization
        self.plot_widget = None

        # Toggles for visibility and scaling
        self.show_bon1 = True  # Default to showing BOn1
        self.show_bon2 = False  # Default to hiding BOn2
        self.x_log_scale = False  # Default to linear X-axis
        self.y_log_scale = False  # Default to linear Y-axis

        # Store references to prevent garbage collection
        self.widgets = {}
        print("[DEBUG] BOScoreLineLayout initialized.")

    def generate_layout(self):
        layout_widget = QWidget()
        layout = QVBoxLayout(layout_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # Header layout with title, corpus indicator and refresh button
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title_label = QLabel("BO Score Line Graph")
        title_label.setStyleSheet("color: #fff; font-size:16px;")
        header_layout.addWidget(title_label)
        
        # Add corpus indicator if available
        if hasattr(self.vis, 'corpus_id') and self.vis.corpus_id:
            corpus_label = QLabel(f"Corpus: {self.vis.corpus_id}")
            corpus_label.setStyleSheet("color: #aaa; font-size: 12px;")
            header_layout.addWidget(corpus_label)
            
        header_layout.addStretch()
        
        # Add refresh button
        refresh_btn = QToolButton()
        refresh_btn.setText("⟳")
        refresh_btn.setToolTip("Refresh visualization")
        refresh_btn.setStyleSheet("""
            QToolButton {
                color: #888888;
                border: none;
                font-size: 16px;
                padding: 4px;
            }
            QToolButton:hover {
                color: #ffffff;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_visualization)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)

        # Controls for toggling visibility and scaling
        controls_layout = QHBoxLayout()

        # Toggle BOn1 button
        bon1_btn = QToolButton()
        bon1_btn.setText("Toggle BOn1")
        bon1_btn.setCheckable(True)
        bon1_btn.setChecked(self.show_bon1)
        bon1_btn.clicked.connect(
            lambda: print("[DEBUG] bon1_btn clicked (signal emitted)") or self.on_bon1_toggle_click()
        )
        bon1_btn.setFocusPolicy(Qt.ClickFocus)  # Ensure it can receive focus
        controls_layout.addWidget(bon1_btn)
        self.widgets['bon1_button'] = bon1_btn  # Prevent GC
        print("[DEBUG] Connected bon1_btn clicked signal.")

        # Toggle BOn2 button
        bon2_btn = QToolButton()
        bon2_btn.setText("Toggle BOn2")
        bon2_btn.setCheckable(True)
        bon2_btn.setChecked(self.show_bon2)
        bon2_btn.clicked.connect(
            lambda: print("[DEBUG] bon2_btn clicked (signal emitted)") or self.on_bon2_toggle_click()
        )
        bon2_btn.setFocusPolicy(Qt.ClickFocus)  # Ensure it can receive focus
        controls_layout.addWidget(bon2_btn)
        self.widgets['bon2_button'] = bon2_btn  # Prevent GC
        print("[DEBUG] Connected bon2_btn clicked signal.")

        # Toggle X-axis log scale button
        x_log_btn = QToolButton()
        x_log_btn.setText("X Log Scale")
        x_log_btn.setCheckable(True)
        x_log_btn.setChecked(self.x_log_scale)
        x_log_btn.clicked.connect(
            lambda: print("[DEBUG] x_log_btn clicked (signal emitted)") or self.on_x_log_scale_toggle_click()
        )
        x_log_btn.setFocusPolicy(Qt.ClickFocus)  # Ensure it can receive focus
        controls_layout.addWidget(x_log_btn)
        self.widgets['x_log_button'] = x_log_btn  # Prevent GC
        print("[DEBUG] Connected x_log_btn clicked signal.")

        # Toggle Y-axis log scale button
        y_log_btn = QToolButton()
        y_log_btn.setText("Y Log Scale")
        y_log_btn.setCheckable(True)
        y_log_btn.setChecked(self.y_log_scale)
        y_log_btn.clicked.connect(
            lambda: print("[DEBUG] y_log_btn clicked (signal emitted)") or self.on_y_log_scale_toggle_click()
        )
        y_log_btn.setFocusPolicy(Qt.ClickFocus)  # Ensure it can receive focus
        controls_layout.addWidget(y_log_btn)
        self.widgets['y_log_button'] = y_log_btn  # Prevent GC
        print("[DEBUG] Connected y_log_btn clicked signal.")

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # Plot widget
        self.plot_widget = PlotWidget()
        self.plot_widget.setBackground('k')
        self.plot_widget.getPlotItem().setLabel("bottom", "Rank")
        self.plot_widget.getPlotItem().setLabel("left", "BO Score")
        layout.addWidget(self.plot_widget)

        # Draw lines initially
        self.update_plot()

        self.widgets['layout_widget'] = layout_widget  # Prevent GC
        return layout_widget

    def update_plot(self):
        print(f"[DEBUG] update_plot called. show_bon1={self.show_bon1}, show_bon2={self.show_bon2}, x_log_scale={self.x_log_scale}, y_log_scale={self.y_log_scale}")
        bon1_data, bon2_data = self.vis.get_data()

        self.plot_widget.clear()
        plot_item = self.plot_widget.getPlotItem()

        # Apply log scale if enabled
        plot_item.setLogMode(x=self.x_log_scale, y=self.y_log_scale)

        # Plot BOn1 curve in red if enabled
        if self.show_bon1 and bon1_data:
            x_vals = [i + 1 for i in range(len(bon1_data))]
            y_vals = [score for (_, score) in bon1_data]
            plot_item.plot(x_vals, y_vals, pen='r', name="BOn1")

        # Plot BOn2 curve in green if enabled
        if self.show_bon2 and bon2_data:
            x_vals2 = [i + 1 for i in range(len(bon2_data))]
            y_vals2 = [score for (_, score) in bon2_data]
            plot_item.plot(x_vals2, y_vals2, pen='g', name="BOn2")

    def on_bon1_toggle_click(self):
        print("[DEBUG] on_bon1_toggle_click called")
        self.show_bon1 = not self.show_bon1
        self.update_plot()
        print(f"[DEBUG] on_bon1_toggle_click -> show_bon1: {self.show_bon1}")

    def on_bon2_toggle_click(self):
        print("[DEBUG] on_bon2_toggle_click called")
        self.show_bon2 = not self.show_bon2
        self.update_plot()
        print(f"[DEBUG] on_bon2_toggle_click -> show_bon2: {self.show_bon2}")

    def on_x_log_scale_toggle_click(self):
        print("[DEBUG] on_x_log_scale_toggle_click called")
        self.x_log_scale = not self.x_log_scale
        self.update_plot()
        print(f"[DEBUG] on_x_log_scale_toggle_click -> x_log_scale: {self.x_log_scale}")

    def on_y_log_scale_toggle_click(self):
        print("[DEBUG] on_y_log_scale_toggle_click called")
        self.y_log_scale = not self.y_log_scale
        self.update_plot()
        print(f"[DEBUG] on_y_log_scale_toggle_click -> y_log_scale: {self.y_log_scale}")
        
    def refresh_visualization(self):
        """Refresh visualization data from its anchored corpus."""
        print(f"[DEBUG] BOScoreLineLayout.refresh_visualization called")
        if hasattr(self.vis, 'update_data'):
            self.vis.update_data()
            print(f"[DEBUG] Updated BO Score Line data for corpus: {getattr(self.vis, 'corpus_id', 'unknown')}")
            self.update_plot()
        else:
            print("[WARNING] BOScoreLineVisualization lacks update_data method")


class BOScoreTableLayout:
    """
    Renders BOn1 and BOn2 scores in a table format with sortable columns.
    """
    
    def __init__(self, vis):
        self.vis = vis  # Instance of BOScoreTableVisualization
        self.plot_widget = None
        
        print("[DEBUG] BOScoreTableLayout initialized.")
        
    def generate_layout(self):
        """Generate the table layout for BOScore visualization."""
        container = QWidget()
        
        # Set dark background
        container.setStyleSheet("background-color: #2b2b2b; color: white;")
        
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(5)
        
        # Create title label
        self.title_label = QLabel("BO Score Table")
        self.title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.title_label)
        
        # Create corpus indicator
        corpus_text = ""
        if hasattr(self.vis, 'corpus_ids') and self.vis.corpus_ids:
            if len(self.vis.corpus_ids) == 1:
                corpus_text = f"Corpus: {self.vis.corpus_ids[0]}"
            else:
                corpus_text = f"Corpora: {len(self.vis.corpus_ids)} selected"
        corpus_layout = QHBoxLayout()
        corpus_layout.setContentsMargins(0, 0, 0, 0)
        corpus_layout.addStretch(1)
        self.corpus_label = QLabel(corpus_text)
        self.corpus_label.setStyleSheet("color: #aaa; font-size: 12px;")
        corpus_layout.addWidget(self.corpus_label)
        
        # Create the table
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels([
            "Rank", "Word", "BOn1", "BOn2"
        ])
        
        # Apply standardized table styling
        apply_standard_table_styling(self.table_widget)
        
        # Fill the table with data
        self.fill_table()
        
        # Add the table to the layout
        main_layout.addWidget(self.table_widget)
        main_layout.addLayout(corpus_layout)
        
        # Add refresh button
        refresh_button = QPushButton("Refresh")
        refresh_button.setStyleSheet("background-color: #444; color: white; border: none; padding: 4px 8px;")
        refresh_button.clicked.connect(self.refresh_visualization)
        refresh_layout = QHBoxLayout()
        refresh_layout.addStretch(1)
        refresh_layout.addWidget(refresh_button)
        refresh_layout.addStretch(1)
        main_layout.addLayout(refresh_layout)
        
        return container
        
    def fill_table(self):
        """Fill the table with BOScore data."""
        # Get data from the visualization
        bon1_data, bon2_data = self.vis.get_data()
        
        # Prepare combined data for display
        combined_data = {}
        
        # Merge BOn1 and BOn2 data
        for word, score in bon1_data:
            if word not in combined_data:
                combined_data[word] = {"bon1": score, "bon2": 0}
            else:
                combined_data[word]["bon1"] = score
                
        for word, score in bon2_data:
            if word not in combined_data:
                combined_data[word] = {"bon1": 0, "bon2": score}
            else:
                combined_data[word]["bon2"] = score
        
        # Convert to a sortable list (sort by BOn1 score descending)
        table_data = [(word, data["bon1"], data["bon2"]) 
                      for word, data in combined_data.items()]
        table_data.sort(key=lambda x: x[1], reverse=True)
        
        # Set table row count
        self.table_widget.setRowCount(len(table_data))
        
        # Block signals during updates to improve performance
        self.table_widget.blockSignals(True)
        
        # Fill the table
        for row, (word, bon1, bon2) in enumerate(table_data):
            # Rank column
            rank_item = QTableWidgetItem(str(row + 1))
            rank_item.setTextAlignment(Qt.AlignCenter)
            self.table_widget.setItem(row, 0, rank_item)
            
            # Word column - left align text for better readability
            word_item = QTableWidgetItem(word)
            self.table_widget.setItem(row, 1, word_item)
            
            # BOn1 column - center align all numeric values
            bon1_item = QTableWidgetItem(f"{bon1:.2f}")
            bon1_item.setTextAlignment(Qt.AlignCenter)
            self.table_widget.setItem(row, 2, bon1_item)
            
            # BOn2 column - center align all numeric values
            bon2_item = QTableWidgetItem(f"{bon2:.2f}")
            bon2_item.setTextAlignment(Qt.AlignCenter)
            self.table_widget.setItem(row, 3, bon2_item)
        
        # Enable signals again
        self.table_widget.blockSignals(False)
    
    def refresh_visualization(self):
        """Refresh the visualization with new data."""
        # Have the visualization update its data
        if hasattr(self.vis, 'update_data'):
            self.vis.update_data()
        
        # Update corpus name in UI
        corpus_text = ""
        if hasattr(self.vis, 'corpus_ids') and self.vis.corpus_ids:
            if len(self.vis.corpus_ids) == 1:
                corpus_text = f"Corpus: {self.vis.corpus_ids[0]}"
            else:
                corpus_text = f"Corpora: {len(self.vis.corpus_ids)} selected"
        self.corpus_label.setText(corpus_text)
            
        # Refill the table
        self.fill_table()


class CorpusSelector(QDialog):
    corpus_changed = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Corpora")
        self.setMinimumWidth(300)
        
        # UI Components
        layout = QVBoxLayout()
        
        # Instructions label
        instructions = QLabel("Select corpora to display in visualization:")
        instructions.setStyleSheet("font-weight: bold;")
        layout.addWidget(instructions)
        
        # Corpus checkboxes container (scrollable)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.checkbox_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.select_all_btn = QPushButton("Select All")
        self.clear_all_btn = QPushButton("Clear All")
        self.apply_btn = QPushButton("Apply")
        self.apply_btn.setDefault(True)
        
        button_layout.addWidget(self.select_all_btn)
        button_layout.addWidget(self.clear_all_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.apply_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Connections
        self.select_all_btn.clicked.connect(self.select_all_corpora)
        self.clear_all_btn.clicked.connect(self.clear_all_corpora)
        self.apply_btn.clicked.connect(self.apply_selection)
        
        # Store checkboxes
        self.corpus_checkboxes = []

    def open_selector(self, available_corpora, current_selection=None):
        """
        Open the corpus selector dialog with the given available corpora.
        
        Args:
            available_corpora: List of corpus names
            current_selection: List of currently selected corpus names
        """
        if not available_corpora:
            print("[WARNING] No corpora available to select")
            return
            
        # Clear existing checkboxes
        self.corpus_checkboxes.clear()
        
        # Remove existing widgets from layout
        while self.checkbox_layout.count():
            item = self.checkbox_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Create checkboxes for each corpus
        for corpus_name in available_corpora:
            checkbox = QCheckBox(corpus_name)
            
            # Check if this corpus is currently selected
            if current_selection and corpus_name in current_selection:
                checkbox.setChecked(True)
                
            self.checkbox_layout.addWidget(checkbox)
            self.corpus_checkboxes.append(checkbox)
            
        # Add a stretch at the end
        self.checkbox_layout.addStretch()
        
        # Show the dialog
        self.exec_()
        
    def select_all_corpora(self):
        """Select all corpora in the list."""
        for checkbox in self.corpus_checkboxes:
            checkbox.setChecked(True)
            
    def clear_all_corpora(self):
        """Clear all selections."""
        for checkbox in self.corpus_checkboxes:
            checkbox.setChecked(False)

    def apply_selection(self):
        """Apply the current selection and close the dialog."""
        selected_corpora = [
            checkbox.text() for checkbox in self.corpus_checkboxes 
            if checkbox.isChecked()
        ]
        
        # Emit signal with selected corpora
        self.corpus_changed.emit(selected_corpora)
        self.accept()

    def get_selected_corpora(self):
        """Return the list of selected corpora."""
        return [
            checkbox.text() for checkbox in self.corpus_checkboxes 
            if checkbox.isChecked()
        ]

