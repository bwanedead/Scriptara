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
    def __init__(self, controller=None, corpus_ids=None, initial_mode=None):
        self.controller = controller  # Reference to controller to access reports
        self.corpus_ids = corpus_ids if corpus_ids is not None else []  # List of corpus IDs
        self.initial_mode = initial_mode
        self.file_reports = {}  # Persistent cache
        
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


class FrequencyDistributionVisualization(BaseVisualization):
    def __init__(self, controller=None, initial_mode='nominal', corpus_ids=None):
        super().__init__(controller, corpus_ids, initial_mode)
        print(f"[DEBUG] Initializing FrequencyDistributionVisualization for corpus_ids: {corpus_ids}")
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
        print(f"[DEBUG] Getting values for mode: {mode} using corpus: {self.corpus_ids[0] if self.corpus_ids else None}")
        col = self.mode_map.get(mode, 1)
        data_sets = {}
        
        # VERIFY WE HAVE DATA
        if not self.file_reports:
            print(f"[ERROR] No file_reports data available for corpus: {self.corpus_ids[0] if self.corpus_ids else None}")
            return data_sets
                
        # Show what reports we have
        print(f"[DEBUG] Available reports for corpus {self.corpus_ids}: {list(self.file_reports.keys())}")
        
        # Process each corpus in corpus_ids
        for corpus_id in self.corpus_ids:
            if corpus_id not in self.file_reports:
                print(f"[ERROR] Corpus {corpus_id} not found in file_reports")
                continue
                
            # Get the corpus report
            corpus_report = self.file_reports[corpus_id]
            print(f"[DEBUG] Processing corpus report for {corpus_id}, keys: {list(corpus_report.keys())}")
            
            # Iterate through file reports in this corpus
            for file_key, file_report in corpus_report.items():
                # Skip Master Report
                if file_key == "Master Report":
                    continue
                    
                if 'data' not in file_report:
                    print(f"[ERROR] No 'data' key in file report: {file_key}")
                    continue
                    
                if 'word_stats' not in file_report['data']:
                    print(f"[ERROR] No 'word_stats' key in file report data: {file_key}")
                    continue
                    
                stats = file_report['data']['word_stats']
                if not stats:
                    print(f"[WARNING] Empty word_stats for {file_key}")
                    continue
                    
                ranks = range(1, len(stats) + 1)
                vals = [s[col] for s in stats]
                # Use corpus_id + file_key as the dataset name for clarity
                dataset_name = f"{corpus_id}: {os.path.basename(file_key)}"
                data_sets[dataset_name] = (list(ranks), vals)
                print(f"[DEBUG] Processed {file_key} for corpus {corpus_id}: {len(vals)} values")
            
        print(f"[DEBUG] Returning {len(data_sets)} datasets for {self.corpus_ids}")
        return data_sets

    def update_plot(self):
        # First update the data source
        self.update_data_source()
        
        print(f"[DEBUG] Starting plot update for corpus: {self.corpus_ids}")
        self.plot_widget.clear()
        data = self.get_values(self.current_mode)

        if not data:
            print(f"[DEBUG] No data available to plot for corpus: {self.corpus_ids}")
            return

        print(f"[DEBUG] Plotting {len(data)} datasets for corpus: {self.corpus_ids}")
        colors = [
            (102, 153, 255), (102, 255, 178), (255, 204, 102),
            (255, 102, 178), (178, 102, 255), (102, 255, 255), (255, 178, 102)
        ]

        for i, (rep, (ranks, vals)) in enumerate(data.items()):
            c = colors[i % len(colors)]
            pen = pg.mkPen(color=c, width=1.5)
            self.plot_widget.plot(ranks, vals, pen=pen, name=rep, clear=False)
            print(f"[DEBUG] Plotted dataset {i+1} for corpus: {self.corpus_ids}")

        self.plot_widget.getPlotItem().setLogMode(x=self.x_log, y=self.y_log)
        self.plot_widget.getPlotItem().enableAutoRange()
        self.plot_widget.getPlotItem().autoRange()

        # Force update
        self.plot_widget.update()
        self.plot_widget.repaint()
        QApplication.processEvents()
        print(f"[DEBUG] Plot update complete for corpus: {self.corpus_ids}")


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