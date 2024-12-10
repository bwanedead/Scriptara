# dashboard_controller.py

from ui.dashboard_ui import DashboardWindow, MetricCellWidget
from config.metrics_registry import get_metric

class DashboardController:
    def __init__(self, main_controller=None):
        self.main_controller = main_controller
        self.view = None

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
        cell = self.view.add_metric_cell(metric_name)

        cell.remove_requested.connect(self.remove_metric_cell)
        cell.move_up_requested.connect(self.move_metric_cell_up)
        cell.move_down_requested.connect(self.move_metric_cell_down)

    def remove_metric_cell(self, metric_name):
        if not self.view:
            return
        for i in range(self.view.metrics_layout.count()):
            item = self.view.metrics_layout.itemAt(i)
            widget = item.widget() if item else None
            if isinstance(widget, MetricCellWidget) and widget.metric_name == metric_name:
                w = self.view.metrics_layout.takeAt(i).widget()
                w.deleteLater()
                break

    def move_metric_cell_up(self, metric_name):
        self.reorder_metric_cell(metric_name, -1)

    def move_metric_cell_down(self, metric_name):
        self.reorder_metric_cell(metric_name, 1)

    def reorder_metric_cell(self, metric_name, direction):
        if not self.view:
            return
        for i in range(self.view.metrics_layout.count()):
            item = self.view.metrics_layout.itemAt(i)
            widget = item.widget() if item else None
            if isinstance(widget, MetricCellWidget) and widget.metric_name == metric_name:
                target_index = i + direction
                if 0 <= target_index < self.view.metrics_layout.count() - 1:
                    self.view.metrics_layout.removeWidget(widget)
                    self.view.metrics_layout.insertWidget(target_index, widget)
                break
