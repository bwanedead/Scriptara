# metric_visualizations.py
import os
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidgetItem
from PyQt5.QtCore import Qt
import logging
import numpy as np
from analysis.advanced_analysis import compute_bo_scores

class BaseVisualization:
    """
    Base class for all visualizations that handles corpus-specific report fetching.
    All visualization classes should inherit from this class.
    """
    def __init__(self, controller=None, corpus_id=None, initial_mode=None):
        self.controller = controller  # Reference to controller to access reports
        self.corpus_id = corpus_id    # Which corpus this visualization belongs to 
        self.initial_mode = initial_mode
        self.file_reports = {}
        
        print(f"[DEBUG] BaseVisualization init with corpus_id: {corpus_id}")
        # Initialize with the appropriate data
        self.update_data_source()
        
    def update_data_source(self):
        """Update the data source based on corpus_id"""
        # Always start with empty reports to avoid stale data
        self.file_reports = {}
        
        if not self.controller:
            print("[ERROR] BaseViz has no controller reference")
            return
            
        if not self.corpus_id:
            print("[ERROR] BaseViz has no corpus_id")
            return
            
        if not hasattr(self.controller, 'get_report_for_corpus'):
            print("[ERROR] BaseViz controller lacks get_report_for_corpus method")
            return
            
        # Check if report exists and generate if needed
        if hasattr(self.controller, 'has_report_for_corpus'):
            has_report = self.controller.has_report_for_corpus(self.corpus_id)
            print(f"[DEBUG] BaseViz checking if report exists for {self.corpus_id}: {has_report}")
            
            if not has_report:
                print(f"[DEBUG] BaseViz generating initial report for corpus: {self.corpus_id}")
                success = self.controller.generate_report_for_corpus(self.corpus_id)
                if not success:
                    print(f"[ERROR] Failed to generate report for corpus: {self.corpus_id}")
                    return
                print(f"[DEBUG] BaseViz report generation success: {success}")
        else:
            # If has_report_for_corpus doesn't exist, always try to generate
            print(f"[DEBUG] BaseViz generating report for corpus (no has_report method): {self.corpus_id}")
            self.controller.generate_report_for_corpus(self.corpus_id)
            
        # Get corpus-specific data
        self.file_reports = self.controller.get_report_for_corpus(self.corpus_id)
        
        # Verify we got data
        if not self.file_reports:
            print(f"[ERROR] BaseViz got empty report for corpus: {self.corpus_id}")
            self.debug_report_access()
        else:
            print(f"[DEBUG] BaseViz fetched report for corpus: {self.corpus_id}, keys: {list(self.file_reports.keys())}")
    
    def debug_report_access(self):
        """Debug report access issues"""
        print(f"[DEBUG] Debugging report access for corpus: {self.corpus_id}")
        
        if not self.controller:
            print("[ERROR] No controller reference")
            return
            
        if not self.corpus_id:
            print("[ERROR] No corpus_id")
            return
            
        # Check if the corpus exists
        if hasattr(self.controller, 'corpora'):
            if self.corpus_id in self.controller.corpora:
                print(f"[DEBUG] Corpus '{self.corpus_id}' exists in controller.corpora")
                corpus = self.controller.corpora[self.corpus_id]
                print(f"[DEBUG] Corpus '{self.corpus_id}' has {len(corpus.get_files())} files")
            else:
                print(f"[ERROR] Corpus '{self.corpus_id}' does not exist in controller.corpora")
                print(f"[DEBUG] Available corpora: {list(self.controller.corpora.keys())}")
        else:
            print("[ERROR] Controller has no corpora attribute")
            
        # Check if the report manager exists
        if hasattr(self.controller, 'report_manager'):
            print("[DEBUG] Controller has report_manager")
            
            # Check if the report manager has the report
            if hasattr(self.controller.report_manager, 'has_report_for_corpus'):
                has_report = self.controller.report_manager.has_report_for_corpus(self.corpus_id)
                print(f"[DEBUG] Report manager has_report_for_corpus('{self.corpus_id}'): {has_report}")
                
                if has_report:
                    # Check the report content
                    report = self.controller.report_manager.get_report_for_corpus(self.corpus_id)
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
                    print(f"[DEBUG] Attempting to generate report for corpus: {self.corpus_id}")
                    if hasattr(self.controller, 'generate_report_for_corpus'):
                        success = self.controller.generate_report_for_corpus(self.corpus_id)
                        print(f"[DEBUG] generate_report_for_corpus result: {success}")
                        
                        # Check if the report was generated
                        has_report = self.controller.report_manager.has_report_for_corpus(self.corpus_id)
                        print(f"[DEBUG] After generation, has_report_for_corpus('{self.corpus_id}'): {has_report}")
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


class FrequencyDistributionVisualization(BaseVisualization):
    def __init__(self, controller=None, initial_mode='nominal', corpus_id=None):
        super().__init__(controller, corpus_id, initial_mode)
        print(f"[DEBUG] Initializing FrequencyDistributionVisualization for corpus: {corpus_id}")
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
        print(f"[DEBUG] Getting values for mode: {mode} using corpus: {self.corpus_id}")
        col = self.mode_map.get(mode, 1)
        data_sets = {}
        
        # VERIFY WE HAVE DATA
        if not self.file_reports:
            print(f"[ERROR] No file_reports data available for corpus: {self.corpus_id}")
            return data_sets
                
        # Show what reports we have
        print(f"[DEBUG] Available reports for corpus {self.corpus_id}: {list(self.file_reports.keys())}")
        
        # Use the corpus-specific data
        for rep_key, rep_data in self.file_reports.items():
            if rep_key == "Master Report":
                continue
                
            if 'data' not in rep_data:
                print(f"[ERROR] No 'data' key in report: {rep_key}")
                continue
                
            if 'word_stats' not in rep_data['data']:
                print(f"[ERROR] No 'word_stats' key in report data: {rep_key}")
                continue
                
            stats = rep_data['data']['word_stats']
            if not stats:
                print(f"[WARNING] Empty word_stats for {rep_key}")
                continue
                
            ranks = range(1, len(stats) + 1)
            vals = [s[col] for s in stats]
            data_sets[rep_key] = (list(ranks), vals)
            print(f"[DEBUG] Processed {rep_key} for corpus {self.corpus_id}: {len(vals)} values")
            
        print(f"[DEBUG] Returning {len(data_sets)} datasets for {self.corpus_id}")
        return data_sets

    def update_plot(self):
        # First update the data source
        self.update_data_source()
        
        print(f"[DEBUG] Starting plot update for corpus: {self.corpus_id}")
        self.plot_widget.clear()
        data = self.get_values(self.current_mode)

        if not data:
            print(f"[DEBUG] No data available to plot for corpus: {self.corpus_id}")
            return

        print(f"[DEBUG] Plotting {len(data)} datasets for corpus: {self.corpus_id}")
        colors = [
            (102, 153, 255), (102, 255, 178), (255, 204, 102),
            (255, 102, 178), (178, 102, 255), (102, 255, 255), (255, 178, 102)
        ]

        for i, (rep, (ranks, vals)) in enumerate(data.items()):
            c = colors[i % len(colors)]
            pen = pg.mkPen(color=c, width=1.5)
            self.plot_widget.plot(ranks, vals, pen=pen, name=rep, clear=False)
            print(f"[DEBUG] Plotted dataset {i+1} for corpus: {self.corpus_id}")

        self.plot_widget.getPlotItem().setLogMode(x=self.x_log, y=self.y_log)
        self.plot_widget.getPlotItem().enableAutoRange()
        self.plot_widget.getPlotItem().autoRange()

        # Force update
        self.plot_widget.update()
        self.plot_widget.repaint()
        QApplication.processEvents()
        print(f"[DEBUG] Plot update complete for corpus: {self.corpus_id}")


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

    def __init__(self, controller=None, initial_mode=None, corpus_id=None):
        super().__init__(controller, corpus_id, initial_mode)
        self.bon1_data = []
        self.bon2_data = []
        
        print(f"[DEBUG] BOScoreBarVisualization initialized with corpus_id: {corpus_id}")
        # Update data based on corpus_id
        self.update_data()
        
    def update_data(self):
        """Update data using the appropriate corpus report"""
        try:
            # First ensure we have the latest data
            self.update_data_source()
            
            # Verify we have data
            if not self.file_reports:
                print(f"[ERROR] BOScoreBar has no data for corpus: {self.corpus_id}")
                self.bon1_data = []
                self.bon2_data = []
                return
                
            # Compute BO scores
            bon1_dict, bon2_dict = compute_bo_scores(self.file_reports)
            
            # Sort descending by score
            self.bon1_data = sorted(bon1_dict.items(), key=lambda x: x[1], reverse=True)
            self.bon2_data = sorted(bon2_dict.items(), key=lambda x: x[1], reverse=True)
            
            print(f"[DEBUG] BOScoreBar calculated {len(self.bon1_data)} BOn1 scores and {len(self.bon2_data)} BOn2 scores for corpus: {self.corpus_id}")

        except Exception as e:
            print(f"[ERROR BOScoreBarVisualization] compute_bo_scores failed for corpus {self.corpus_id}: {e}")
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
    def __init__(self, controller=None, initial_mode=None, corpus_id=None):
        super().__init__(controller, corpus_id, initial_mode)
        self.bon1_data = []
        self.bon2_data = []
        
        print(f"[DEBUG] BOScoreLineVisualization initialized with corpus_id: {corpus_id}")
        # Update data based on corpus_id
        self.update_data()
        
    def update_data(self):
        """Update data using the appropriate corpus report"""
        try:
            # First ensure we have the latest data
            self.update_data_source()
            
            # Verify we have data
            if not self.file_reports:
                print(f"[ERROR] BOScoreLine has no data for corpus: {self.corpus_id}")
                self.bon1_data = []
                self.bon2_data = []
                return
                
            # Compute BO scores
            bon1_dict, bon2_dict = compute_bo_scores(self.file_reports)
            
            # Sort descending by score
            self.bon1_data = sorted(bon1_dict.items(), key=lambda x: x[1], reverse=True)
            self.bon2_data = sorted(bon2_dict.items(), key=lambda x: x[1], reverse=True)
            
            print(f"[DEBUG] BOScoreLine calculated {len(self.bon1_data)} BOn1 scores and {len(self.bon2_data)} BOn2 scores for corpus: {self.corpus_id}")
        except Exception as e:
            print(f"[ERROR BOScoreLineVisualization] compute_bo_scores failed for corpus {self.corpus_id}: {e}")
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
    def __init__(self, controller=None, initial_mode=None, corpus_id=None):
        super().__init__(controller, corpus_id, initial_mode)
        self.bon1_data = []
        self.bon2_data = []
        
        print(f"[DEBUG] BOScoreTableVisualization initialized with corpus_id: {corpus_id}")
        # Update data based on corpus_id
        self.update_data()
        
    def update_data(self):
        """Update data using the appropriate corpus report"""
        try:
            # First ensure we have the latest data
            self.update_data_source()
            
            # Verify we have data
            if not self.file_reports:
                print(f"[ERROR] BOScoreTable has no data for corpus: {self.corpus_id}")
                self.bon1_data = []
                self.bon2_data = []
                return
                
            # Compute BO scores
            bon1_dict, bon2_dict = compute_bo_scores(self.file_reports)
            
            # Sort descending by score
            self.bon1_data = sorted(bon1_dict.items(), key=lambda x: x[1], reverse=True)
            self.bon2_data = sorted(bon2_dict.items(), key=lambda x: x[1], reverse=True)
            
            print(f"[DEBUG] BOScoreTable calculated {len(self.bon1_data)} BOn1 scores and {len(self.bon2_data)} BOn2 scores for corpus: {self.corpus_id}")
        except Exception as e:
            print(f"[ERROR BOScoreTableVisualization] compute_bo_scores failed for corpus {self.corpus_id}: {e}")
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