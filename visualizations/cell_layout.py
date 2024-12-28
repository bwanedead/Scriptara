# cell_layout.py
print("DEBUG: cell_layout_DEBUG.py is now actually loading!")
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



class FrequencyReportsLayout:
    """
    A layout class that displays all file_reports (Master + each file) in a simple interface
    with Previous / Next buttons to cycle through them.
    """

    def __init__(self, file_reports):
        self.file_reports = file_reports
        # We'll store a list of {"title": <filename or 'Master'>, "data": {...}}
        self.reports_list = []
        self._build_reports_list()

        self.current_index = 0  # start at 0 (first report)

    def _build_reports_list(self):
        # If there's a "Master Report", put it first
        if "Master Report" in self.file_reports:
            self.reports_list.append({
                "title": "Master Report",
                "data": self.file_reports["Master Report"]
            })
        # Then add all other files
        for key, val in self.file_reports.items():
            if key != "Master Report":
                self.reports_list.append({
                    "title": key,
                    "data": val
                })

    def generate_layout(self):
        """
        Creates the layout with a label to display the current report name,
        plus Previous/Next buttons to cycle through the list.
        """
        layout_widget = QWidget()
        main_layout = QVBoxLayout(layout_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)

        # Title label that shows "Report X of N: short_name"
        self.title_label = QLabel("")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 16px; color: #FFFFFF;")
        main_layout.addWidget(self.title_label)

        # Navigation buttons
        nav_layout = QHBoxLayout()

        prev_button = QPushButton("Previous")
        prev_button.clicked.connect(self.show_previous_report)
        nav_layout.addWidget(prev_button)

        next_button = QPushButton("Next")
        next_button.clicked.connect(self.show_next_report)
        nav_layout.addWidget(next_button)

        nav_layout.addStretch()
        main_layout.addLayout(nav_layout)

        # Initialize the label for the current report
        self.update_title()

        return layout_widget

    def show_previous_report(self):
        if self.reports_list:
            self.current_index = (self.current_index - 1) % len(self.reports_list)
            self.update_title()

    def show_next_report(self):
        if self.reports_list:
            self.current_index = (self.current_index + 1) % len(self.reports_list)
            self.update_title()

    def update_title(self):
        if not self.reports_list:
            self.title_label.setText("No Reports Available")
            return

        total = len(self.reports_list)
        # current report dict
        report_dict = self.reports_list[self.current_index]
        report_title = report_dict["title"]

        # For "Master Report," just show that. Otherwise, show the file's base name
        if report_title == "Master Report":
            short_name = "Master Report"
        else:
            short_name = os.path.basename(report_title)

        self.title_label.setText(f"Report {self.current_index + 1} of {total}: {short_name}")
