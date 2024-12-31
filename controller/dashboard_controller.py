# dashboard_controller.py

from ui.dashboard_ui import DashboardWindow
from config.metric_registry import get_metric
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
        """
        Called when user double-clicks or selects a metric.
        Retrieves metric data and calls create_cell(...) to build the widget.
        """
        if not self.view:
            return

        # Get selected metric details from the UI
        category_key, sub_key = self.view.get_selected_metric_keys()
        if category_key is None or sub_key is None:
            return

        # Retrieve metric data from the registry
        metric_data = get_metric(category_key, sub_key)
        if not metric_data:
            return

        # Extract necessary data
        metric_name = metric_data["name"]
        visualization_type = metric_data["visualization_type"]
        initial_mode = metric_data.get("initial_mode", "nominal")

        # Create the cell widget using the factory
        file_reports = self.main_controller.file_reports
        cell_widget = create_cell(file_reports, category_key, sub_key, initial_mode=initial_mode)
        if cell_widget:
            # Add the widget to the dashboard notebook
            cell = self.view.add_cell(metric_name, cell_widget)

            # Hook up signals for cell actions
            cell.remove_requested.connect(lambda: self.remove_metric_cell(metric_name))
            cell.duplicate_requested.connect(lambda: self.duplicate_metric_cell(metric_name, cell))
            cell.move_up_requested.connect(lambda: self.move_metric_cell_up(cell))
            cell.move_down_requested.connect(lambda: self.move_metric_cell_down(cell))

            # Store metadata about the cell
            self.cell_data_map[cell] = {
                "category_key": category_key,
                "sub_key": sub_key,
                "visualization_type": visualization_type,
                "initial_mode": initial_mode,
            }

    def remove_metric_cell(self, metric_name):
        """
        Remove the specified metric cell by its name.
        """
        if self.view:
            self.view.remove_cell_by_name(metric_name)

    def duplicate_metric_cell(self, metric_name, original_cell):
        """
        Duplicate a metric cell by creating a new one with the same configuration.
        """
        if not self.view or original_cell not in self.cell_data_map:
            return

        # Retrieve metadata for the original cell
        info = self.cell_data_map[original_cell]
        category_key = info["category_key"]
        sub_key = info["sub_key"]
        initial_mode = info["initial_mode"]
        file_reports = self.main_controller.file_reports

        # Preserve current scroll position before inserting the new cell
        current_scroll = self.view.preserve_scroll_position()

        # Create and insert the duplicated widget
        new_widget = create_cell(file_reports, category_key, sub_key, initial_mode=initial_mode)
        if new_widget:
            self.view.insert_cell_below(original_cell, f"{metric_name} (copy)", new_widget)

        # Restore the scroll position after insertion
        self.view.restore_scroll_position(current_scroll)

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
