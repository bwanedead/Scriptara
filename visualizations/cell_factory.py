# cell_factory.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from config.metric_registry import get_metric, METRICS

from visualizations.visualization_registry import get_visualization_class, get_visualization_layout



def create_cell(file_reports, category_key, sub_key, sub_sub_key=None, initial_mode=None):
    # Retrieve the metric data using get_metric
    metric_data = get_metric(category_key, sub_key, sub_sub_key)

    if not metric_data:
        print(f"[ERROR] Metric data not found for keys: category_key={category_key}, sub_key={sub_key}, sub_sub_key={sub_sub_key}")
        return create_placeholder()

    # Get visualization type, class, and layout function
    vis_type = metric_data.get("visualization_type")
    vis_class = get_visualization_class(vis_type)
    layout_func = get_visualization_layout(vis_type)

    if not layout_func:
        print(f"[ERROR] No layout function found for vis_type: {vis_type}")
        return create_placeholder()

    # Handle visualization initialization
    try:
        if vis_class:
            # Pass `initial_mode` only if the visualization class supports it
            vis = vis_class(file_reports, initial_mode=metric_data.get("initial_mode", initial_mode))
            cell_widget = layout_func(vis)
        else:
            # Handle simpler cases without visualization classes
            cell_widget = layout_func(file_reports)
    except Exception as e:
        print(f"[ERROR] Failed to create cell widget: {e}")
        return create_placeholder()

    print(f"[DEBUG] Cell created with vis_type={vis_type}, sub_sub_key={sub_sub_key}")
    return cell_widget


def create_placeholder():
    placeholder = QWidget()
    layout = QVBoxLayout(placeholder)
    layout.addWidget(QWidget())  # Empty content
    return placeholder
