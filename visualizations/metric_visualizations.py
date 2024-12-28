# metric_visualizations.py
import os
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt

class BaseVisualization:
    def __init__(self, file_reports):
        self.file_reports = file_reports

    def widget(self):
        raise NotImplementedError("Subclasses must implement widget() method.")


class FrequencyDistributionVisualization(BaseVisualization):
    def __init__(self, file_reports, initial_mode='nominal'):
        super().__init__(file_reports)
        self.current_mode = initial_mode
        self.x_log = False
        self.y_log = False

        # mode_map defines the index of each metric in word_stats
        self.mode_map = {
            'nominal': 1,
            'percentage': 2,
            'z_score': 3
        }

        pg.setConfigOptions(antialias=True, useOpenGL=True)
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('k')

        self.update_plot()

    def widget(self):
        return self.plot_widget

    def set_mode(self, mode):
        if mode in self.mode_map:
            self.current_mode = mode
        else:
            self.current_mode = 'nominal'
        self.update_plot()

    def set_x_log(self, enabled):
        self.x_log = enabled
        self.update_plot()

    def set_y_log(self, enabled):
        self.y_log = enabled
        self.update_plot()

    def get_values(self, mode):
        col = self.mode_map.get(mode, 1)
        data_sets = {}
        for rep_key, rep_data in self.file_reports.items():
            if rep_key == "Master Report":
                continue
            stats = rep_data['data']['word_stats']
            if not stats:
                continue
            ranks = range(1, len(stats) + 1)
            vals = [s[col] for s in stats]
            data_sets[rep_key] = (list(ranks), vals)
        return data_sets

    def update_plot(self):
        self.plot_widget.clear()
        data = self.get_values(self.current_mode)

        if not data:
            print("DEBUG: No data available to plot.")
            return

        colors = [
            (102, 153, 255), (102, 255, 178), (255, 204, 102),
            (255, 102, 178), (178, 102, 255), (102, 255, 255), (255, 178, 102)
        ]

        for i, (rep, (ranks, vals)) in enumerate(data.items()):
            c = colors[i % len(colors)]
            pen = pg.mkPen(color=c, width=1.5)
            self.plot_widget.plot(ranks, vals, pen=pen, name=rep, clear=False)

        self.plot_widget.getPlotItem().setLogMode(x=self.x_log, y=self.y_log)
        self.plot_widget.getPlotItem().enableAutoRange()
        self.plot_widget.getPlotItem().autoRange()

        # Force update
        self.plot_widget.update()
        self.plot_widget.repaint()
        QApplication.processEvents()


class FrequencyReportsAggregator:
    """
    A class to aggregate and prepare reports (including the Master Report) for navigation and display.
    Provides a widget() method with Next/Previous plus a test button, all wired the same way.
    """

    def __init__(self, file_reports):
        print("DEBUG: FrequencyReportsAggregator __init__ fired!")
        self.file_reports = file_reports
        self.aggregated_reports = []
        self._aggregate_reports()

        self.current_index = 0
        self.title_label = None

        # We'll store the buttons as instance attributes so they don't go out of scope
        self.prev_button = None
        self.next_button = None
        self.test_button = None

    def _aggregate_reports(self):
        """
        Aggregates all reports into a list for easier navigation.
        Ensures the Master Report (if present) is first.
        """
        if "Master Report" in self.file_reports:
            self.aggregated_reports.append({
                "title": "Master Report",
                "data": self.file_reports["Master Report"]
            })

        for report_key, report_data in self.file_reports.items():
            if report_key != "Master Report":
                self.aggregated_reports.append({
                    "title": report_key,
                    "data": report_data
                })

    def widget(self):
        """
        Returns a QWidget containing:
          - A label showing "Report X of N: short_name"
          - Two buttons (Previous, Next) wired exactly like the test button
          - A "TEST DEBUG BUTTON" to confirm clicks definitely arrive
        """
        from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
        from PyQt5.QtCore import Qt
        import os

        container = QWidget()
        layout = QVBoxLayout(container)

        self.title_label = QLabel()
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 16px; color: #FFFFFF;")
        layout.addWidget(self.title_label)

        btn_layout = QHBoxLayout()

        # -------- PREV BUTTON --------
        self.prev_button = QPushButton("Previous")
        # 1) Quick inline debug
        self.prev_button.clicked.connect(lambda: print("DEBUG: aggregator PREVIOUS button was clicked!"))
        # 2) Actual aggregator method
        self.prev_button.clicked.connect(self.on_prev_clicked)
        btn_layout.addWidget(self.prev_button)

        # -------- NEXT BUTTON --------
        self.next_button = QPushButton("Next")
        # 1) Quick inline debug
        self.next_button.clicked.connect(lambda: print("DEBUG: aggregator NEXT button was clicked!"))
        # 2) Actual aggregator method
        self.next_button.clicked.connect(self.on_next_clicked)
        btn_layout.addWidget(self.next_button)

        layout.addLayout(btn_layout)

        # -------- TEST DEBUG BUTTON (unchanged) --------
        self.test_button = QPushButton("TEST DEBUG BUTTON")
        self.test_button.setStyleSheet("background-color: red; color: white;")
        # Quick inline debug
        self.test_button.clicked.connect(lambda: print("DEBUG: aggregator TEST BUTTON was clicked!"))
        layout.addWidget(self.test_button)

        self.update_label()
        return container

    def on_prev_clicked(self):
        print("DEBUG: on_prev_clicked() aggregator method fired!")
        if self.aggregated_reports:
            self.current_index = (self.current_index - 1) % len(self.aggregated_reports)
        self.update_label()

    def on_next_clicked(self):
        print("DEBUG: on_next_clicked() aggregator method fired!")
        if self.aggregated_reports:
            self.current_index = (self.current_index + 1) % len(self.aggregated_reports)
        self.update_label()

    def update_label(self):
        if not self.aggregated_reports:
            if self.title_label:
                self.title_label.setText("No Reports Available")
            return

        total = len(self.aggregated_reports)
        report_dict = self.aggregated_reports[self.current_index]
        report_title = report_dict["title"]

        import os
        if report_title == "Master Report":
            short_name = "Master Report"
        else:
            short_name = os.path.basename(report_title)

        if self.title_label:
            self.title_label.setText(f"Report {self.current_index+1} of {total}: {short_name}")

    #
    #  Original aggregator getters below (if needed)
    #
    def get_aggregated_list(self):
        return self.aggregated_reports

    def get_report_titles(self):
        return [r["title"] for r in self.aggregated_reports]

    def get_report_by_index(self, index):
        if 0 <= index < len(self.aggregated_reports):
            return self.aggregated_reports[index]
        raise IndexError("Report index out of range.")

    def get_report_count(self):
        return len(self.aggregated_reports)