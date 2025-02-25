# metric_visualizations.py
import os
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidgetItem
from PyQt5.QtCore import Qt
import logging
import numpy as np
from analysis.advanced_analysis import compute_bo_scores

class BaseVisualization:
    def __init__(self, file_reports):
        self.file_reports = file_reports

    def widget(self):
        raise NotImplementedError("Subclasses must implement widget() method.")


class FrequencyDistributionVisualization(BaseVisualization):
    def __init__(self, file_reports, initial_mode='nominal'):
        super().__init__(file_reports)
        print("[DEBUG] Initializing FrequencyDistributionVisualization")
        self.current_mode = initial_mode
        self.x_log = False
        self.y_log = False

        # mode_map defines the index of each metric in word_stats
        self.mode_map = {
            'nominal': 1,
            'percentage': 2,
            'z_score': 3
        }

        print("[DEBUG] Setting up plot widget")
        pg.setConfigOptions(antialias=True, useOpenGL=True)
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('k')

        print("[DEBUG] Running initial plot update")
        self.update_plot()
        print("[DEBUG] Initialization complete")

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
        print(f"[DEBUG] Getting values for mode: {mode}")
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
            print(f"[DEBUG] Processed {rep_key}: {len(vals)} values")
        return data_sets

    def update_plot(self):
        print("[DEBUG] Starting plot update")
        self.plot_widget.clear()
        data = self.get_values(self.current_mode)

        if not data:
            print("[DEBUG] No data available to plot")
            return

        print(f"[DEBUG] Plotting {len(data)} datasets")
        colors = [
            (102, 153, 255), (102, 255, 178), (255, 204, 102),
            (255, 102, 178), (178, 102, 255), (102, 255, 255), (255, 178, 102)
        ]

        for i, (rep, (ranks, vals)) in enumerate(data.items()):
            c = colors[i % len(colors)]
            pen = pg.mkPen(color=c, width=1.5)
            self.plot_widget.plot(ranks, vals, pen=pen, name=rep, clear=False)
            print(f"[DEBUG] Plotted dataset {i+1}")

        self.plot_widget.getPlotItem().setLogMode(x=self.x_log, y=self.y_log)
        self.plot_widget.getPlotItem().enableAutoRange()
        self.plot_widget.getPlotItem().autoRange()

        # Force update
        self.plot_widget.update()
        self.plot_widget.repaint()
        QApplication.processEvents()
        print("[DEBUG] Plot update complete")


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
    

# visualizations/metric_visualizations.py

class BOScoreBarVisualization:
    """
    This class computes BOn1 and BOn2, storing them in instance variables
    so that the layout (BOScoreBarLayout) can retrieve them via get_data().
    """

    def __init__(self, file_reports, initial_mode=None):
        # Initialize with given parameters
        self.file_reports = file_reports
        self.initial_mode = initial_mode  # Store initial_mode for potential future use

        # Attempt to compute BO scores
        try:
            bon1_dict, bon2_dict = compute_bo_scores(file_reports)
            # Sort descending by score
            self.bon1_data = sorted(bon1_dict.items(), key=lambda x: x[1], reverse=True)
            self.bon2_data = sorted(bon2_dict.items(), key=lambda x: x[1], reverse=True)

        except Exception as e:
            print("[ERROR BOScoreBarVisualization] compute_bo_scores failed:", e)
            self.bon1_data = []
            self.bon2_data = []

    def get_data(self):
        """
        Called by the layout to retrieve (bon1_data, bon2_data).
        Each is a list of (word, score).
        """
        return (self.bon1_data, self.bon2_data)

    def widget(self):
        """
        Typically, we'd return a PyQt widget. But in this approach,
        the layout class (BOScoreBarLayout) constructs the PlotWidget.
        So we just return None or a small placeholder.
        """
        return None


    


class BOScoreLineVisualization:
    """
    Computes BOn1/BOn2 exactly like the Bar counterpart,
    storing data for line plotting.
    """
    def __init__(self, file_reports, initial_mode=None):
        self.file_reports = file_reports
        self.initial_mode = initial_mode
        self.bon1_data = []
        self.bon2_data = []
        try:
            bon1_dict, bon2_dict = compute_bo_scores(self.file_reports)
            self.bon1_data = sorted(bon1_dict.items(), key=lambda x: x[1], reverse=True)
            self.bon2_data = sorted(bon2_dict.items(), key=lambda x: x[1], reverse=True)
        except Exception as e:
            print("[ERROR BOScoreLineVisualization] compute_bo_scores failed:", e)

    def get_data(self):
        return (self.bon1_data, self.bon2_data)

    def widget(self):
        """
        Normally, the layout class will create the PlotWidget. So here, we can return None
        or a placeholder if you prefer.
        """
        placeholder = QLabel("Line visualization is handled in BOScoreLineLayout.")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("color: white; font-size: 16px;")
        return placeholder


class BOScoreTableVisualization:
    """
    Computes BOn1/BOn2 for table display.
    """
    def __init__(self, file_reports, initial_mode=None):
        self.file_reports = file_reports
        self.initial_mode = initial_mode
        self.bon1_data = []
        self.bon2_data = []
        try:
            bon1_dict, bon2_dict = compute_bo_scores(self.file_reports)
            self.bon1_data = sorted(bon1_dict.items(), key=lambda x: x[1], reverse=True)
            self.bon2_data = sorted(bon2_dict.items(), key=lambda x: x[1], reverse=True)
        except Exception as e:
            print("[ERROR BOScoreTableVisualization] compute_bo_scores failed:", e)

    def get_data(self):
        return (self.bon1_data, self.bon2_data)

    def widget(self):
        """
        The layout class will create the QTableWidget. Here we just return None or
        a placeholder again.
        """
        placeholder = QLabel("Table layout is handled in BOScoreTableLayout.")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("color: white; font-size: 16px;")
        return placeholder