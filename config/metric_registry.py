# metrics_registry.py

METRICS = {
    "frequency_distribution": {
        "name": "Frequency Distribution",
        "description": "Metrics related to frequency of words.",
        "sub_metrics": {
            "nominal": {
                "name": "Nominal Frequency",
                "description": "Raw frequency of words.",
                "calculation_function": "advanced_analysis.calculate_nominal_frequency",
                "visualization_type": "frequency_distribution",
                "initial_mode": "nominal"
            },
            "percentage": {
                "name": "Percentage Frequency",
                "description": "Frequency as percentages.",
                "calculation_function": "advanced_analysis.calculate_percentage_frequency",
                "visualization_type": "frequency_distribution",
                "initial_mode": "percentage"
            },
            "z_score": {
                "name": "Z-Score Frequency",
                "description": "Z-score of word frequencies.",
                "calculation_function": "advanced_analysis.calculate_z_score_frequency",
                "visualization_type": "frequency_distribution",
                "initial_mode": "z_score"
            },
            "reports": {
                "name": "Frequency Reports",
                "description": "Display aggregator-based frequency reports in a single view.",
                "calculation_function": "advanced_analysis.get_reports",
                "visualization_type": "frequency_reports"
            },
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
        }
    }
}

def get_metric(category_key, sub_key):
    category = METRICS.get(category_key)
    if not category:
        return None
    return category["sub_metrics"].get(sub_key)
