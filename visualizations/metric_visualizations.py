# metric_visualizations.py
import os
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidgetItem
from PyQt5.QtCore import Qt, QObject, pyqtSignal
import logging
import numpy as np
from analysis.advanced_analysis import compute_bo_scores
from PyQt5.QtGui import QColor

class BaseVisualization(QWidget):
    visibility_updated = pyqtSignal(dict)

    def __init__(self, controller=None, corpus_ids=None, initial_mode=None, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.corpus_ids = corpus_ids if corpus_ids is not None else []
        self.initial_mode = initial_mode
        self.file_reports = {}
        
        print(f"[DEBUG] BaseVisualization init with corpus_ids: {self.corpus_ids}")
        
    def update_data_source(self):
        """Update the data source based on corpus_ids"""
        self.file_reports = getattr(self, 'file_reports', {})
        
        if not self.controller:
            print("[ERROR] BaseViz has no controller reference")
            return
            
        if not self.corpus_ids:
            print("[ERROR] BaseViz has no corpus_ids")
            return
            
        if not hasattr(self.controller, 'get_report_for_corpus'):
            print("[ERROR] BaseViz controller lacks get_report_for_corpus method")
            return
            
        # Fetch reports only for corpus_ids not already in cache
        for corpus_id in self.corpus_ids:
            if corpus_id not in self.file_reports:
                if hasattr(self.controller, 'has_report_for_corpus'):
                    has_report = self.controller.has_report_for_corpus(corpus_id)
                    print(f"[DEBUG] BaseViz checking if report exists for {corpus_id}: {has_report}")
                    
                    if not has_report:
                        print(f"[DEBUG] BaseViz generating initial report for corpus: {corpus_id}")
                        success = self.controller.generate_report_for_corpus(corpus_id)
                        if not success:
                            print(f"[ERROR] Failed to generate report for corpus: {corpus_id}")
                            continue
                        print(f"[DEBUG] BaseViz report generation success: {success}")
                else:
                    # If has_report_for_corpus doesn't exist, always try to generate
                    print(f"[DEBUG] BaseViz generating report for corpus (no has_report method): {corpus_id}")
                    self.controller.generate_report_for_corpus(corpus_id)
                
                self.file_reports[corpus_id] = self.controller.get_report_for_corpus(corpus_id)
                
                if not self.file_reports[corpus_id]:
                    print(f"[ERROR] BaseViz got empty report for corpus: {corpus_id}")
                else:
                    print(f"[DEBUG] BaseViz fetched report for corpus: {corpus_id}, keys: {list(self.file_reports[corpus_id].keys())}")
        
        if not self.file_reports:
            print(f"[ERROR] BaseViz got empty report for corpus_ids: {self.corpus_ids}")
            self.debug_report_access()
        else:
            print(f"[DEBUG] BaseViz has reports for corpus_ids: {list(self.file_reports.keys())}")
    
    def set_corpus_ids(self, corpus_ids):
        """Update corpus_ids without fetching data"""
        self.corpus_ids = corpus_ids if corpus_ids is not None else []
        print(f"[DEBUG] BaseVisualization updated corpus_ids to: {self.corpus_ids}")

    def refresh_data_source(self):
        """Clear cache and refetch all data"""
        self.file_reports.clear()
        self.update_data_source()
        print(f"[DEBUG] BaseVisualization refreshed data source for corpus_ids: {self.corpus_ids}")
    
    def debug_report_access(self):
        """Debug report access issues"""
        print(f"[DEBUG] Debugging report access for corpus_ids: {self.corpus_ids}")
        
        if not self.controller:
            print("[ERROR] No controller reference")
            return
            
        if not self.corpus_ids:
            print("[ERROR] No corpus_ids")
            return
            
        # Check if the corpus exists
        if hasattr(self.controller, 'corpora'):
            for corpus_id in self.corpus_ids:
                if corpus_id in self.controller.corpora:
                    print(f"[DEBUG] Corpus '{corpus_id}' exists in controller.corpora")
                    corpus = self.controller.corpora[corpus_id]
                    print(f"[DEBUG] Corpus '{corpus_id}' has {len(corpus.get_files())} files")
                else:
                    print(f"[ERROR] Corpus '{corpus_id}' does not exist in controller.corpora")
                    print(f"[DEBUG] Available corpora: {list(self.controller.corpora.keys())}")
        else:
            print("[ERROR] Controller has no corpora attribute")
            
        # Check if the report manager exists
        if hasattr(self.controller, 'report_manager'):
            print("[DEBUG] Controller has report_manager")
            
            # Check if the report manager has the report
            if hasattr(self.controller.report_manager, 'has_report_for_corpus'):
                for corpus_id in self.corpus_ids:
                    has_report = self.controller.report_manager.has_report_for_corpus(corpus_id)
                    print(f"[DEBUG] Report manager has_report_for_corpus('{corpus_id}'): {has_report}")
                    
                    if has_report:
                        # Check the report content
                        report = self.controller.report_manager.get_report_for_corpus(corpus_id)
                        print(f"[DEBUG] Report keys: {list(report.keys())}")
                        
                        # Check if there's a Master Report
                        if "Master Report" in report:
                            master_data = report["Master Report"]
                            if "data" in master_data and "word_stats" in master_data["data"]:
                                word_stats = master_data["data"]["word_stats"]
                                print(f"[DEBUG] Master Report has {len(word_stats)} word stats")
                            else:
                                print("[DEBUG] Master Report has no word stats")
                        else:
                            print("[DEBUG] No Master Report in report")
                            
                        # Count individual file reports
                        file_reports = [k for k in report.keys() if k != "Master Report"]
                        print(f"[DEBUG] Report has {len(file_reports)} individual file reports")
                    else:
                        # Try to generate the report
                        print(f"[DEBUG] Attempting to generate report for corpus: {corpus_id}")
                        if hasattr(self.controller, 'generate_report_for_corpus'):
                            success = self.controller.generate_report_for_corpus(corpus_id)
                            print(f"[DEBUG] generate_report_for_corpus result: {success}")
                            
                            # Check if the report was generated
                            has_report = self.controller.report_manager.has_report_for_corpus(corpus_id)
                            print(f"[DEBUG] After generation, has_report_for_corpus('{corpus_id}'): {has_report}")
                        else:
                            print("[ERROR] Controller has no generate_report_for_corpus method")
            else:
                print("[ERROR] Report manager has no has_report_for_corpus method")
                
            # List all available reports
            if hasattr(self.controller.report_manager, 'list_available_reports'):
                available_reports = self.controller.report_manager.list_available_reports()
                print(f"[DEBUG] Available reports: {available_reports}")
            else:
                print("[ERROR] Report manager has no list_available_reports method")
        else:
            print("[ERROR] Controller has no report_manager attribute")
    
    def widget(self):
        """Return the visualization widget"""
        raise NotImplementedError("Subclasses must implement widget() method.")

class FrequencyDistributionSupplementary:
    def __init__(self, mode):
        self.mode = mode
        self.mode_map = {'nominal': 1, 'percentage': 2, 'z_score': 3}

    def compute_average_curve(self, corpus_id, file_reports):
        if corpus_id not in file_reports:
            return None
        corpus_report = file_reports[corpus_id]
        all_vals = []
        for file_key, file_report in corpus_report.items():
            if file_key != "Master Report" and 'data' in file_report and 'word_stats' in file_report['data']:
                stats = file_report['data']['word_stats']
                if stats:
                    all_vals.append([s[self.mode_map.get(self.mode, 1)] for s in stats])
        if not all_vals:
            return None
        max_len = max(len(vals) for vals in all_vals)
        averaged_vals = []
        for i in range(max_len):
            vals_at_rank = [vals[i] for vals in all_vals if i < len(vals)]
            averaged_vals.append(sum(vals_at_rank) / len(vals_at_rank) if vals_at_rank else 0)
        ranks = list(range(1, len(averaged_vals) + 1))
        return ranks, averaged_vals

    def compute_best_fit_curve(self, corpus_id, file_reports):
        ranks, avg_vals = self.compute_average_curve(corpus_id, file_reports) or (None, None)
        if not ranks or not avg_vals:
            return None
        coeffs = np.polyfit(ranks, avg_vals, 3)
        poly = np.poly1d(coeffs)
        best_fit_vals = [poly(x) for x in ranks]
        return ranks, best_fit_vals

    def compute_variability_band(self, corpus_id, file_reports):
        if corpus_id not in file_reports:
            return None
        corpus_report = file_reports[corpus_id]
        all_vals = []
        for file_key, file_report in corpus_report.items():
            if file_key != "Master Report" and 'data' in file_report and 'word_stats' in file_report['data']:
                stats = file_report['data']['word_stats']
                if stats:
                    all_vals.append([s[self.mode_map.get(self.mode, 1)] for s in stats])
        if not all_vals:
            return None
        max_len = max(len(vals) for vals in all_vals)
        min_vals, max_vals = [], []
        for i in range(max_len):
            vals_at_rank = [vals[i] for vals in all_vals if i < len(vals)]
            if not vals_at_rank:
                min_vals.append(0)
                max_vals.append(0)
            else:
                min_vals.append(min(vals_at_rank))
                max_vals.append(max(vals_at_rank))
        ranks = list(range(1, len(min_vals) + 1))
        
        # Debug output to confirm band data
        print(f"[DEBUG] Variability band for {corpus_id} computed with {len(ranks)} points. Sample min: {min_vals[:3]}, max: {max_vals[:3]}")
        
        return ranks, min_vals, max_vals

class FrequencyDistributionVisualization(BaseVisualization):
    def __init__(self, controller=None, initial_mode='nominal', corpus_ids=None):
        super().__init__(controller, corpus_ids, initial_mode)
        print(f"[DEBUG] Initializing FrequencyDistributionVisualization for corpus_ids: {corpus_ids}")
        self.current_mode = initial_mode
        self.x_log = False
        self.y_log = False
        self.supplementary = FrequencyDistributionSupplementary(self.current_mode)
        self.analytics_cache = {}  # {corpus_id: {"average": (ranks, vals), "best_fit": (ranks, vals), "band": (ranks, min_vals, max_vals)}}
        
        # Initialize visibility settings with default values (show corpus curves by default)
        self.visibility_settings = {}
        if corpus_ids:
            for corpus_id in corpus_ids:
                # Enable the corpus curves by default, but leave analytics off
                self.visibility_settings[corpus_id] = True
                # Initialize analytics settings to False so they don't show by default
                self.visibility_settings[f"{corpus_id} (Average)"] = False
                self.visibility_settings[f"{corpus_id} (Best Fit)"] = False
                self.visibility_settings[f"{corpus_id} (Band)"] = False
        
        # New color mapping for corpus coloring
        self.corpus_colors = {}  # {corpus_id: QColor}
        
        # Track color grouping state for each corpus
        self.color_grouping_enabled = {}  # {corpus_id: bool}
                
        self.mode_map = {'nominal': 1, 'percentage': 2, 'z_score': 3}
        pg.setConfigOptions(antialias=True, useOpenGL=True)
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('k')
        
        print(f"[DEBUG] Default visibility settings: {self.visibility_settings}")
        self.update_plot()
        self.visibility_updated.connect(self.set_visibility_settings)
        print("[DEBUG] Initialization complete")

    def update_data_source(self):
        old_reports = self.file_reports.copy()
        super().update_data_source()
        if old_reports != self.file_reports:  # Invalidate cache if data changes
            self.analytics_cache.clear()
            print(f"[DEBUG] Analytics cache cleared due to data change")

    def get_available_plot_settings(self):
        items = []
        if self.file_reports:
            for corpus_id in self.corpus_ids or []:
                if corpus_id in self.file_reports:
                    items.append(corpus_id)
                    items.extend([f"{corpus_id} (Average)", f"{corpus_id} (Best Fit)", f"{corpus_id} (Band)"])
        return items

    def set_visibility_settings(self, settings):
        print(f"[DEBUG] Setting visibility_settings: {settings}")
        # Process regular visibility settings
        for key, value in settings.items():
            # Special handling for color settings
            if key.startswith('_color_'):
                corpus_name = key[7:]  # Remove '_color_' prefix
                self.set_corpus_color(corpus_name, value)
            # Special handling for color grouping toggle
            elif key.startswith('_group_'):
                corpus_name = key[7:]  # Remove '_group_' prefix
                self.color_grouping_enabled[corpus_name] = value
                print(f"[DEBUG] Setting color grouping for {corpus_name} to {value}")
            else:
                self.visibility_settings[key] = value
        self.update_plot()

    def set_corpus_color(self, corpus_name, color):
        """Set the color for all curves in a corpus."""
        # If color is a string (like "#RRGGBB"), convert to QColor
        if isinstance(color, str):
            color = QColor(color)
            
        print(f"[DEBUG] Setting corpus color for {corpus_name} to {color.name()}")
        self.corpus_colors[corpus_name] = color
        # No need to update plot here, set_visibility_settings will do it

    def set_mode(self, mode):
        if mode in self.mode_map:
            self.current_mode = mode
            self.supplementary.mode = mode
            self.analytics_cache.clear()  # Invalidate cache on mode change
            print(f"[DEBUG] Analytics cache cleared due to mode change")
        else:
            self.current_mode = 'nominal'
            self.supplementary.mode = 'nominal'
        self.update_plot()

    def set_x_log(self, enabled):
        self.x_log = enabled
        self.update_plot()

    def set_y_log(self, enabled):
        self.y_log = enabled
        self.update_plot()

    def get_values(self, mode):
        print(f"[DEBUG] Getting values for mode: {mode} with visibility_settings: {self.visibility_settings}")
        col = self.mode_map.get(mode, 1)
        data_sets = {}
        self.update_data_source()
        if not self.file_reports:
            print(f"[ERROR] No file_reports data available")
            return data_sets
        for corpus_id in self.corpus_ids or []:
            if corpus_id in self.file_reports:
                if corpus_id not in self.analytics_cache:
                    self.analytics_cache[corpus_id] = {}
                if self.visibility_settings.get(corpus_id, False):
                    corpus_report = self.file_reports[corpus_id]
                    for file_key in corpus_report.keys():
                        if file_key != "Master Report":
                            file_report = corpus_report[file_key]
                            if 'data' in file_report and 'word_stats' in file_report['data']:
                                stats = file_report['data']['word_stats']
                                if stats:
                                    ranks = list(range(1, len(stats) + 1))
                                    vals = [s[col] for s in stats]
                                    data_sets[f"{corpus_id}: {os.path.basename(file_key)}"] = (ranks, vals)
                if self.visibility_settings.get(f"{corpus_id} (Average)", False):
                    if "average" not in self.analytics_cache[corpus_id]:
                        self.analytics_cache[corpus_id]["average"] = self.supplementary.compute_average_curve(corpus_id, self.file_reports)
                    if self.analytics_cache[corpus_id]["average"]:
                        data_sets[f"{corpus_id} (Average)"] = self.analytics_cache[corpus_id]["average"]
                if self.visibility_settings.get(f"{corpus_id} (Best Fit)", False):
                    if "best_fit" not in self.analytics_cache[corpus_id]:
                        self.analytics_cache[corpus_id]["best_fit"] = self.supplementary.compute_best_fit_curve(corpus_id, self.file_reports)
                    if self.analytics_cache[corpus_id]["best_fit"]:
                        data_sets[f"{corpus_id} (Best Fit)"] = self.analytics_cache[corpus_id]["best_fit"]
                if self.visibility_settings.get(f"{corpus_id} (Band)", False):
                    if "band" not in self.analytics_cache[corpus_id]:
                        self.analytics_cache[corpus_id]["band"] = self.supplementary.compute_variability_band(corpus_id, self.file_reports)
                    if self.analytics_cache[corpus_id]["band"]:
                        data_sets[f"{corpus_id} (Band)"] = self.analytics_cache[corpus_id]["band"]
                        print(f"[DEBUG] Added variability band for {corpus_id} to data_sets")
        return data_sets

    def update_plot(self):
        print(f"[DEBUG] Starting plot update with visibility_settings: {self.visibility_settings}")
        self.plot_widget.clear()
        data = self.get_values(self.current_mode)
        plot_item = self.plot_widget.getPlotItem()
        plot_item.setLogMode(x=self.x_log, y=self.y_log)
        if not data:
            print(f"[DEBUG] No data to plot")
            return
            
        # Default colors to use when corpus color grouping is not active
        default_colors = [(102, 153, 255), (102, 255, 178), (255, 204, 102), 
                         (255, 102, 178), (178, 102, 255), (102, 255, 255), (255, 178, 102)]
        color_index = 0
        
        # Track file count for each corpus for assigning unique colors
        corpus_file_count = {}
        
        # First determine corpus for each dataset for color grouping
        for name, data_item in data.items():
            corpus_name = name.split(":")[0] if ":" in name else name.split(" (")[0] if " (" in name else name
            
            # Count files per corpus for color index tracking
            if corpus_name not in corpus_file_count:
                corpus_file_count[corpus_name] = 0
            
            # Special handling for different item types
            if name.endswith("(Band)"):
                ranks, min_vals, max_vals = data_item
                
                # Use corpus color if grouping is enabled, otherwise use gray
                if corpus_name in self.color_grouping_enabled and self.color_grouping_enabled[corpus_name] and corpus_name in self.corpus_colors:
                    color = self.corpus_colors[corpus_name]
                    # Make a more transparent version for the fill
                    fill_color = QColor(color)
                    fill_color.setAlpha(50)  # Set transparency
                    pen_color = QColor(color)
                    pen_color.setAlpha(200)  # Less transparent for the lines
                else:
                    pen_color = QColor(180, 180, 180, 200)  # Light gray with some transparency
                    fill_color = QColor(150, 150, 150, 40)  # More transparent gray for fill
                
                # Plot min and max lines with slightly thinner pen
                min_curve = plot_item.plot(ranks, min_vals, pen=pg.mkPen(color=pen_color, width=1), name=f"{name} Min")
                max_curve = plot_item.plot(ranks, max_vals, pen=pg.mkPen(color=pen_color, width=1), name=f"{name} Max")
                
                # Create fill between with proper z-order (ensure it's behind curves)
                fill = pg.FillBetweenItem(min_curve, max_curve, brush=fill_color)
                # Add fill to plot first (lower z-order)
                plot_item.addItem(fill)
                # Ensure fill is behind other curves
                fill.setZValue(-10)
            else:
                ranks, vals = data_item
                
                # Choose pen color and style based on item type
                if name.endswith("(Average)"):
                    if corpus_name in self.color_grouping_enabled and self.color_grouping_enabled[corpus_name] and corpus_name in self.corpus_colors:
                        color = self.corpus_colors[corpus_name]
                        pen = pg.mkPen(color=color, width=2, style=Qt.DashLine)
                    else:
                        pen = pg.mkPen(color='w', width=2, style=Qt.DashLine)
                elif name.endswith("(Best Fit)"):
                    if corpus_name in self.color_grouping_enabled and self.color_grouping_enabled[corpus_name] and corpus_name in self.corpus_colors:
                        color = self.corpus_colors[corpus_name]
                        pen = pg.mkPen(color=color, width=2)
                    else:
                        pen = pg.mkPen(color='y', width=2)
                else:
                    # For regular file curves
                    if corpus_name in self.color_grouping_enabled and self.color_grouping_enabled[corpus_name] and corpus_name in self.corpus_colors:
                        # When grouping is enabled, use the corpus color for all files
                        color = self.corpus_colors[corpus_name]
                        pen = pg.mkPen(color=color, width=1.5)
                    else:
                        # When grouping is disabled, use unique colors for each file
                        corpus_file_count[corpus_name] += 1
                        color_idx = (color_index + corpus_file_count[corpus_name] - 1) % len(default_colors)
                        color = default_colors[color_idx]
                        pen = pg.mkPen(color=color, width=1.5)
                
                # Plot the curve
                plot_item.plot(ranks, vals, pen=pen, name=name)
            
            # Increment color index for the next corpus
            if corpus_name not in corpus_file_count:
                color_index += 1
        
        # Update plot display
        plot_item.enableAutoRange()
        plot_item.autoRange()
        self.plot_widget.update()
        self.plot_widget.repaint()
        QApplication.processEvents()
        print(f"[DEBUG] Plot update complete")

    def widget(self):
        return self.plot_widget

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
    

class BOScoreBarVisualization(BaseVisualization):
    """
    This class computes BOn1 and BOn2, storing them in instance variables
    so that the layout (BOScoreBarLayout) can retrieve them via get_data().
    """

    def __init__(self, controller=None, initial_mode=None, corpus_ids=None):
        super().__init__(controller, corpus_ids, initial_mode)
        self.bon1_data = []
        self.bon2_data = []
        
        print(f"[DEBUG] BOScoreBarVisualization initialized with corpus_ids: {corpus_ids}")
        # Update data based on corpus_id
        self.update_data()
        
    def update_data(self):
        """Update data using the appropriate corpus report"""
        try:
            # First ensure we have the latest data
            self.update_data_source()
            
            # Verify we have data
            if not self.file_reports:
                print(f"[ERROR] BOScoreBar has no data for corpus: {self.corpus_ids[0] if self.corpus_ids else None}")
                self.bon1_data = []
                self.bon2_data = []
                return
                
            # Process each corpus in corpus_ids
            all_file_reports = {}
            for corpus_id in self.corpus_ids:
                if corpus_id not in self.file_reports:
                    print(f"[ERROR] Corpus {corpus_id} not found in file_reports")
                    continue
                    
                # Get the corpus report and add its file reports to all_file_reports
                corpus_report = self.file_reports[corpus_id]
                print(f"[DEBUG] Processing corpus report for {corpus_id}, keys: {list(corpus_report.keys())}")
                
                # Add all file reports except Master Report
                for file_key, file_report in corpus_report.items():
                    if file_key != "Master Report":
                        all_file_reports[file_key] = file_report
            
            # Compute BO scores using all file reports
            if all_file_reports:
                bon1_dict, bon2_dict = compute_bo_scores(all_file_reports)
                
                # Sort descending by score
                self.bon1_data = sorted(bon1_dict.items(), key=lambda x: x[1], reverse=True)
                self.bon2_data = sorted(bon2_dict.items(), key=lambda x: x[1], reverse=True)
                
                print(f"[DEBUG] BOScoreBar calculated {len(self.bon1_data)} BOn1 scores and {len(self.bon2_data)} BOn2 scores for corpus: {self.corpus_ids}")
            else:
                print(f"[ERROR] No file reports found for corpus: {self.corpus_ids}")
                self.bon1_data = []
                self.bon2_data = []

        except Exception as e:
            print(f"[ERROR BOScoreBarVisualization] compute_bo_scores failed for corpus {self.corpus_ids}: {e}")
            import traceback
            traceback.print_exc()
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


class BOScoreLineVisualization(BaseVisualization):
    """
    Computes BOn1/BOn2 exactly like the Bar counterpart,
    storing data for line plotting.
    """
    def __init__(self, controller=None, initial_mode=None, corpus_ids=None):
        super().__init__(controller, corpus_ids, initial_mode)
        self.bon1_data = []
        self.bon2_data = []
        
        print(f"[DEBUG] BOScoreLineVisualization initialized with corpus_ids: {corpus_ids}")
        # Update data based on corpus_id
        self.update_data()
        
    def update_data(self):
        """Update data using the appropriate corpus report"""
        try:
            # First ensure we have the latest data
            self.update_data_source()
            
            # Verify we have data
            if not self.file_reports:
                print(f"[ERROR] BOScoreLine has no data for corpus: {self.corpus_ids[0] if self.corpus_ids else None}")
                self.bon1_data = []
                self.bon2_data = []
                return
                
            # Process each corpus in corpus_ids
            all_file_reports = {}
            for corpus_id in self.corpus_ids:
                if corpus_id not in self.file_reports:
                    print(f"[ERROR] Corpus {corpus_id} not found in file_reports")
                    continue
                    
                # Get the corpus report and add its file reports to all_file_reports
                corpus_report = self.file_reports[corpus_id]
                print(f"[DEBUG] Processing corpus report for {corpus_id}, keys: {list(corpus_report.keys())}")
                
                # Add all file reports except Master Report
                for file_key, file_report in corpus_report.items():
                    if file_key != "Master Report":
                        all_file_reports[file_key] = file_report
            
            # Compute BO scores using all file reports
            if all_file_reports:
                bon1_dict, bon2_dict = compute_bo_scores(all_file_reports)
                
                # Sort descending by score
                self.bon1_data = sorted(bon1_dict.items(), key=lambda x: x[1], reverse=True)
                self.bon2_data = sorted(bon2_dict.items(), key=lambda x: x[1], reverse=True)
                
                print(f"[DEBUG] BOScoreLine calculated {len(self.bon1_data)} BOn1 scores and {len(self.bon2_data)} BOn2 scores for corpus: {self.corpus_ids}")
            else:
                print(f"[ERROR] No file reports found for corpus: {self.corpus_ids}")
                self.bon1_data = []
                self.bon2_data = []
                
        except Exception as e:
            print(f"[ERROR BOScoreLineVisualization] compute_bo_scores failed for corpus {self.corpus_ids}: {e}")
            import traceback
            traceback.print_exc()
            self.bon1_data = []
            self.bon2_data = []

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


class BOScoreTableVisualization(BaseVisualization):
    """
    Computes BOn1/BOn2 for table display.
    """
    def __init__(self, controller=None, initial_mode=None, corpus_ids=None):
        super().__init__(controller, corpus_ids, initial_mode)
        self.bon1_data = []
        self.bon2_data = []
        
        print(f"[DEBUG] BOScoreTableVisualization initialized with corpus_ids: {corpus_ids}")
        # Update data based on corpus_id
        self.update_data()
        
    def update_data(self):
        """Update data using the appropriate corpus report"""
        try:
            # First ensure we have the latest data
            self.update_data_source()
            
            # Verify we have data
            if not self.file_reports:
                print(f"[ERROR] BOScoreTable has no data for corpus: {self.corpus_ids[0] if self.corpus_ids else None}")
                self.bon1_data = []
                self.bon2_data = []
                return
                
            # Process each corpus in corpus_ids
            all_file_reports = {}
            for corpus_id in self.corpus_ids:
                if corpus_id not in self.file_reports:
                    print(f"[ERROR] Corpus {corpus_id} not found in file_reports")
                    continue
                    
                # Get the corpus report and add its file reports to all_file_reports
                corpus_report = self.file_reports[corpus_id]
                print(f"[DEBUG] Processing corpus report for {corpus_id}, keys: {list(corpus_report.keys())}")
                
                # Add all file reports except Master Report
                for file_key, file_report in corpus_report.items():
                    if file_key != "Master Report":
                        all_file_reports[file_key] = file_report
            
            # Compute BO scores using all file reports
            if all_file_reports:
                bon1_dict, bon2_dict = compute_bo_scores(all_file_reports)
                
                # Sort descending by score
                self.bon1_data = sorted(bon1_dict.items(), key=lambda x: x[1], reverse=True)
                self.bon2_data = sorted(bon2_dict.items(), key=lambda x: x[1], reverse=True)
                
                print(f"[DEBUG] BOScoreTable calculated {len(self.bon1_data)} BOn1 scores and {len(self.bon2_data)} BOn2 scores for corpus: {self.corpus_ids}")
            else:
                print(f"[ERROR] No file reports found for corpus: {self.corpus_ids}")
                self.bon1_data = []
                self.bon2_data = []
                
        except Exception as e:
            print(f"[ERROR BOScoreTableVisualization] compute_bo_scores failed for corpus {self.corpus_ids}: {e}")
            import traceback
            traceback.print_exc()
            self.bon1_data = []
            self.bon2_data = []

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