# dashboard_controller.py

from ui.dashboard_ui import DashboardWindow
from config.metric_registry import get_metric, METRICS
from visualizations.cell_factory import create_cell
from model.corpora import Corpus  # Add this import

class DashboardController:
    def __init__(self, main_controller=None):
        self.main_controller = main_controller
        self.view = None
        self.cell_data_map = {}

    def show(self):
        if not self.view:
            self.view = DashboardWindow(controller=self)
            # Ensure the view has access to main_controller
            self.view.main_controller = self.main_controller
        
        # Make sure there's an active corpus if any exist
        if self.main_controller and hasattr(self.main_controller, 'corpora') and self.main_controller.corpora:
            if not self.main_controller.single_active_corpus:
                # Set the first corpus as active
                first_corpus = next(iter(self.main_controller.corpora))
                print(f"[DEBUG] Setting first corpus as active: {first_corpus}")
                self.main_controller.single_active_corpus = first_corpus
                self.main_controller.active_corpus = self.main_controller.corpora[first_corpus]
        
        self.view.show()
        
        # Sync UI with initial corpus state
        if self.view and hasattr(self.view, 'update_corpus_indicators'):
            self.view.update_corpus_indicators()

    def add_corpus(self, corpus_name):
        """Delegate corpus addition to main controller."""
        if self.main_controller and hasattr(self.main_controller, 'add_corpus'):
            self.main_controller.add_corpus(corpus_name)
            if self.view:
                self.view.populate_corpora_tree()
        else:
            print("[ERROR] Cannot add corpus - main controller not available")

    def set_active_corpus(self, corpus_name):
        """Delegate setting active corpus to main controller."""
        if self.main_controller and hasattr(self.main_controller, 'set_active_corpus'):
            self.main_controller.set_active_corpus(corpus_name)
        else:
            print("[ERROR] Cannot set active corpus - main controller not available")

    def add_selected_metric(self, item=None, column=None):
        if not self.view:
            return

        # Retrieve the keys from the selected metric
        category_key, sub_key, sub_sub_key = self.view.get_selected_metric_keys()
        if category_key is None or sub_key is None:
            print("[ERROR] Invalid keys selected.")
            return

        # Retrieve the correct metric data using get_metric
        metric_data = get_metric(category_key, sub_key, sub_sub_key)

        if not metric_data:
            print(f"[ERROR] Metric data not found for keys: category_key={category_key}, sub_key={sub_key}, sub_sub_key={sub_sub_key}")
            return

        # Get visualization type and other attributes
        visualization_type = metric_data.get("visualization_type")
        metric_name = metric_data.get("name")
        initial_mode = metric_data.get("initial_mode", "nominal")

        # Debugging
        print(f"[DEBUG] Visualization Type: {visualization_type}")
        print(f"[DEBUG] Metric Name: {metric_name}")
        print(f"[DEBUG] Selected Keys: category_key={category_key}, sub_key={sub_key}, sub_sub_key={sub_sub_key}")

        if not visualization_type:
            print("[ERROR] Visualization type is missing.")
            return

        # Get active corpus ID for anchoring - use the single active corpus
        corpus_id = None
        if hasattr(self.main_controller, 'single_active_corpus') and self.main_controller.single_active_corpus:
            corpus_id = self.main_controller.single_active_corpus
            print(f"[DEBUG] Adding metric for single active corpus: {corpus_id}")
        else:
            print("[ERROR] No single active corpus is set. Cannot create visualization.")
            return
            
        # Always generate a fresh report for this corpus
        print(f"[DEBUG] Generating fresh report for {corpus_id}")
        success = self.main_controller.generate_report_for_corpus(corpus_id)
        if not success:
            print(f"[ERROR] Failed to generate report for corpus: {corpus_id}")
            return

        # Create the cell widget with corpus ID
        cell_widget = create_cell(
            self.main_controller,  # Pass controller instead of file_reports
            category_key,
            sub_key,
            sub_sub_key=sub_sub_key, 
            initial_mode=initial_mode,
            corpus_id=corpus_id     # Pass corpus identifier
        )

        if cell_widget:
            # Add the cell to the view
            cell = self.view.add_cell(metric_name, cell_widget)
            # Connect the refresh signal from the cell to the new refresh_cell method
            if hasattr(cell, 'refresh_requested'):
                cell.refresh_requested.connect(lambda: self.refresh_cell(cell))
            
            # Store metadata including corpus_id
            self.cell_data_map[cell] = {
                "category_key": category_key,
                "sub_key": sub_key,
                "sub_sub_key": sub_sub_key,
                "name": metric_name,
                "initial_mode": initial_mode,
                "corpus_id": corpus_id  # Store corpus ID in metadata
            }
            print(f"[DEBUG] Metric cell added for {metric_name} (corpus: {corpus_id}).")
        else:
            print("[ERROR] Cell widget creation failed.")

    def refresh_cell(self, cell):
        """Refresh a cell's data from its specific anchored corpus."""
        if cell in self.cell_data_map:
            metadata = self.cell_data_map[cell]
            corpus_id = metadata.get("corpus_id")
            
            if corpus_id and self.main_controller:
                print(f"[DEBUG] Refreshing cell for anchored corpus: {corpus_id}")
                
                # Generate fresh report for this specific corpus if needed
                if not self.main_controller.report_manager.has_report_for_corpus(corpus_id):
                    self.main_controller.generate_report_for_corpus(corpus_id)
                
                # Get the report for this corpus
                report = self.main_controller.report_manager.get_report_for_corpus(corpus_id)
                
                # Retrieve visualization instance stored in cell.stored_content
                vis_instance = getattr(cell, 'stored_content', None)
                if vis_instance is not None:
                    # Update the visualization with fresh data
                    if hasattr(vis_instance, 'update_data'):
                        vis_instance.update_data(report)
                    elif hasattr(vis_instance, 'update_data_source'):
                        vis_instance.update_data_source()
                        if hasattr(vis_instance, 'update_plot'):
                            vis_instance.update_plot()
                    else:
                        print("[WARNING] Visualization lacks update methods")
                    print(f"[DEBUG] Refreshed cell '{getattr(cell, 'title', 'unknown')}' with updated data.")
                else:
                    print("[DEBUG] No visualization instance found in cell for refresh.")
            else:
                print(f"[ERROR] No corpus_id for cell {metadata.get('name', 'unknown')}")
        else:
            print("[ERROR] Cell not found in data map")

    def remove_metric_cell(self, metric_name):
        """
        Remove the specified metric cell by its name.
        """
        if self.view:
            self.view.remove_cell_by_name(metric_name)

    def duplicate_metric_cell(self, metric_name, cell):
        """Handle duplicate requests for a metric cell."""
        if cell not in self.cell_data_map:
            print(f"[ERROR] No metadata found for cell: {metric_name}")
            return

        metadata = self.cell_data_map[cell]
        category_key = metadata["category_key"]
        sub_key = metadata["sub_key"]
        sub_sub_key = metadata["sub_sub_key"]
        visualization_type = metadata.get("visualization_type")  # If available in metadata
        initial_mode = metadata["initial_mode"]

        # Debug
        print(f"[DEBUG] Duplicating metric cell: {metric_name}")
        print(f"[DEBUG] Metadata: {metadata}")

        # Create a new cell widget using the existing metadata
        file_reports = self.main_controller.file_reports
        new_cell_widget = create_cell(
            file_reports,
            category_key,
            sub_key,
            sub_sub_key=sub_sub_key,
            initial_mode=initial_mode
        )

        if new_cell_widget:
            new_cell = self.view.add_cell(metric_name, new_cell_widget)

            # Connect signals for the new cell
            new_cell.remove_requested.connect(lambda title=new_cell.title: self.remove_metric_cell_instance(new_cell))
            new_cell.duplicate_requested.connect(lambda: self.duplicate_metric_cell(metric_name, new_cell))
            new_cell.move_up_requested.connect(lambda: self.move_metric_cell_up(new_cell))
            new_cell.move_down_requested.connect(lambda: self.move_metric_cell_down(new_cell))
            # Connect the refresh signal to the new refresh_cell method
            if hasattr(new_cell, 'refresh_requested'):
                new_cell.refresh_requested.connect(lambda: self.refresh_cell(new_cell))

            # Store metadata for the new cell
            self.cell_data_map[new_cell] = metadata.copy()
            print(f"[DEBUG] Metric cell duplicated for {metric_name}.")
        else:
            print("[ERROR] Failed to duplicate metric cell.")

    def move_metric_cell_up(self, cell):
        """
        Move the specified cell up in the dashboard notebook.
        """
        if self.view:
            self.view.move_cell_up(cell)

    def move_metric_cell_down(self, cell):
        """
        Move the specified cell down in the dashboard notebook.
        """
        if self.view:
            self.view.move_cell_down(cell)
    
    def remove_metric_cell_instance(self, cell):
        if cell in self.cell_data_map:
            del self.cell_data_map[cell]  # Remove cell from the map
        if self.view:
            self.view.notebook_layout.removeWidget(cell)  # Remove cell from the layout
            cell.setParent(None)  # Detach from the parent
            cell.deleteLater()  # Schedule for deletion

    def refresh_visualizations(self):
        """Refresh all visualization cells with their anchored corpus data."""
        if self.view:
            # Store current cell configurations
            cell_configs = []
            for i in range(self.view.notebook_layout.count()):
                cell = self.view.notebook_layout.itemAt(i).widget()
                if cell and cell in self.cell_data_map:
                    cell_configs.append(self.cell_data_map[cell])
            
            # Clear existing cells
            while self.view.notebook_layout.count():
                item = self.view.notebook_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            # Recreate cells with new data, respecting their corpus anchors
            for config in cell_configs:
                # Get corpus_id from the cell metadata
                corpus_id = config.get("corpus_id")
                
                # If this cell has a corpus_id, ensure we have fresh data for it
                if corpus_id and hasattr(self.main_controller, 'generate_report_for_corpus'):
                    self.main_controller.generate_report_for_corpus(corpus_id)
                
                cell_widget = create_cell(
                    self.main_controller,
                    config["category_key"],
                    config["sub_key"],
                    sub_sub_key=config.get("sub_sub_key"),
                    initial_mode=config.get("initial_mode", "nominal"),
                    corpus_id=corpus_id  # Pass corpus_id when recreating the cell
                )
                if cell_widget:
                    cell = self.view.add_cell(config.get("name", "Metric"), cell_widget)
                    self.cell_data_map[cell] = config
                    print(f"[DEBUG] Recreated cell for {config.get('name')} anchored to corpus: {corpus_id}")
                else:
                    print(f"[ERROR] Failed to recreate cell for {config.get('name')}")


