# cell_factory.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from config.metric_registry import get_metric
from visualizations.visualization_registry import get_visualization_class, get_visualization_layout

def create_cell(file_reports, category_key, sub_key, initial_mode=None):
    metric_data = get_metric(category_key, sub_key)
    if not metric_data:
        return create_placeholder()

    visualization_type = metric_data["visualization_type"]
    vis_class = get_visualization_class(visualization_type)
    layout_func = get_visualization_layout(visualization_type)

    if not layout_func:
        return create_placeholder()

    # If we have a class, we instantiate it with file_reports, else pass file_reports to the layout
    if vis_class:
        vis = vis_class(file_reports, initial_mode=metric_data.get("initial_mode", initial_mode))
        cell_widget = layout_func(vis)
    else:
        # For "frequency_reports", we assume no class is needed.
        cell_widget = layout_func(file_reports)

    return cell_widget

def create_placeholder():
    placeholder = QWidget()
    layout = QVBoxLayout(placeholder)
    layout.addWidget(QWidget())  # Empty content
    return placeholder
