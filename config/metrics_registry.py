# config/metrics_registry.py

METRICS = {
    "frequency_distribution": {
        "name": "Frequency Distribution",
        "description": "Metrics related to frequency of words.",
        "sub_metrics": {
            "nominal_frequency": {
                "name": "Nominal Frequency",
                "description": "Raw frequency of words.",
                "calculation_function": "advanced_analysis.calculate_nominal_frequency",
                "visualization_type": "line_plot",
            },
            # Additional sub-metrics can go here...
        }
    },
    "overlap_metrics": {
        "name": "Overlap Metrics",
        "description": "Metrics that measure overlap between texts.",
        "sub_metrics": {
            "jaccard_index": {
                "name": "Jaccard Index",
                "description": "Measures similarity between sets.",
                "calculation_function": "advanced_analysis.calculate_jaccard_index",
                "visualization_type": "heatmap",
            },
            "bo_score": {
                "name": "BO Score",
                "description": "Custom overlap metric BOn1 and BOn2.",
                "calculation_function": "advanced_analysis.calculate_bo_scores",
                "visualization_type": "bar_chart",
            }
            # Additional sub-metrics can go here...
        }
    }
}

def get_metric(category_key, sub_key):
    """
    Retrieve a specific metric configuration by category and sub-metric key.

    Args:
        category_key (str): The key for the category of the metric.
        sub_key (str): The key for the sub-metric.

    Returns:
        dict or None: The configuration dictionary for the metric, or None if not found.
    """
    category = METRICS.get(category_key)
    if not category:
        return None
    return category["sub_metrics"].get(sub_key)
