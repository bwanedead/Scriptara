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
        if not self.view:
            return

        category_key, sub_key = self.view.get_selected_metric_keys()
        if category_key is None or sub_key is None:
            return

        metric_data = get_metric(category_key, sub_key)
        if not metric_data:
            return

        metric_name = metric_data["name"]
        visualization_type = metric_data["visualization_type"]
        file_reports = self.main_controller.file_reports

        if visualization_type == "frequency_reports":
            from visualizations.metric_visualizations import FrequencyReportsAggregator

            # Create the aggregator
            aggregator = FrequencyReportsAggregator(file_reports)
            aggregator_widget = aggregator.widget()

            # Add the widget to a collapsible cell
            cell = self.view.add_cell(metric_name, aggregator_widget)

            # Keep the aggregator alive by storing it in cell_data_map
            self.cell_data_map[cell] = {
                "category_key": category_key,
                "sub_key": sub_key,
                "initial_mode": None,
                "aggregator": aggregator  # Store the aggregator object
            }

            # Connect signals to handle cell actions
            cell.remove_requested.connect(self.remove_metric_cell)
            cell.duplicate_requested.connect(lambda: self.duplicate_metric_cell(metric_name, cell))
            cell.move_up_requested.connect(lambda: self.move_metric_cell_up(cell))
            cell.move_down_requested.connect(lambda: self.move_metric_cell_down(cell))
        else:
            # Handle other visualization types
            initial_mode = metric_data.get("initial_mode", "nominal")
            cell_widget = create_cell(file_reports, category_key, sub_key, initial_mode=initial_mode)
            if cell_widget:
                cell = self.view.add_cell(metric_name, cell_widget)
                self.cell_data_map[cell] = {
                    "category_key": category_key,
                    "sub_key": sub_key,
                    "initial_mode": initial_mode
                }

                cell.remove_requested.connect(self.remove_metric_cell)
                cell.duplicate_requested.connect(lambda: self.duplicate_metric_cell(metric_name, cell))
                cell.move_up_requested.connect(lambda: self.move_metric_cell_up(cell))
                cell.move_down_requested.connect(lambda: self.move_metric_cell_down(cell))

    def remove_metric_cell(self, metric_name):
        if not self.view:
            return
        self.view.remove_cell_by_name(metric_name)

    def duplicate_metric_cell(self, metric_name, original_cell):
        if not self.view or original_cell not in self.cell_data_map:
            return

        category_key, sub_key, initial_mode = self.cell_data_map[original_cell]
        file_reports = self.main_controller.file_reports

        # Preserve scroll position
        current_scroll_position = self.view.preserve_scroll_position()

        # Recreate the cell
        cell_widget = create_cell(file_reports, category_key, sub_key, initial_mode=initial_mode)
        if cell_widget:
            self.view.insert_cell_below(original_cell, f"{metric_name} (copy)", cell_widget)

        # Restore scroll
        self.view.restore_scroll_position(current_scroll_position)

    def move_metric_cell_up(self, cell):
        if not self.view:
            return
        self.view.move_cell_up(cell)

    def move_metric_cell_down(self, cell):
        if not self.view:
            return
        self.view.move_cell_down(cell)
