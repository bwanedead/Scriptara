# cell_layout.py
from visualizations.metric_visualizations import FrequencyReportsAggregator
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
                            QHBoxLayout, QPushButton, QHeaderView, QComboBox, QToolButton
                            )
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush
from pyqtgraph import PlotWidget, BarGraphItem, mkPen
import numpy as np


class BaseMetricLayout:
    def __init__(self, file_reports, report_key):
        self.file_reports = file_reports
        self.report_key = report_key

    def generate_layout(self):
        """Override this in subclasses to generate the specific layout."""
        raise NotImplementedError

    def add_buttons(self, layout):
        """Override in subclasses to add any extra controls."""
        pass


class FrequencyDistributionLayout:
    def __init__(self, vis):
        self.vis = vis

    def generate_layout(self):
        layout_widget = QWidget()
        layout = QVBoxLayout(layout_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

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

        return layout_widget



class FrequencyReportsLayout(QWidget):
    def __init__(self, file_reports, parent=None):
        super().__init__(parent)

        print("DEBUG: FrequencyReportsLayout __init__ called!")
        self.file_reports = file_reports
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

        # Navigation Buttons
        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("Previous")
        self.prev_btn.clicked.connect(self.show_previous_report)
        nav_layout.addWidget(self.prev_btn)

        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.show_next_report)
        nav_layout.addWidget(self.next_btn)

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

    def _build_aggregated_list(self):
        """Collect Master first, then others."""
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
        print("DEBUG: show_previous_report() in FrequencyReportsLayout")
        if self.reports_list:
            self.current_index = (self.current_index - 1) % len(self.reports_list)
            self.update_table()

    def show_next_report(self):
        """Show the next report."""
        print("DEBUG: show_next_report() in FrequencyReportsLayout")
        if self.reports_list:
            self.current_index = (self.current_index + 1) % len(self.reports_list)
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

        # Title
        title_label = QLabel("BO Score Bar Chart")
        title_label.setStyleSheet("color: #fff; font-size:16px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Controls for toggling visibility
        controls_layout = QHBoxLayout()

        # Toggle BOn1 button
        bon1_btn = QToolButton()
        bon1_btn.setText("Toggle BOn1")
        bon1_btn.setCheckable(True)
        bon1_btn.setChecked(self.show_bon1)
        bon1_btn.toggled.connect(self.on_bon1_toggle)
        controls_layout.addWidget(bon1_btn)
        self.widgets['bon1_button'] = bon1_btn  # Prevent GC
        print("[DEBUG] Connected bon1_btn toggled signal.")

        # Toggle BOn2 button
        bon2_btn = QToolButton()
        bon2_btn.setText("Toggle BOn2")
        bon2_btn.setCheckable(True)
        bon2_btn.setChecked(self.show_bon2)
        bon2_btn.toggled.connect(self.on_bon2_toggle)
        controls_layout.addWidget(bon2_btn)
        self.widgets['bon2_button'] = bon2_btn  # Prevent GC
        print("[DEBUG] Connected bon2_btn toggled signal.")

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

    def on_bon1_toggle(self, checked):
        print(f"[DEBUG] on_bon1_toggle called with checked={checked}")
        self.show_bon1 = checked
        self.update_plot()

    def on_bon2_toggle(self, checked):
        print(f"[DEBUG] on_bon2_toggle called with checked={checked}")
        self.show_bon2 = checked
        self.update_plot()







class BOScoreLineLayout:
    """
    Renders line plots for BOn1 and BOn2 using PyQtGraph.
    We could also add toggles for log-scale, or whether to show/hide BOn1/BOn2.
    """
    def __init__(self, vis):
        self.vis = vis  # Instance of BOScoreLineVisualization
        self.plot_widget = None
        # Let's store some toggles to optionally show/hide each curve
        self.show_bon1 = True
        self.show_bon2 = True
        self.x_log = False
        self.y_log = False

    def generate_layout(self):
        layout_widget = QWidget()
        layout = QVBoxLayout(layout_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        title_label = QLabel("BO Score Line Chart")
        title_label.setStyleSheet("color: #fff; font-size:16px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Optional controls row
        controls_layout = QHBoxLayout()

        bon1_btn = QToolButton()
        bon1_btn.setText("Toggle BOn1")
        bon1_btn.setCheckable(True)
        bon1_btn.setChecked(True)
        bon1_btn.toggled.connect(self.on_bon1_toggle)
        controls_layout.addWidget(bon1_btn)

        bon2_btn = QToolButton()
        bon2_btn.setText("Toggle BOn2")
        bon2_btn.setCheckable(True)
        bon2_btn.setChecked(True)
        bon2_btn.toggled.connect(self.on_bon2_toggle)
        controls_layout.addWidget(bon2_btn)

        x_log_btn = QToolButton()
        x_log_btn.setText("X Log")
        x_log_btn.setCheckable(True)
        x_log_btn.setChecked(False)
        x_log_btn.toggled.connect(self.on_x_log_toggled)
        controls_layout.addWidget(x_log_btn)

        y_log_btn = QToolButton()
        y_log_btn.setText("Y Log")
        y_log_btn.setCheckable(True)
        y_log_btn.setChecked(False)
        y_log_btn.toggled.connect(self.on_y_log_toggled)
        controls_layout.addWidget(y_log_btn)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # Create the PlotWidget
        self.plot_widget = PlotWidget()
        self.plot_widget.setBackground('k')
        layout.addWidget(self.plot_widget)

        # Draw lines initially
        self.update_plot()

        return layout_widget

    def update_plot(self):
        bon1_data, bon2_data = self.vis.get_data()

        self.plot_widget.clear()
        plot_item = self.plot_widget.getPlotItem()

        # Set log modes (if toggled)
        plot_item.setLogMode(self.x_log, self.y_log)

        # BOn1 line
        if self.show_bon1 and bon1_data:
            x_vals = np.arange(1, len(bon1_data)+1)
            y_vals = [val for (_, val) in bon1_data]
            pen = mkPen(color='r', width=2)
            plot_item.plot(x_vals, y_vals, pen=pen, name="BOn1", clear=False)

        # BOn2 line
        if self.show_bon2 and bon2_data:
            x_vals = np.arange(1, len(bon2_data)+1)
            y_vals = [val for (_, val) in bon2_data]
            pen = mkPen(color='g', width=2)
            plot_item.plot(x_vals, y_vals, pen=pen, name="BOn2", clear=False)

        plot_item.setLabel("bottom", "Rank")
        plot_item.setLabel("left",  "BO Score")
        plot_item.enableAutoRange()
        plot_item.autoRange()

    # --- Toggled slots ---
    def on_bon1_toggle(self, checked):
        self.show_bon1 = checked
        self.update_plot()

    def on_bon2_toggle(self, checked):
        self.show_bon2 = checked
        self.update_plot()

    def on_x_log_toggled(self, checked):
        self.x_log = checked
        self.update_plot()

    def on_y_log_toggled(self, checked):
        self.y_log = checked
        self.update_plot()


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

        title_label = QLabel("BO Score Table")
        title_label.setStyleSheet("color: #fff; font-size:16px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

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

