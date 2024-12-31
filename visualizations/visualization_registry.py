# visualization_registry.py

from visualizations.metric_visualizations import (
    FrequencyDistributionVisualization,
    FrequencyReportsAggregator
)
from visualizations.cell_layout import (
    FrequencyDistributionLayout,
    FrequencyReportsLayout
)

visualization_registry = {
    "frequency_distribution": {
        "class": FrequencyDistributionVisualization,
        # layout expects a "vis" object
        "layout": lambda vis: FrequencyDistributionLayout(vis).generate_layout(),
    },
      "frequency_reports": {
        "class": None,
        # Use the consistent name FrequencyReportsLayout
        "layout": lambda file_reports: FrequencyReportsLayout(file_reports),
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
