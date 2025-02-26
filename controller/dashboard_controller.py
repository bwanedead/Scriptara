# dashboard_controller.py

from ui.dashboard_ui import DashboardWindow
from config.metric_registry import get_metric, METRICS
from visualizations.cell_factory import create_cell
from model.corpora import Corpus  # Add this import

class DashboardController:
    def __init__(self, main_controller=None):
        print(f"[DEBUG] DashboardController.__init__ called with main_controller={main_controller is not None}")
        self.main_controller = main_controller
        self.view = None
        self.cell_data_map = {}

    def show(self):
        print(f"[DEBUG] DashboardController.show() called, view exists: {self.view is not None}")
        if not self.view:
            print(f"[DEBUG] Creating new DashboardWindow instance")
            self.view = DashboardWindow(controller=self)
            # Ensure the view has access to main_controller
            self.view.main_controller = self.main_controller
            print(f"[DEBUG] Set view.main_controller reference: {self.view.main_controller is not None}")
        else:
            print(f"[DEBUG] Using existing DashboardWindow instance")
        self.view.show()

    def add_corpus(self, corpus_name):
        """Delegate corpus addition to main controller."""
        if self.main_controller and hasattr(self.main_controller, 'add_corpus'):
            self.main_controller.add_corpus(corpus_name)
            if self.view:
                self.view.populate_corpora_tree()
        else:
            print("[ERROR] Cannot add corpus - main controller not available")

    def set_active_corpus(self, corpus_name):
        """Set the active corpus and delegate to main controller."""
        print(f"[DEBUG] Dashboard controller setting active corpus to: {corpus_name}")
        if self.main_controller and hasattr(self.main_controller, 'set_active_corpus'):
            self.main_controller.set_active_corpus(corpus_name)
            print(f"[DEBUG] Called main_controller.set_active_corpus({corpus_name})")
            # Update UI after change
            if self.view:
                self.view.update_selection_indicators()
                print(f"[DEBUG] Called view.update_selection_indicators()")
        else:
            print(f"[ERROR] Cannot set active corpus - main_controller={self.main_controller is not None}, has_set_active_corpus={hasattr(self.main_controller, 'set_active_corpus') if self.main_controller else False}")

    def toggle_multi_corpus(self, corpus_name):
        """Toggle corpus for multi-corpus metrics."""
        print(f"[DEBUG] DashboardController.toggle_multi_corpus called with corpus_name={corpus_name}")
        if self.main_controller and hasattr(self.main_controller, 'toggle_multi_corpus'):
            self.main_controller.toggle_multi_corpus(corpus_name)
            # Update UI after change
            if self.view:
                self.view.update_selection_indicators()
        else:
            print(f"[DEBUG] Cannot toggle multi-corpus - main_controller={self.main_controller is not None}, has_toggle_multi_corpus={hasattr(self.main_controller, 'toggle_multi_corpus') if self.main_controller else False}")
            
    def get_active_corpus_name(self):
        """Get the name of the active corpus."""
        if self.main_controller and hasattr(self.main_controller, 'active_corpus') and self.main_controller.active_corpus:
            return self.main_controller.active_corpus.name
        return None
    
    def get_multi_corpora(self):
        """Get list of corpora selected for multi-corpus metrics."""
        if self.main_controller and hasattr(self.main_controller, 'selected_corpora'):
            return self.main_controller.selected_corpora
        return []

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

        # Create the cell widget using all keys
        file_reports = self.main_controller.file_reports
        cell_widget = create_cell(
            file_reports, 
            category_key, 
            sub_key, 
            sub_sub_key=sub_sub_key,
            initial_mode=initial_mode
        )

        if cell_widget:
            # Add the cell to the view
            cell = self.view.add_cell(metric_name, cell_widget)
            # Connect the refresh signal from the cell to the new refresh_cell method
            if hasattr(cell, 'refresh_requested'):
                cell.refresh_requested.connect(lambda: self.refresh_cell(cell))
            self.cell_data_map[cell] = {
                "category_key": category_key,
                "sub_key": sub_key,
                "sub_sub_key": sub_sub_key,
                "name": metric_name,
                "initial_mode": initial_mode
            }
            print(f"[DEBUG] Metric cell added for {metric_name}.")
        else:
            print("[ERROR] Cell widget creation failed.")

    def refresh_cell(self, cell):
        """Refresh a cell's data from the current analysis."""
        # Re-run analysis to update file_reports
        if self.main_controller:
            self.main_controller.run_analysis()
            # Retrieve visualization instance stored in cell.stored_content
            vis_instance = getattr(cell, 'stored_content', None)
            if vis_instance is not None:
                # Update the file_reports attribute
                vis_instance.file_reports = self.main_controller.file_reports
                # Redraw the plot using the visualization's update method
                vis_instance.update_plot()
                print(f"[DEBUG] Refreshed cell '{getattr(cell, 'title', 'unknown')}' with updated data.")
            else:
                print("[DEBUG] No visualization instance found in cell for refresh.")

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
        """Refresh all visualization cells with new data."""
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
            
            # Recreate cells with new data
            for config in cell_configs:
                cell_widget = create_cell(
                    self.main_controller.file_reports,
                    config["category_key"],
                    config["sub_key"],
                    sub_sub_key=config.get("sub_sub_key"),
                    initial_mode=config.get("initial_mode", "nominal")
                )
                if cell_widget:
                    cell = self.view.add_cell(config.get("name", "Metric"), cell_widget)
                    self.cell_data_map[cell] = config

    def rename_corpus(self, old_name, new_name):
        """Delegate corpus renaming to main controller."""
        print(f"[DEBUG] DashboardController.rename_corpus called with old_name={old_name}, new_name={new_name}")
        
        if self.main_controller and hasattr(self.main_controller, 'rename_corpus'):
            print(f"[DEBUG] Delegating rename_corpus to main_controller")
            self.main_controller.rename_corpus(old_name, new_name)
            
            # Update UI after renaming
            if self.view:
                print(f"[DEBUG] Updating dashboard UI after rename")
                self.view.populate_corpora_tree()
                print(f"[DEBUG] Dashboard updated after renaming corpus")
            else:
                print(f"[DEBUG] Cannot update dashboard UI - view not available")
        else:
            print(f"[DEBUG] Cannot rename corpus - main_controller={self.main_controller is not None}, has_rename_corpus={hasattr(self.main_controller, 'rename_corpus') if self.main_controller else False}")


