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
                "name": "BO Score (choose type)",
                "description": "Custom overlap metric BOn1 and BOn2",
                "visualization_type": None,  # parent node
                "sub_metrics": {
                    "bo_table": {
                        "name": "BO Score Table",
                        "description": "Displays BOn1/BOn2 in table form",
                        "visualization_type": "bo_score_table",
                    },
                    "bo_bar": {
                        "name": "BO Score Bar Chart",
                        "description": "Displays BOn1/BOn2 as a bar chart",
                        "visualization_type": "bo_score_bar",
                    },
                    "bo_line": {
                        "name": "BO Score Line Chart",
                        "description": "Displays BOn1/BOn2 as a line chart",
                        "visualization_type": "bo_score_line",
                    },
                },
            },
            
            
        },
    },
}

def get_metric(category_key, sub_key, sub_sub_key=None):
    category = METRICS.get(category_key, {})
    if not category:
        return None
    metric_data = category.get("sub_metrics", {}).get(sub_key, {})
    if sub_sub_key:
        return metric_data.get("sub_metrics", {}).get(sub_sub_key)
    return metric_data

