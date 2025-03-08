from visualizations.metric_visualizations import (
    FrequencyDistributionVisualization,
    BOScoreBarVisualization,
    BOScoreLineVisualization,  # Placeholder
    BOScoreTableVisualization,  # Placeholder
    
)
from visualizations.cell_layout import (
    FrequencyDistributionLayout,
    FrequencyReportsLayout,
    BOScoreBarLayout,
    BOScoreLineLayout,  # Placeholder
    BOScoreTableLayout  # Placeholder
)

visualization_registry = {
    "frequency_distribution": {
        "class": FrequencyDistributionVisualization,
        "layout": FrequencyDistributionLayout,
        "needs_vis": True,  # Layout needs a visualization instance
    },
    "frequency_reports": {
        "class": None,
        "layout": FrequencyReportsLayout,
        "needs_vis": False,  # Layout directly uses controller/corpus_id
    },

    # BO Score sub-metrics
    "bo_score_bar": {
        "class": BOScoreBarVisualization,
        "layout": BOScoreBarLayout,
        "needs_vis": True,
    },
    "bo_score_line": {
        "class": BOScoreLineVisualization,
        "layout": BOScoreLineLayout,
        "needs_vis": True,
    },
    "bo_score_table": {
        "class": BOScoreTableVisualization,
        "layout": BOScoreTableLayout,
        "needs_vis": True,
    },
}

def get_visualization_class(vis_type):
    entry = visualization_registry.get(vis_type)
    if not entry or not entry["class"]:
        return None
    return entry["class"]

def get_visualization_layout(vis_type):
    entry = visualization_registry.get(vis_type)
    if not entry or not entry["layout"]:
        return None
    return entry["layout"]

def needs_visualization(vis_type):
    """Determines if this visualization type needs a visualization instance for its layout."""
    entry = visualization_registry.get(vis_type)
    if not entry:
        return True  # Default to needing visualization
    return entry.get("needs_vis", True)  # Default to True if not specified
