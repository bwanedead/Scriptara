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
        "layout": lambda vis: FrequencyDistributionLayout(vis).generate_layout(),
    },
    "frequency_reports": {
        "class": None,
        "layout": lambda file_reports: FrequencyReportsLayout(file_reports),
    },

    # BO Score sub-metrics
    "bo_score_bar": {
        "class": BOScoreBarVisualization,
        "layout": lambda vis: BOScoreBarLayout(vis).generate_layout(),
    },
    "bo_score_line": {
        "class": BOScoreLineVisualization,
        "layout": lambda vis: BOScoreLineLayout(vis).generate_layout(),
    },
    "bo_score_table": {
        "class": BOScoreTableVisualization,
        "layout": lambda vis: BOScoreTableLayout(vis).generate_layout(),
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
