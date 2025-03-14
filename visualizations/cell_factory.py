# cell_factory.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import pyqtSignal, Qt
from config.metric_registry import get_metric, METRICS

from visualizations.visualization_registry import (
    get_visualization_class, 
    get_visualization_layout,
    needs_visualization
)


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
        return create_placeholder("No metric data available")

    vis_type = metric_data.get("visualization_type")
    vis_class = get_visualization_class(vis_type)
    layout_class = get_visualization_layout(vis_type)
    requires_vis = needs_visualization(vis_type)

    try:
        # Create appropriate layout based on whether it needs a visualization
        if layout_class:
            if requires_vis and vis_class:
                # Convert corpus_id to corpus_ids list for visualizations
                corpus_ids = [corpus_id] if corpus_id else []
                vis = vis_class(
                    controller=controller,
                    initial_mode=metric_data.get("initial_mode", initial_mode),
                    corpus_ids=corpus_ids  # Pass as list
                )
                print(f"[DEBUG] Created vis_class {vis_type} with corpus_ids: {corpus_ids}")
                
                # Create layout with visualization
                layout = layout_class(vis)
                if hasattr(layout, 'generate_layout'):
                    layout = layout.generate_layout()
                    
                print(f"[DEBUG] Created layout for {vis_type} with visualization")
                return layout
            else:
                # Layouts like FrequencyReportsLayout still expect corpus_id
                layout = layout_class(controller, corpus_id)
                print(f"[DEBUG] Created layout for {vis_type} without visualization")
                return layout
        else:
            print(f"[ERROR] No layout class found for {vis_type}")
            return create_placeholder(f"No layout available for {vis_type}")
    except Exception as e:
        import traceback
        print(f"[ERROR] Failed to create cell widget: {e}")
        traceback.print_exc()
        return create_placeholder(f"Error creating visualization: {str(e)}")


def create_placeholder(message="Visualization unavailable"):
    placeholder = QWidget()
    layout = QVBoxLayout(placeholder)
    error_label = QLabel(message)
    error_label.setAlignment(Qt.AlignCenter)
    error_label.setStyleSheet("color: #ff5555; font-size: 14px;")
    layout.addWidget(error_label)
    return placeholder
