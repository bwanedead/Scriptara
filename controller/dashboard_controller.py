# dashboard_controller.py

from ui.dashboard_ui import DashboardWindow
from config.metric_registry import get_metric, METRICS
from visualizations.cell_factory import create_cell

class DashboardController:
    def __init__(self, main_controller=None):
        self.main_controller = main_controller
        self.view = None
        self.cell_data_map = {}

    def show(self):
        if not self.view:
            self.view = DashboardWindow(controller=self)
        self.view.show()

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
            sub_sub_key=sub_sub_key,  # Explicitly pass sub_sub_key
            initial_mode=initial_mode
        )

        if cell_widget:
            cell = self.view.add_cell(metric_name, cell_widget)

            # Connect signals to handle cell actions
            cell.remove_requested.connect(lambda title=cell.title: self.remove_metric_cell_instance(cell))
            cell.duplicate_requested.connect(lambda: self.duplicate_metric_cell(metric_name, cell))
            cell.move_up_requested.connect(lambda: self.move_metric_cell_up(cell))
            cell.move_down_requested.connect(lambda: self.move_metric_cell_down(cell))

            # Store metadata for this cell
            self.cell_data_map[cell] = {
                "category_key": category_key,
                "sub_key": sub_key,
                "sub_sub_key": sub_sub_key,
                "visualization_type": visualization_type,
                "initial_mode": initial_mode,
            }
            print(f"[DEBUG] Metric cell added for {metric_name}.")
        else:
            print("[ERROR] Cell widget creation failed.")


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
        visualization_type = metadata["visualization_type"]
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


