# cell_factory.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from config.metric_registry import get_metric, METRICS

from visualizations.visualization_registry import get_visualization_class, get_visualization_layout



def create_cell(file_reports, category_key, sub_key, sub_sub_key=None, initial_mode=None):
    metric_data = get_metric(category_key, sub_key, sub_sub_key)
    if not metric_data:
        return create_placeholder()

    vis_type = metric_data.get("visualization_type")
    vis_class = get_visualization_class(vis_type)
    layout_class = get_visualization_layout(vis_type)

    try:
        if vis_class and layout_class:
            vis = vis_class(file_reports, initial_mode=metric_data.get("initial_mode", initial_mode))
            return layout_class(vis)  # Return the layout widget directly
        elif layout_class:
            return layout_class(file_reports)
    except Exception as e:
        print(f"[ERROR] Failed to create cell widget: {e}")
        return create_placeholder()


def create_placeholder():
    placeholder = QWidget()
    layout = QVBoxLayout(placeholder)
    layout.addWidget(QWidget())  # Empty content
    return placeholder
