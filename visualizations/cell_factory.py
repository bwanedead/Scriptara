# cell_factory.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import pyqtSignal
from config.metric_registry import get_metric, METRICS

from visualizations.visualization_registry import get_visualization_class, get_visualization_layout



def create_cell(controller, category_key, sub_key, sub_sub_key=None, initial_mode=None, corpus_id=None):
    """
    Creates a visualization cell with the specified parameters.
    
    Args:
        controller: The main controller reference
        category_key, sub_key, sub_sub_key: Metric identifiers
        initial_mode: Initial visualization mode
        corpus_id: The corpus this cell should be anchored to
        
    Returns:
        A visualization layout widget configured for the specified corpus
    """
    print(f"[DEBUG] create_cell called with corpus_id: {corpus_id}")
    metric_data = get_metric(category_key, sub_key, sub_sub_key)
    if not metric_data:
        print(f"[ERROR] No metric data for {category_key}, {sub_key}, {sub_sub_key}")
        return create_placeholder()

    vis_type = metric_data.get("visualization_type")
    vis_class = get_visualization_class(vis_type)
    layout_class = get_visualization_layout(vis_type)

    try:
        if vis_class and layout_class:
            # Create visualization with controller reference and corpus_id
            vis = vis_class(
                controller=controller,
                initial_mode=metric_data.get("initial_mode", initial_mode),
                corpus_id=corpus_id
            )
            print(f"[DEBUG] Created vis_class {vis_type} with corpus_id: {corpus_id}")
            layout = layout_class(vis)
            
            # Add refresh capability to the layout
            if hasattr(layout, 'refresh_visualization'):
                layout.refresh_requested = pyqtSignal()
                layout.refresh_requested.connect(lambda: layout.refresh_visualization())
            
            print(f"[DEBUG] Returning layout for {vis_type}")
            return layout
        elif layout_class:
            # For layouts that don't use a visualization class
            if vis_type == "frequency_reports":
                # Pass controller and corpus_id instead of file_reports
                layout = layout_class(controller, corpus_id)
                print(f"[DEBUG] Created special layout {vis_type} with corpus_id: {corpus_id}")
            else:
                layout = layout_class(controller, corpus_id)
                print(f"[DEBUG] Created layout {vis_type} with controller")
            return layout
    except Exception as e:
        print(f"[ERROR] Failed to create cell widget: {e}")
        return create_placeholder()


def create_placeholder():
    placeholder = QWidget()
    layout = QVBoxLayout(placeholder)
    layout.addWidget(QWidget())  # Empty content
    return placeholder
