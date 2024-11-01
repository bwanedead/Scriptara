import re
import numpy as np
from collections import Counter



import re

import re

import re

def read_and_preprocess_file(file_path):
    """Reads a text file, processes it to capture alphanumeric sequences with symbols as single words."""
    words = []
    punctuation = []

    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read().lower()

        # Updated regex to capture alphanumeric words with attached symbols as single units
        tokens = re.findall(r'\b\w[\w@#\$%&!\-]*\b', text)  # Adjust to capture words with symbols like @, #, etc.
        
        for token in tokens:
            if re.match(r'\w[\w@#\$%&!\-]*', token):  # Accept words with alphanumeric characters and symbols
                words.append(token)
            else:
                punctuation.append(token)  # Collect standalone punctuation separately

    return words, punctuation





def calculate_word_frequencies(words):
    """Calculates the word frequencies using a Counter."""
    return Counter(words)

def get_text_statistics(word_counts):
    """Calculates total word count, unique word count, and word statistics including percentage, Z-score, and log-transformed Z-score."""
    total_word_count = sum(word_counts.values())
    unique_word_count = len(word_counts)

    # Check if total_word_count is zero to handle empty inputs
    if total_word_count == 0:
        return {
            'total_word_count': 0,
            'unique_word_count': 0,
            'word_stats': []  # Empty list since there are no words
        }

    # Extract word counts
    words = list(word_counts.keys())
    counts = np.array(list(word_counts.values()))

    # Calculate percentage frequencies
    percentages = (counts / total_word_count) * 100

    # Calculate Z-scores for raw counts
    mean_freq = np.mean(counts)
    std_freq = np.std(counts, ddof=1)  # Use ddof=1 for sample standard deviation
    if std_freq > 0:
        z_scores = (counts - mean_freq) / std_freq
    else:
        z_scores = np.zeros_like(counts)

    # Calculate log-transformed Z-scores
    log_counts = np.log(counts)
    mean_log_count = np.mean(log_counts)
    std_log_count = np.std(log_counts, ddof=1)
    if std_log_count > 0:
        log_z_scores = (log_counts - mean_log_count) / std_log_count
    else:
        log_z_scores = np.zeros_like(counts)

    # Combine statistics into a list of tuples with five elements
    word_stats = list(zip(words, counts, percentages, z_scores, log_z_scores))

    # Sort word_stats by count in descending order (for consistent ranking)
    word_stats.sort(key=lambda x: x[1], reverse=True)

    return {
        'total_word_count': total_word_count,
        'unique_word_count': unique_word_count,
        'word_stats': word_stats
    }




def get_sorted_word_frequencies(word_counts):
    """Returns a list of word frequencies sorted in descending order."""
    return [count for word, count in word_counts.most_common()]



