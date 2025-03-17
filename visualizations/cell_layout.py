# cell_layout.py
from visualizations.metric_visualizations import FrequencyReportsAggregator
import os
import math
import pyqtgraph as pg
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
                            QHBoxLayout, QPushButton, QHeaderView, QComboBox, QToolButton, QDialog, QListWidget, QListWidgetItem, QScrollArea, QCheckBox, QFrame, QSizePolicy, QApplication
                            )
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QPropertyAnimation, QPoint, QRect
from PyQt5.QtGui import QColor, QBrush, QPalette, QIcon
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
        self.corpus_label = None
        self.settings_sidebar = None
        self.sidebar_button = None
        # Create content container once here
        self.content_container = QWidget()

    def generate_layout(self):
        """Create the main layout with header, content area, and sidebar container."""
        self.layout_widget = QWidget()
        
        # Main layout for entire widget
        main_layout = QHBoxLayout(self.layout_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create the sidebar toggle button
        self.sidebar_button = QToolButton()
        self.sidebar_button.setText("◀")
        self.sidebar_button.setToolTip("Open multi-corpus settings menu")
        self.sidebar_button.setFixedWidth(20)
        self.sidebar_button.setStyleSheet("""
            QToolButton {
                color: #888888;
                border: none;
                border-right: 1px solid #444;
                background-color: #333333;
                font-size: 14px;
                padding: 4px 0px;
                margin: 0px;
            }
            QToolButton:hover {
                color: #ffffff;
                background-color: #444444;
            }
        """)
        self.sidebar_button.clicked.connect(self.toggle_settings_sidebar)
        main_layout.addWidget(self.sidebar_button)
        
        # Create a container for sidebar and content with horizontal layout
        self.sidebar_container = QWidget()
        container_layout = QHBoxLayout(self.sidebar_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # Add the content container to the container layout
        # (the sidebar will be inserted at index 0 when needed)
        content_layout = QVBoxLayout(self.content_container)
        content_layout.setContentsMargins(5, 5, 5, 5)
        content_layout.setSpacing(10)
        container_layout.addWidget(self.content_container)
        
        # Add the sidebar if it exists
        if self.settings_sidebar:
            container_layout.insertWidget(0, self.settings_sidebar)
        
        # Add the container to the main layout
        main_layout.addWidget(self.sidebar_container)
        
        # Create header layout
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add title
        title_label = QLabel(self.get_title())
        title_label.setStyleSheet("color: #fff; font-size: 14px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        # Add corpus info
        if hasattr(self.vis, 'corpus_ids') and self.vis.corpus_ids:
            if len(self.vis.corpus_ids) == 1:
                corpus_text = f"Corpus: {self.vis.corpus_ids[0]}"
            else:
                corpus_text = f"Corpora: {len(self.vis.corpus_ids)} selected"
        elif hasattr(self.vis, 'corpus_id') and self.vis.corpus_id:
            corpus_text = f"Corpus: {self.vis.corpus_id}"
        else:
            corpus_text = "No corpus selected"
        self.corpus_label = QLabel(corpus_text)
        self.corpus_label.setStyleSheet("color: #aaa; font-size: 12px;")
        header_layout.addWidget(self.corpus_label)
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
        
        # Add corpus selector button
        manage_btn = QToolButton()
        manage_btn.setText("Select Corpora")
        manage_btn.setToolTip("Select which corpora to display in this visualization")
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
        
        # Add header to content layout
        content_layout.addLayout(header_layout)
        
        # Add custom content from subclasses
        self.add_content(content_layout)
        
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

    def toggle_settings_sidebar(self):
        """Toggle the settings sidebar visibility."""
        # Only create the sidebar once
        if not self.settings_sidebar:
            # Create the sidebar with the sidebar_container as parent for proper positioning
            self.settings_sidebar = SettingsSidebar(self.vis, self.sidebar_container)
            
            # Add the sidebar to the beginning of the container layout
            if self.sidebar_container and self.sidebar_container.layout():
                self.sidebar_container.layout().insertWidget(0, self.settings_sidebar)
                print(f"[DEBUG] Created and added settings sidebar to container: {self.sidebar_container}")
            else:
                print("[WARNING] Could not find sidebar_container to add sidebar to")
        
        # Get plot settings and current visibility settings
        plot_items = self.get_available_plot_settings()
        current_settings = getattr(self.vis, 'visibility_settings', {})
        
        # Check if we have any plot items to display
        if not plot_items:
            print("[WARNING] No plot settings available to display")
            return
        
        # Toggle sidebar and update button state
        if self.settings_sidebar.is_visible and not self.settings_sidebar.is_animating:
            # If sidebar is visible and not in the middle of animating, close it
            self.settings_sidebar.close_sidebar()
            self.sidebar_button.setText("◀")
            self.sidebar_button.setToolTip("Open settings menu")
        elif not self.settings_sidebar.is_visible and not self.settings_sidebar.is_animating:
            # If sidebar is hidden and not animating, show it
            self.settings_sidebar.show_settings(self.vis, plot_items, current_settings)
            self.sidebar_button.setText("▶")
            self.sidebar_button.setToolTip("Close settings menu")
        else:
            # If sidebar is in the middle of an animation, don't do anything
            print("[DEBUG] Sidebar is currently animating, ignoring toggle request")

    def on_settings_changed(self, settings):
        if hasattr(self.vis, 'set_visibility_settings'):
            self.vis.set_visibility_settings(settings)
        self.refresh_visualization()

    def get_available_plot_settings(self):
        return []


class FrequencyDistributionLayout(BaseMetricLayout):
    def get_title(self):
        return "Frequency Distribution"
    
    def add_content(self, layout):
        # Access the visualization
        freqdist_viz = self.vis
        
        # Create controls panel
        controls_layout = QHBoxLayout()
        
        # Add mode selection
        mode_label = QLabel("Mode:")
        mode_label.setStyleSheet("color: white;")
        
        mode_combo = QComboBox()
        mode_combo.addItems(["Nominal", "Percentage", "Z-Score"])
        mode_combo.setStyleSheet("""
            QComboBox {
                background-color: #333; 
                color: white; 
                border: 1px solid #555;
                padding: 2px;
                border-radius: 2px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 10px;
                height: 10px;
            }
        """)
        
        # Set initial mode
        if freqdist_viz.current_mode == 'percentage':
            mode_combo.setCurrentIndex(1)
        elif freqdist_viz.current_mode == 'z_score':
            mode_combo.setCurrentIndex(2)
        else:  # nominal
            mode_combo.setCurrentIndex(0)
            
        # Add toggle for log scales
        x_log_btn = QCheckBox("Log X")
        x_log_btn.setStyleSheet("color: white;")
        x_log_btn.setChecked(freqdist_viz.x_log)
        
        y_log_btn = QCheckBox("Log Y")
        y_log_btn.setStyleSheet("color: white;")
        y_log_btn.setChecked(freqdist_viz.y_log)
        
        # Add all controls to layout
        controls_layout.addWidget(mode_label)
        controls_layout.addWidget(mode_combo)
        controls_layout.addStretch()
        controls_layout.addWidget(x_log_btn)
        controls_layout.addWidget(y_log_btn)
        
        # Connect the signals
        mode_combo.currentIndexChanged.connect(lambda idx: self.set_mode(idx))
        x_log_btn.toggled.connect(freqdist_viz.set_x_log)
        y_log_btn.toggled.connect(freqdist_viz.set_y_log)
        
        # Connect visibility_updated signal if available
        if hasattr(freqdist_viz, 'visibility_updated'):
            freqdist_viz.visibility_updated.connect(freqdist_viz.set_visibility_settings)
        
        # Add the plot widget
        plot_widget = freqdist_viz.widget()
        
        # Add the controls and plot to the layout
        layout.addLayout(controls_layout)
        layout.addWidget(plot_widget)
    
    def set_mode(self, index):
        """Convert combo box index to mode string and update visualization"""
        mode_map = {0: 'nominal', 1: 'percentage', 2: 'z_score'}
        if index in mode_map:
            self.vis.set_mode(mode_map[index])
    
    def refresh_visualization(self):
        """Force refresh the visualization from latest data"""
        # Update data source first
        if hasattr(self.vis, 'update_data_source'):
            self.vis.update_data_source()
        
        # Then update the plot
        if hasattr(self.vis, 'update_plot'):
            self.vis.update_plot()
            
    def get_available_plot_settings(self):
        """Get available plot settings from visualization"""
        if hasattr(self.vis, 'get_available_plot_settings'):
            items = self.vis.get_available_plot_settings()
            print(f"[DEBUG] Got {len(items)} plot settings from visualization")
            return items
        return []


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

        # Store data for dynamic labels
        self.current_label_data = None
        self.current_max_bars = 0
        self.current_view_range = (0, 50)  # Default view range

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
        
        # Connect to the view range changed signal to update labels on zoom
        view_box = self.plot_widget.getPlotItem().getViewBox()
        view_box.sigRangeChanged.connect(self.on_view_range_changed)
        
        layout.addWidget(self.plot_widget)

        # Add a hint about zooming
        zoom_hint = QLabel("Tip: Zoom in to see more word labels")
        zoom_hint.setStyleSheet("color: #888; font-size: 10px; font-style: italic;")
        zoom_hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(zoom_hint)

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
        self.current_max_bars = max_bars
        
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
        
        # Store label data for dynamic updates - ALWAYS STORE LABEL DATA
        # Determine which dataset to use for labels
        if self.show_bon1 and bon1_data:
            self.current_label_data = bon1_data[:max_bars]
        elif self.show_bon2 and bon2_data:
            self.current_label_data = bon2_data[:max_bars]
        else:
            self.current_label_data = None
            
        # Set the x-axis range to show all bars with some padding
        plot_item.setXRange(0.5, max_bars + 0.5)
        
        # Update labels based on current view
        self.update_labels()
        
        # Auto-scale y-axis
        plot_item.enableAutoRange(axis='y')

    def update_labels(self):
        """Update the word labels based on the current view range."""
        if not self.current_label_data:
            # No labels if no data
            bottom_axis = self.plot_widget.getPlotItem().getAxis('bottom')
            bottom_axis.setTicks(None)  # Use default numeric ticks
            return
            
        # Get the current view range
        view_box = self.plot_widget.getPlotItem().getViewBox()
        view_range = view_box.viewRange()
        x_min, x_max = view_range[0]
        self.current_view_range = (x_min, x_max)
        
        # Calculate visible range
        visible_width = x_max - x_min
        
        # Determine label density based on zoom level and mode
        # More zoomed in = more labels
        # In "All Bars" mode, be more conservative with labels to avoid overcrowding
        if self.show_top_only:
            # Top 50 mode - more aggressive labeling
            if visible_width <= 25:
                step = 1  # Show every label
            elif visible_width <= 35:
                step = 2  # Show every other label
            elif visible_width <= 45:
                step = 3  # Show every third label
            else:
                step = 4  # Show every fourth label
        else:
            # All bars mode - more conservative labeling
            if visible_width <= 15:
                step = 1  # Show every label
            elif visible_width <= 30:
                step = 2  # Show every other label
            elif visible_width <= 60:
                step = 5  # Show every fifth label
            elif visible_width <= 100:
                step = 10  # Show every tenth label
            else:
                step = 20  # Show every twentieth label
            
        print(f"[DEBUG] View range: {x_min:.1f} to {x_max:.1f}, width: {visible_width:.1f}, step: {step}")
        
        # Create ticks for visible range
        ticks = []
        for i, (word, _) in enumerate(self.current_label_data):
            pos = i + 1  # Position is 1-based
            
            # Only include if in visible range and matches step
            if x_min - 1 <= pos <= x_max + 1 and (i % step == 0):
                # Truncate long words
                display_word = word if len(word) <= 8 else word[:6] + '..'
                ticks.append((pos, display_word))
        
        # Apply the ticks to the bottom axis
        bottom_axis = self.plot_widget.getPlotItem().getAxis('bottom')
        bottom_axis.setTicks([ticks])
        
        # Make the labels horizontal but small
        bottom_axis.setStyle(tickFont=pg.QtGui.QFont('Arial', 8))
        bottom_axis.setRotation(0)  # Horizontal text

    def on_view_range_changed(self, view_box, range_data):
        """Called when the user zooms or pans the plot."""
        x_min, x_max = range_data[0]
        
        # Only update if the range has changed significantly
        old_min, old_max = self.current_view_range
        if abs(x_min - old_min) > 0.1 or abs(x_max - old_max) > 0.1:
            print(f"[DEBUG] View range changed: {x_min:.1f} to {x_max:.1f}")
            self.update_labels()

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

class SettingsSidebar(QWidget):
    def __init__(self, target, parent=None):
        super().__init__(parent)
        self.target = target
        self.setFixedWidth(250)  # Slightly wider for better presentation
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b; 
                color: white;
                border: 1px solid #444;
                border-radius: 3px;
            }
            QLabel {
                border: none;
            }
            QPushButton {
                background-color: #444;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 2px;
            }
            QPushButton:hover {
                background-color: #555;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:horizontal {
                height: 0px;  /* Hide horizontal scrollbar */
            }
        """)
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        
        # Add title
        title_label = QLabel("Plot Settings")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: white;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #444;")
        main_layout.addWidget(separator)
        
        # Create scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background-color: transparent;")
        main_layout.addWidget(scroll, 1)  # 1 = stretch factor
        
        # Create container widget for scroll area
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background-color: transparent; border: none;")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(10)
        self.content_layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(self.content_widget)
        
        # Add close button
        self.close_btn = QPushButton("Close")
        self.close_btn.setCursor(Qt.PointingHandCursor)  # Show hand cursor on hover
        main_layout.addWidget(self.close_btn)
        
        # Connect the close button
        self.close_btn.clicked.connect(self.close_sidebar)
        
        # Set initial state
        self.is_visible = False
        self.is_animating = False  # Track animation state to prevent overlapping animations
        
        # For organized corpus data
        self.corpus_sections = {}  # Store sections by corpus
        self.color_buttons = {}    # Store color buttons by corpus
        
        # Make sure we're hidden initially
        self.hide()
        print("[DEBUG] SettingsSidebar initialized with parent:", parent)

    def show_settings(self, target, plot_items=None, current_settings=None):
        """Show the sidebar with organized plot items and settings."""
        print(f"[DEBUG] show_settings called, is_visible: {self.is_visible}, is_animating: {self.is_animating}")
        
        # If already animating, don't start another animation
        if self.is_animating:
            print("[DEBUG] Animation already in progress, ignoring show_settings call")
            return
            
        # If already visible, just close it
        if self.is_visible:
            self.close_sidebar()
            return
            
        # Update target reference
        self.target = target
        
        # Default values
        if plot_items is None:
            plot_items = []
        if current_settings is None:
            current_settings = {}
            
        # Clear the content layout
        self._clear_content()
        
        # Organize items by corpus
        corpus_groups = self._group_items_by_corpus(plot_items)
        
        # Add sections for each corpus
        for corpus_name, items in corpus_groups.items():
            # Create a section for this corpus
            self._add_corpus_section(corpus_name, items, current_settings)
        
        # Make sure we're visible and positioned correctly before animation
        self.raise_()  # Bring to front
        self.move(-self.width(), 0)  # Start position off-screen
        self.show()
        
        # Create a fresh animation for opening
        self.open_animation = QPropertyAnimation(self, b"pos")
        self.open_animation.setDuration(200)
        self.open_animation.setStartValue(self.pos())
        self.open_animation.setEndValue(QPoint(0, 0))
        
        # Connect signals
        self.open_animation.finished.connect(self._on_open_finished)
        self.is_animating = True
        
        # Start animation
        self.open_animation.start()
        print("[DEBUG] Sidebar open animation started")
    
    def _on_open_finished(self):
        """Handle completion of open animation."""
        self.is_animating = False
        self.is_visible = True
        print("[DEBUG] Sidebar open animation finished")
    
    def _on_close_finished(self):
        """Handle completion of close animation."""
        self.hide()
        self.is_animating = False
        self.is_visible = False
        print("[DEBUG] Sidebar close animation finished")
    
    def _clear_content(self):
        """Clear all widgets from the content layout."""
        # Remove all widgets from content layout
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Reset tracking dictionaries
        self.corpus_sections = {}
        self.color_buttons = {}
    
    def _group_items_by_corpus(self, plot_items):
        """Group plot items by their corpus."""
        corpus_groups = {}
        
        for item in plot_items:
            # Check if this is a corpus item or a derived item
            if " (Average)" in item or " (Best Fit)" in item or " (Band)" in item:
                # Extract corpus name from derived item
                corpus_name = item.split(" (")[0]
                item_type = item.split(" (")[1].rstrip(")")
            else:
                # Regular corpus item (could be "corpus: filename")
                if ":" in item:
                    corpus_name = item.split(":")[0]
                else:
                    corpus_name = item
                item_type = "File"  # Regular file item
            
            # Create the corpus group if it doesn't exist
            if corpus_name not in corpus_groups:
                corpus_groups[corpus_name] = []
            
            # Add the item to its group
            corpus_groups[corpus_name].append((item, item_type))
        
        return corpus_groups
    
    def _add_corpus_section(self, corpus_name, items, current_settings):
        """Add a collapsible section for a corpus with its items."""
        # Create frame for this corpus section
        section_frame = QFrame()
        section_frame.setFrameShape(QFrame.StyledPanel)
        section_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #555;
                border-radius: 4px;
                background-color: #333;
            }
        """)
        section_layout = QVBoxLayout(section_frame)
        section_layout.setContentsMargins(8, 8, 8, 8)
        section_layout.setSpacing(4)
        
        # Create header with corpus name and color selector
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Toggle button
        toggle_btn = QPushButton("▼")  # Down arrow for expand
        toggle_btn.setFixedWidth(20)
        toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-weight: bold;
            }
        """)
        
        # Corpus label
        corpus_label = QLabel(corpus_name)
        corpus_label.setStyleSheet("font-weight: bold; color: white;")
        
        # Color button
        color_btn = QPushButton()
        color_btn.setFixedSize(16, 16)
        color_btn.setCursor(Qt.PointingHandCursor)
        color_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #6699ff;  /* Default blue */
                border: 1px solid #888;
                border-radius: 8px;
            }}
        """)
        color_btn.setToolTip("Change color for this corpus")
        
        # Store color button for later access
        self.color_buttons[corpus_name] = color_btn
        
        # Add widgets to header
        header_layout.addWidget(toggle_btn)
        header_layout.addWidget(corpus_label)
        header_layout.addStretch()
        header_layout.addWidget(color_btn)
        
        # Add header to section
        section_layout.addLayout(header_layout)
        
        # Create container for items (for collapsible effect)
        items_container = QWidget()
        items_layout = QVBoxLayout(items_container)
        items_layout.setContentsMargins(5, 5, 5, 0)
        items_layout.setSpacing(4)
        
        # Add items with modern checkboxes
        for item_name, item_type in items:
            checkbox = QCheckBox(item_type if item_type != "File" else os.path.basename(item_name.split(": ")[1]) if ": " in item_name else item_name)
            checkbox.setStyleSheet("""
                QCheckBox {
                    color: #ddd;
                    spacing: 5px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                    border: 1px solid #777;
                    border-radius: 3px;
                    background-color: #444;
                }
                QCheckBox::indicator:checked {
                    background-color: #6699ff;
                    border: 1px solid #6699ff;
                    image: url(check.png);  /* Will fall back to default if not found */
                }
                QCheckBox::indicator:hover {
                    border: 1px solid #999;
                }
            """)
            checkbox.setChecked(current_settings.get(item_name, False))
            checkbox.setObjectName(item_name)  # Store original item name
            
            # Connect the state change
            checkbox.stateChanged.connect(lambda state, cb=checkbox: self._on_checkbox_changed(cb))
            
            items_layout.addWidget(checkbox)
        
        # Add items container to section
        section_layout.addWidget(items_container)
        
        # Set up toggle behavior
        toggle_btn.clicked.connect(lambda checked, w=items_container, b=toggle_btn: self._toggle_section(w, b))
        
        # Add complete section to content layout
        self.content_layout.addWidget(section_frame)
        
        # Store section in our tracking dictionary
        self.corpus_sections[corpus_name] = {
            'frame': section_frame,
            'container': items_container,
            'toggle_btn': toggle_btn
        }
    
    def _toggle_section(self, container, button):
        """Toggle visibility of a section's items."""
        if container.isVisible():
            container.hide()
            button.setText("►")  # Right arrow for collapsed
        else:
            container.show()
            button.setText("▼")  # Down arrow for expanded
    
    def _on_checkbox_changed(self, checkbox):
        """Handle checkbox state changes and update visibility settings."""
        if hasattr(self.target, 'visibility_updated'):
            # Collect all current states
            settings = {}
            for corpus_name, section in self.corpus_sections.items():
                container = section['container']
                for i in range(container.layout().count()):
                    item = container.layout().itemAt(i).widget()
                    if isinstance(item, QCheckBox):
                        # Use the original item name stored in objectName
                        item_name = item.objectName()
                        settings[item_name] = item.isChecked()
            
            # Emit the updated settings
            self.target.visibility_updated.emit(settings)
    
    def close_sidebar(self):
        """Close the sidebar with animation."""
        print(f"[DEBUG] close_sidebar called, is_visible: {self.is_visible}, is_animating: {self.is_animating}")
        
        # If already animating or not visible, don't do anything
        if self.is_animating or not self.is_visible:
            print("[DEBUG] Animation in progress or sidebar not visible, ignoring close_sidebar call")
            return
        
        # Create a fresh animation for closing
        self.close_animation = QPropertyAnimation(self, b"pos")
        self.close_animation.setDuration(200)
        self.close_animation.setStartValue(self.pos())
        self.close_animation.setEndValue(QPoint(-self.width(), 0))
        
        # Connect signals
        self.close_animation.finished.connect(self._on_close_finished)
        self.is_animating = True
        
        # Start animation
        self.close_animation.start()
        print("[DEBUG] Sidebar close animation started")


