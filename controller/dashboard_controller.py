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

    def rename_corpus(self, old_name, new_name):
        """
        Handle corpus renaming through the main controller.
        Updates all cell references to the renamed corpus.
        
        Args:
            old_name: The current name of the corpus
            new_name: The new name to assign to the corpus
            
        Returns:
            bool: Success or failure of the rename operation
        """
        if not self.main_controller:
            print("[ERROR] Cannot rename corpus - main controller not available")
            return False
            
        # Check if main controller has the rename_corpus method
        if not hasattr(self.main_controller, 'rename_corpus'):
            # If not available, we'll implement the rename logic here
            print("[INFO] Implementing corpus rename in dashboard controller")
            
            # Check if corpus exists
            if old_name not in self.main_controller.corpora:
                print(f"[ERROR] Cannot rename corpus - '{old_name}' not found")
                return False
                
            # Check if target name already exists
            if new_name in self.main_controller.corpora:
                print(f"[ERROR] Cannot rename corpus - '{new_name}' already exists")
                return False
                
            # Get the corpus object
            corpus = self.main_controller.corpora[old_name]
            
            # Update the corpus name
            corpus.name = new_name
            
            # Update corpora dictionary
            self.main_controller.corpora[new_name] = corpus
            del self.main_controller.corpora[old_name]
            
            # Update active corpus references if needed
            if hasattr(self.main_controller, 'single_active_corpus') and self.main_controller.single_active_corpus == old_name:
                self.main_controller.single_active_corpus = new_name
                print(f"[DEBUG] Updated single active corpus reference to {new_name}")
            
            if hasattr(self.main_controller, 'multi_active_corpora') and old_name in self.main_controller.multi_active_corpora:
                self.main_controller.multi_active_corpora.remove(old_name)
                self.main_controller.multi_active_corpora.add(new_name)
                print(f"[DEBUG] Updated multi active corpus reference to {new_name}")
                
            if hasattr(self.main_controller, 'active_corpus') and self.main_controller.active_corpus == corpus:
                self.main_controller.active_corpus = corpus
                print(f"[DEBUG] Updated active corpus object reference")
            
            # Update any cell references to this corpus
            self.update_cell_corpus_references(old_name, new_name)
            
            print(f"[INFO] Successfully renamed corpus from '{old_name}' to '{new_name}'")
            return True
        else:
            # If main controller has rename_corpus method, use it
            success = self.main_controller.rename_corpus(old_name, new_name)
            if success:
                # Update references in dashboard controller cells
                self.update_cell_corpus_references(old_name, new_name)
            return success
    
    def update_cell_corpus_references(self, old_name, new_name):
        """
        Update all cell references from the old corpus name to the new one.
        
        Args:
            old_name: Previous corpus name
            new_name: New corpus name
        """
        cells_updated = 0
        for cell, metadata in self.cell_data_map.items():
            if metadata.get("corpus_id") == old_name:
                # Update the metadata
                metadata["corpus_id"] = new_name
                cells_updated += 1
                
                # If refresh_cell is available, refresh the cell
                if hasattr(self, 'refresh_cell'):
                    self.refresh_cell(cell)
                    
        print(f"[DEBUG] Updated {cells_updated} cell references from '{old_name}' to '{new_name}'")

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
            
        # Check if report exists for this corpus - compute only if needed (lazy loading)
        if hasattr(self.main_controller, 'report_manager') and not self.main_controller.report_manager.has_report_for_corpus(corpus_id):
            print(f"[DEBUG] Generating initial report for {corpus_id}")
            success = self.main_controller.generate_report_for_corpus(corpus_id)
            if not success:
                print(f"[ERROR] Failed to generate report for corpus: {corpus_id}")
                return
        else:
            print(f"[DEBUG] Using existing report for {corpus_id}")

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
            
            # Store metadata including corpus_id
            self.cell_data_map[cell] = {
                "category_key": category_key,
                "sub_key": sub_key,
                "sub_sub_key": sub_sub_key,
                "name": metric_name,
                "initial_mode": initial_mode,
                "corpus_id": corpus_id  # Store corpus ID in metadata
            }
            
            # Connect all the cell signals to their respective handlers
            if hasattr(cell, 'refresh_requested'):
                cell.refresh_requested.connect(lambda: self.refresh_cell(cell))
                print(f"[DEBUG] Connected cell refresh signal")
                
            # Connect the action signals
            cell.remove_requested.connect(lambda title: self.remove_metric_cell(title))
            cell.move_up_requested.connect(lambda title: self.move_cell_up_by_name(title))
            cell.move_down_requested.connect(lambda title: self.move_cell_down_by_name(title))
            cell.duplicate_requested.connect(lambda title: self.duplicate_metric_cell_by_name(title))
                
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
                
                # Check if report exists before generating - lazy refresh
                if hasattr(self.main_controller, 'has_report_for_corpus') and not self.main_controller.has_report_for_corpus(corpus_id):
                    print(f"[DEBUG] Generating fresh report for {corpus_id} during refresh")
                    self.main_controller.generate_report_for_corpus(corpus_id)
                else:
                    print(f"[DEBUG] Using existing report for {corpus_id} during refresh")
                
                # Retrieve the layout widget stored in cell.stored_content
                layout_widget = getattr(cell, 'stored_content', None)
                if layout_widget is not None:
                    print(f"[DEBUG] Found layout widget: {type(layout_widget).__name__}")
                    
                    # Try to access the visualization directly from layout widget
                    vis_instance = getattr(layout_widget, 'vis', None)
                    if vis_instance is not None:
                        # Update the visualization with fresh data
                        print(f"[DEBUG] Found visualization instance: {type(vis_instance).__name__}")
                        
                        # Universal approach - try all update methods in sequence
                        if hasattr(vis_instance, 'update_data_source'):
                            vis_instance.update_data_source()
                            print(f"[DEBUG] Called update_data_source on visualization")
                            
                        if hasattr(vis_instance, 'update_data'):
                            vis_instance.update_data()
                            print(f"[DEBUG] Called update_data on visualization")
                            
                        if hasattr(vis_instance, 'update_plot'):
                            vis_instance.update_plot()
                            print(f"[DEBUG] Called update_plot on visualization")
                            
                        print(f"[DEBUG] Refreshed cell '{getattr(cell, 'title', 'unknown')}' with data from corpus {corpus_id}")
                    else:
                        # Try refreshing the layout directly if it has a refresh method
                        if hasattr(layout_widget, 'refresh'):
                            print(f"[DEBUG] Layout has refresh method, calling it directly")
                            layout_widget.refresh()
                            print(f"[DEBUG] Refreshed layout directly for corpus {corpus_id}")
                        else:
                            print(f"[WARNING] Cannot find visualization instance or refresh method")
                else:
                    print("[DEBUG] No layout widget found in cell")
            else:
                print(f"[ERROR] No corpus_id for cell {metadata.get('name', 'unknown')}")
        else:
            print("[ERROR] Cell not found in data map")

    def remove_metric_cell(self, metric_name):
        """
        Remove the specified metric cell by its name.
        """
        print(f"[DEBUG] Removing metric cell with name: {metric_name}")
        if self.view:
            # Get the cell widget first
            cell = self.view.get_cell_by_name(metric_name)
            if cell:
                # Remove from data map first
                if cell in self.cell_data_map:
                    del self.cell_data_map[cell]
                # Then remove from view
                self.view.remove_cell_by_name(metric_name)
                print(f"[DEBUG] Successfully removed cell: {metric_name}")
            else:
                print(f"[ERROR] Could not find cell with name: {metric_name}")

    def move_cell_up_by_name(self, metric_name):
        """
        Move the cell with the specified name up in the notebook.
        """
        print(f"[DEBUG] Moving up cell with name: {metric_name}")
        if self.view:
            cell = self.view.get_cell_by_name(metric_name)
            if cell:
                self.view.move_cell_up(cell)
                print(f"[DEBUG] Successfully moved up cell: {metric_name}")
            else:
                print(f"[ERROR] Could not find cell with name: {metric_name}")

    def move_cell_down_by_name(self, metric_name):
        """
        Move the cell with the specified name down in the notebook.
        """
        print(f"[DEBUG] Moving down cell with name: {metric_name}")
        if self.view:
            cell = self.view.get_cell_by_name(metric_name)
            if cell:
                self.view.move_cell_down(cell)
                print(f"[DEBUG] Successfully moved down cell: {metric_name}")
            else:
                print(f"[ERROR] Could not find cell with name: {metric_name}")

    def duplicate_metric_cell_by_name(self, metric_name):
        """
        Duplicate the cell with the specified name.
        """
        print(f"[DEBUG] Duplicating cell with name: {metric_name}")
        if self.view:
            original_cell = self.view.get_cell_by_name(metric_name)
            if original_cell and original_cell in self.cell_data_map:
                # Get the metadata for the original cell
                metadata = self.cell_data_map[original_cell]
                
                # Create a new cell with the same parameters
                new_cell_widget = create_cell(
                    self.main_controller,
                    metadata["category_key"],
                    metadata["sub_key"],
                    sub_sub_key=metadata.get("sub_sub_key"),
                    initial_mode=metadata.get("initial_mode", "nominal"),
                    corpus_id=metadata.get("corpus_id")
                )
                
                if new_cell_widget:
                    # Insert the new cell just below the original
                    new_cell = self.view.insert_cell_below(original_cell, metric_name, new_cell_widget)
                    
                    # Connect all signals for the new cell
                    new_cell.remove_requested.connect(lambda title: self.remove_metric_cell(title))
                    new_cell.move_up_requested.connect(lambda title: self.move_cell_up_by_name(title))
                    new_cell.move_down_requested.connect(lambda title: self.move_cell_down_by_name(title))
                    new_cell.duplicate_requested.connect(lambda title: self.duplicate_metric_cell_by_name(title))
                    
                    # Store the metadata for the new cell
                    self.cell_data_map[new_cell] = metadata.copy()
                    
                    print(f"[DEBUG] Successfully duplicated cell: {metric_name}")
                else:
                    print(f"[ERROR] Failed to create new cell widget for duplication")
            else:
                print(f"[ERROR] Could not find cell with name: {metric_name} or it has no metadata")

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
                    
                    # Connect all signals for the recreated cell
                    if hasattr(cell, 'refresh_requested'):
                        cell.refresh_requested.connect(lambda c=cell: self.refresh_cell(c))
                    cell.remove_requested.connect(lambda title: self.remove_metric_cell(title))
                    cell.move_up_requested.connect(lambda title: self.move_cell_up_by_name(title))
                    cell.move_down_requested.connect(lambda title: self.move_cell_down_by_name(title))
                    cell.duplicate_requested.connect(lambda title: self.duplicate_metric_cell_by_name(title))
                    
                    print(f"[DEBUG] Recreated cell for {config.get('name')} anchored to corpus: {corpus_id}")
                else:
                    print(f"[ERROR] Failed to recreate cell for {config.get('name')}")


