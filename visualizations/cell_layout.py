# cell_layout.py
from visualizations.metric_visualizations import FrequencyReportsAggregator
import os
import math
import pyqtgraph as pg
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
                            QHBoxLayout, QPushButton, QHeaderView, QComboBox, QToolButton
                            )
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QBrush, QPalette
from pyqtgraph import PlotWidget, BarGraphItem, mkPen
import numpy as np


class BaseMetricLayout:
    def __init__(self, vis):
        self.vis = vis
        self.layout_widget = None

    def generate_layout(self):
        """Generate the base layout with refresh functionality."""
        self.layout_widget = QWidget()
        layout = QVBoxLayout(self.layout_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # Header with title and refresh button
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel(self.get_title())
        title_label.setStyleSheet("color: #fff; font-size: 14px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        # Add corpus indicator if available
        if hasattr(self.vis, 'corpus_id') and self.vis.corpus_id:
            corpus_label = QLabel(f"Corpus: {self.vis.corpus_id}")
            corpus_label.setStyleSheet("color: #aaa; font-size: 12px;")
            header_layout.addWidget(corpus_label)
        
        header_layout.addStretch()
        
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
        
        # Create header with report title
        self.title_label = QLabel("Frequency Reports")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: white; margin-bottom: 2px;")
        main_layout.addWidget(self.title_label)
        
        # Create navigation with corpus indicator (like BO table has)
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(0, 0, 0, 0)
        
        self.prev_button = QPushButton("← Previous")
        self.prev_button.setStyleSheet("background-color: #444; color: white; border: none; padding: 4px 8px;")
        self.prev_button.clicked.connect(self.show_previous_report)
        
        self.report_label = QLabel("Report: 1 of 1")
        self.report_label.setAlignment(Qt.AlignCenter)
        self.report_label.setStyleSheet("color: #aaa; font-size: 12px;")
        
        self.next_button = QPushButton("Next →")
        self.next_button.setStyleSheet("background-color: #444; color: white; border: none; padding: 4px 8px;")
        self.next_button.clicked.connect(self.show_next_report)
        
        # Like BO Score Table, add corpus indicator
        self.corpus_label = QLabel(f"Corpus: {corpus_id}")
        self.corpus_label.setStyleSheet("color: #aaa; font-size: 12px;")
        self.corpus_label.setAlignment(Qt.AlignRight)
        
        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.report_label, 1)
        nav_layout.addWidget(self.next_button)
        nav_layout.addWidget(self.corpus_label)
        
        main_layout.addLayout(nav_layout)
        
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
        
        # Style the table like BO Score Table
        self.table_widget.setStyleSheet("""
            QTableWidget {
                background-color: #2b2b2b;
                color: white;
                gridline-color: #444;
                border: none;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QTableWidget::item:selected {
                background-color: #3d3d3d;
            }
            QHeaderView::section {
                background-color: #444;
                color: white;
                padding: 4px;
                border: 1px solid #555;
            }
            QTableCornerButton::section {
                background-color: #444;
                border: 1px solid #555;
            }
        """)
        
        # Configure table behavior
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)  # Read-only
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Equal columns
        self.table_widget.verticalHeader().setVisible(False)  # Hide row numbers
        self.table_widget.setSortingEnabled(False)  # Disable sorting for now
        
        main_layout.addWidget(self.table_widget)
        
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
            
            # Update the table
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
                
                # Add word
                word_item = QTableWidgetItem(word)
                self.table_widget.setItem(row, 1, word_item)
                
                # Add count
                count_item = QTableWidgetItem(str(count))
                count_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table_widget.setItem(row, 2, count_item)
                
                # Add percentage (format to 2 decimal places)
                percentage_item = QTableWidgetItem(f"{percentage:.2f}")
                percentage_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table_widget.setItem(row, 3, percentage_item)
                
                # Add z-score (format to 2 decimal places)
                z_score_item = QTableWidgetItem(f"{z_score:.2f}")
                z_score_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table_widget.setItem(row, 4, z_score_item)
                
                # Add log z-score
                log_z_item = QTableWidgetItem(f"{log_z_score:.2f}")
                log_z_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table_widget.setItem(row, 5, log_z_item)
                
                # Apply alternating row colors
                for col in range(6):
                    item = self.table_widget.item(row, col)
                    if item:
                        # Make read-only
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                        # Apply background color based on row
                        if row % 2:
                            item.setBackground(QColor(60, 60, 60))  # Dark gray for even rows
                        else:
                            item.setBackground(QColor(45, 45, 45))  # Darker gray for odd rows
            
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
    Includes toggle buttons to show/hide each dataset.
    """

    def __init__(self, vis):
        self.vis = vis  # Instance of BOScoreBarVisualization
        self.plot_widget = None

        # Toggles for visibility
        self.show_bon1 = True  # Default to showing BOn1
        self.show_bon2 = False  # Default to hiding BOn2

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

        # Controls for toggling visibility
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

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # Plot widget
        self.plot_widget = PlotWidget()
        self.plot_widget.setBackground('k')
        self.plot_widget.getPlotItem().setLabel("bottom", "Rank")
        self.plot_widget.getPlotItem().setLabel("left", "BO Score")
        layout.addWidget(self.plot_widget)

        # Draw bars initially
        self.update_plot()

        self.widgets['layout_widget'] = layout_widget  # Prevent GC
        return layout_widget

    def update_plot(self):
        print(f"[DEBUG] update_plot called. show_bon1={self.show_bon1}, show_bon2={self.show_bon2}")
        bon1_data, bon2_data = self.vis.get_data()
        print(f"[DEBUG] BOn1={len(bon1_data)}, BOn2={len(bon2_data)}")

        self.plot_widget.clear()
        plot_item = self.plot_widget.getPlotItem()

        # Plot BOn1 bars in red if enabled
        if self.show_bon1 and bon1_data:
            x_vals = [i + 1 for i in range(len(bon1_data))]
            y_vals = [score for (_, score) in bon1_data]
            bar_item = BarGraphItem(x=x_vals, height=y_vals, width=0.3, brush='r')
            plot_item.addItem(bar_item)

        # Plot BOn2 bars in green if enabled
        if self.show_bon2 and bon2_data:
            x_vals2 = [i + 1 + 0.4 for i in range(len(bon2_data))]
            y_vals2 = [score for (_, score) in bon2_data]
            bar_item2 = BarGraphItem(x=x_vals2, height=y_vals2, width=0.3, brush='g')
            plot_item.addItem(bar_item2)

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
        
    def refresh_visualization(self):
        """Refresh visualization data from its anchored corpus."""
        print(f"[DEBUG] BOScoreBarLayout.refresh_visualization called")
        if hasattr(self.vis, 'update_data'):
            self.vis.update_data()
            print(f"[DEBUG] Updated BO Score Bar data for corpus: {getattr(self.vis, 'corpus_id', 'unknown')}")
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
    Renders a QTableWidget showing each word + BOn1 score + BOn2 score.
    Optionally, you can hide BOn2 or combine columns—your choice.
    """
    def __init__(self, vis):
        self.vis = vis  # Instance of BOScoreTableVisualization
        self.table_widget = None

    def generate_layout(self):
        layout_widget = QWidget()
        layout = QVBoxLayout(layout_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # Header layout with title, corpus indicator and refresh button
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title_label = QLabel("BO Score Table")
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

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["Rank", "Word", "BOn1", "BOn2"])

        # Apply dark theme for headers
        header_style = """
            QHeaderView::section {
                background-color: #444; 
                color: white; 
                font-size: 14px; 
                font-weight: bold; 
                border: 1px solid #555;
            }
        """
        self.table_widget.setStyleSheet(header_style)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.verticalHeader().setVisible(False)
        layout.addWidget(self.table_widget)

        # Fill it from vis data
        self.fill_table()

        return layout_widget

    def fill_table(self):
        bon1_data, bon2_data = self.vis.get_data()
        if not bon1_data and not bon2_data:
            self.table_widget.setRowCount(0)  # Clear table if no data
            return

        # Convert lists -> dict for quick lookup
        bon1_dict = {w: s for (w, s) in bon1_data}
        bon2_dict = {w: s for (w, s) in bon2_data}

        # Union of all words, sorted by combined score
        all_words = sorted(set(bon1_dict.keys()) | set(bon2_dict.keys()),
                           key=lambda w: bon1_dict.get(w, 0) + bon2_dict.get(w, 0),
                           reverse=True)

        self.table_widget.setRowCount(len(all_words))

        for i, word in enumerate(all_words):
            rank = i + 1
            b1 = bon1_dict.get(word, 0.0)
            b2 = bon2_dict.get(word, 0.0)
            formatted_b1 = f"{b1:,.2f}"  # Comma-separated, 2 decimals
            formatted_b2 = f"{b2:,.2f}"  # Comma-separated, 2 decimals

            # Fill table
            self.table_widget.setItem(i, 0, QTableWidgetItem(str(rank)))
            self.table_widget.setItem(i, 1, QTableWidgetItem(word))
            self.table_widget.setItem(i, 2, QTableWidgetItem(formatted_b1))
            self.table_widget.setItem(i, 3, QTableWidgetItem(formatted_b2))

            # Style cells for alignment and alternating row colors
            for j in range(self.table_widget.columnCount()):
                item = self.table_widget.item(i, j)
                if item:
                    item.setTextAlignment(Qt.AlignCenter)
                    if i % 2 == 0:
                        item.setBackground(QColor("#333"))  # Darker background for even rows
                    else:
                        item.setBackground(QColor("#222"))  # Slightly lighter background for odd rows
                        
    def refresh_visualization(self):
        """Refresh visualization data from its anchored corpus."""
        print(f"[DEBUG] BOScoreTableLayout.refresh_visualization called")
        if hasattr(self.vis, 'update_data'):
            self.vis.update_data()
            print(f"[DEBUG] Updated BO Score Table data for corpus: {getattr(self.vis, 'corpus_id', 'unknown')}")
            self.fill_table()
        else:
            print("[WARNING] BOScoreTableVisualization lacks update_data method")

