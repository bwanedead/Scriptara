# cell_layout.py
from visualizations.metric_visualizations import FrequencyReportsAggregator
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
                            QHBoxLayout, QPushButton, QHeaderView, QComboBox, QToolButton
                            )
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush

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
    """
    A self-contained QWidget that aggregates 'Master Report' + other files
    and displays them in a QTableWidget with Next/Previous navigation.
    """

    def __init__(self, file_reports, parent=None):
        super().__init__()  # Do not pass parent here
        self.setParent(parent)  # Explicitly set the parent if needed

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

        # Nav buttons row
        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("Previous")
        self.prev_btn.clicked.connect(self.show_previous_report)
        nav_layout.addWidget(self.prev_btn)

        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.show_next_report)
        nav_layout.addWidget(self.next_btn)

        nav_layout.addStretch()
        main_layout.addLayout(nav_layout)

        # Table
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(["Word", "Count", "Pct", "Z", "LogZ"])
        main_layout.addWidget(self.table_widget)

        # Initialize
        self.update_table()

    def _build_aggregated_list(self):
        """Collect Master Report first, then others."""
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

        self.table_widget.setRowCount(len(word_stats))
        for r_i, row_val in enumerate(word_stats):
            # row_val = (word, count, pct, z, logz)
            word, count, pct, z_val, logz = row_val
            self.table_widget.setItem(r_i, 0, QTableWidgetItem(str(word)))
            self.table_widget.setItem(r_i, 1, QTableWidgetItem(str(count)))
            self.table_widget.setItem(r_i, 2, QTableWidgetItem(f"{pct:.2f}"))
            self.table_widget.setItem(r_i, 3, QTableWidgetItem(f"{z_val:.2f}"))
            self.table_widget.setItem(r_i, 4, QTableWidgetItem(f"{logz:.2f}"))

        for c in range(5):
            self.table_widget.horizontalHeader().setSectionResizeMode(c, QHeaderView.Stretch)

    def show_previous_report(self):
        print("DEBUG: show_previous_report() in FrequencyReportsLayout")
        if self.reports_list:
            self.current_index = (self.current_index - 1) % len(self.reports_list)
            self.update_table()

    def show_next_report(self):
        print("DEBUG: show_next_report() in FrequencyReportsLayout")
        if self.reports_list:
            self.current_index = (self.current_index + 1) % len(self.reports_list)
            self.update_table()