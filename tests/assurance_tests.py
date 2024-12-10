# scriptara/tests/assurance_tests.py

from collections import Counter

def independent_total_word_count(words):
    """Calculates the total number of words."""
    return len(words)

def independent_unique_word_count(words):
    """Calculates the number of unique words."""
    return len(set(words))

def independent_percentage_sum(word_counts):
    """Calculates the sum of percentage frequencies, with a safeguard for division by zero."""
    total_count = sum(word_counts.values())
    if total_count == 0:
        return 0.0  # Handle division by zero for empty inputs
    percentages = [(count / total_count) * 100 for count in word_counts.values()]
    return sum(percentages)

def independent_rank_count(word_stats):
    """Calculates the number of ranks (unique words) in the word stats."""
    return len(word_stats)

def independent_total_from_counts(word_counts):
    """Calculates the total word count from individual word frequencies."""
    return sum(word_counts.values())
