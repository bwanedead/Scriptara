# cell_layout.py
from visualizations.metric_visualizations import FrequencyReportsAggregator
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
                            QHBoxLayout, QPushButton, QHeaderView, QComboBox, QToolButton
                            )
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QBrush
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

        print(f"DEBUG: FrequencyReportsLayout __init__ called with corpus_id: {corpus_id}")
        self.controller = controller
        self.corpus_id = corpus_id
        self.file_reports = {}
        
        # Get the appropriate data source
        self.update_data_source()
            
        self.reports_list = []
        self._build_aggregated_list()

        self.current_index = 0

        # Build the UI
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)

        # Title Label
        self.title_label = QLabel()
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size:16px; color:#FFFFFF;")
        main_layout.addWidget(self.title_label)

        # Add corpus indicator
        if self.corpus_id:
            self.corpus_label = QLabel(f"Corpus: {self.corpus_id}")
            self.corpus_label.setAlignment(Qt.AlignCenter)
            self.corpus_label.setStyleSheet("font-size:12px; color:#AAAAAA;")
            main_layout.addWidget(self.corpus_label)

        # Navigation Buttons
        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("Previous")
        self.prev_btn.clicked.connect(self.show_previous_report)
        nav_layout.addWidget(self.prev_btn)

        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.show_next_report)
        nav_layout.addWidget(self.next_btn)

        # Add refresh button
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh)
        self.refresh_btn.setToolTip(f"Refresh data from corpus: {self.corpus_id}")
        nav_layout.addWidget(self.refresh_btn)

        nav_layout.addStretch()
        main_layout.addLayout(nav_layout)

        # Table Widget
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(5)  # Only the original 5 columns
        self.table_widget.setHorizontalHeaderLabels(["Rank", "Word", "Count", "Pct", "Z", "LogZ"])
        self.table_widget.setStyleSheet("""
            QTableWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                alternate-background-color: #3b3b3b;
                gridline-color: #555555;
            }
            QHeaderView::section {
                background-color: #444444;
                color: #ffffff;
                padding: 4px;
                border: 1px solid #555555;
            }
            QTableCornerButton::section {
                background-color: #444444; /* Match dark mode for top-left cell */
                border: 1px solid #555555;
            }
        """)
        self.table_widget.setAlternatingRowColors(True)
        main_layout.addWidget(self.table_widget)

        # Initialize with the first report
        self.update_table()
        
    def update_data_source(self):
        """Update the data source based on corpus_id - similar to BaseVisualization"""
        # Always start with empty reports to avoid stale data
        self.file_reports = {}
        
        if not self.controller:
            print("[ERROR] FrequencyReportsLayout has no controller reference")
            return
            
        if not self.corpus_id:
            print("[ERROR] FrequencyReportsLayout has no corpus_id")
            return
            
        if not hasattr(self.controller, 'get_report_for_corpus'):
            print("[ERROR] FrequencyReportsLayout controller lacks get_report_for_corpus method")
            return
            
        # Check if report exists and generate if needed
        if hasattr(self.controller, 'has_report_for_corpus'):
            has_report = self.controller.has_report_for_corpus(self.corpus_id)
            print(f"[DEBUG] FrequencyReportsLayout checking if report exists for {self.corpus_id}: {has_report}")
            
            if not has_report:
                print(f"[DEBUG] FrequencyReportsLayout generating initial report for corpus: {self.corpus_id}")
                success = self.controller.generate_report_for_corpus(self.corpus_id)
                if not success:
                    print(f"[ERROR] Failed to generate report for corpus: {self.corpus_id}")
                    return
                print(f"[DEBUG] FrequencyReportsLayout report generation success: {success}")
        else:
            # If has_report_for_corpus doesn't exist, always try to generate
            print(f"[DEBUG] FrequencyReportsLayout generating report for corpus (no has_report method): {self.corpus_id}")
            self.controller.generate_report_for_corpus(self.corpus_id)
            
        # Get corpus-specific data
        self.file_reports = self.controller.get_report_for_corpus(self.corpus_id)
        
        # Verify we got data
        if not self.file_reports:
            print(f"[ERROR] FrequencyReportsLayout got empty report for corpus: {self.corpus_id}")
        else:
            print(f"[DEBUG] FrequencyReportsLayout fetched report for corpus: {self.corpus_id}, keys: {list(self.file_reports.keys())}")

    def _build_aggregated_list(self):
        """Collect Master first, then others."""
        self.reports_list = []
        if not self.file_reports:
            print(f"[ERROR] No file_reports data to build list for corpus: {self.corpus_id}")
            return
            
        if "Master Report" in self.file_reports:
            self.reports_list.append({
                "title": "Master Report",
                "data": self.file_reports["Master Report"]
            })

        for k, v in self.file_reports.items():
            if k != "Master Report":
                self.reports_list.append({
                    "title": k,
                    "data": v
                })
                
        print(f"[DEBUG] Built reports list with {len(self.reports_list)} items for corpus: {self.corpus_id}")

    def update_table(self):
        if not self.reports_list:
            self.title_label.setText("No Reports Available")
            self.table_widget.setRowCount(0)
            return

        total = len(self.reports_list)
        current_report = self.reports_list[self.current_index]
        report_title = current_report["title"]
        short_label = ("Master Report" 
                    if report_title == "Master Report" 
                    else os.path.basename(report_title))
        self.title_label.setText(f"Report {self.current_index + 1} of {total}: {short_label}")

        # Extract word_stats from current_report["data"]["data"]["word_stats"]
        data_wrapper = current_report["data"]
        word_stats = []
        if "data" in data_wrapper and "word_stats" in data_wrapper["data"]:
            word_stats = data_wrapper["data"]["word_stats"]

        # Update the table row count
        self.table_widget.setRowCount(len(word_stats))

        # Set the corrected column headers
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels([
            "Rank", "Word", "Count", "Percentage Frequency", "Z-Score"
        ])

        # Disable default row numbers (vertical header labels)
        self.table_widget.verticalHeader().setVisible(False)

        for r_i, row_val in enumerate(word_stats):
            # row_val = (word, count, pct, z_val, logz)
            word, count, pct, z_val, _ = row_val  # Skip unnecessary logz column
            self.table_widget.setItem(r_i, 0, QTableWidgetItem(str(r_i + 1)))  # Rank
            self.table_widget.setItem(r_i, 1, QTableWidgetItem(str(word)))    # Word
            self.table_widget.setItem(r_i, 2, QTableWidgetItem(str(count)))   # Count
            self.table_widget.setItem(r_i, 3, QTableWidgetItem(f"{pct:.2f}")) # Percentage Frequency
            self.table_widget.setItem(r_i, 4, QTableWidgetItem(f"{z_val:.2f}"))  # Z-Score

        # Auto-stretch columns
        for c in range(5):
            self.table_widget.horizontalHeader().setSectionResizeMode(c, QHeaderView.Stretch)

    def show_previous_report(self):
        """Show the previous report."""
        print(f"DEBUG: show_previous_report() in FrequencyReportsLayout for corpus: {self.corpus_id}")
        if self.reports_list:
            self.current_index = (self.current_index - 1) % len(self.reports_list)
            self.update_table()

    def show_next_report(self):
        """Show the next report."""
        print(f"DEBUG: show_next_report() in FrequencyReportsLayout for corpus: {self.corpus_id}")
        if self.reports_list:
            self.current_index = (self.current_index + 1) % len(self.reports_list)
            self.update_table()

    def refresh(self):
        """Refresh the data source and update the table."""
        print(f"DEBUG: Refreshing FrequencyReportsLayout for corpus: {self.corpus_id}")
        
        # Update the data source
        self.update_data_source()
            
        # Rebuild the reports list and update the table
        self.reports_list = []
        self._build_aggregated_list()
        self.current_index = 0  # Reset to first report
        self.update_table()


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

