# metric_visualizations.py
import os
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
import logging

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
    Gathers "Master Report" + any other files in a list. No UI code here.
    """
    def __init__(self, file_reports):
        self.file_reports = file_reports
        self.aggregated_list = []
        self._aggregate()

    def _aggregate(self):
        # Put Master first if it exists
        if "Master Report" in self.file_reports:
            self.aggregated_list.append({
                "title": "Master Report",
                "data": self.file_reports["Master Report"]
            })

        # Add the other files
        for k, v in self.file_reports.items():
            if k != "Master Report":
                self.aggregated_list.append({
                    "title": k,
                    "data": v
                })

    def get_list(self):
        return self.aggregated_list

    def count(self):
        return len(self.aggregated_list)

    def get_report_at(self, idx):
        return self.aggregated_list[idx]