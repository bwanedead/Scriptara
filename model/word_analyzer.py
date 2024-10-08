

import re
import numpy as np
from collections import Counter



def read_and_preprocess_file(file_path):
    """Reads a text file and preprocesses it by removing punctuation and converting to lowercase."""
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read().lower()
        text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    return text.split()

def calculate_word_frequencies(words):
    """Calculates the word frequencies using a Counter."""
    return Counter(words)

def get_text_statistics(word_counts):
    """Returns key statistics like total words, unique words, word frequencies, percentage frequencies, and Z-scores."""
    total_word_count = sum(word_counts.values())
    unique_word_count = len(word_counts)

    # Get word frequencies sorted by count in descending order
    word_stats = word_counts.most_common()
    words = [word for word, count in word_stats]
    counts = np.array([count for word, count in word_stats])

    # Calculate percentage frequencies
    percentages = (counts / total_word_count) * 100

    # Calculate Z-scores
    mean_freq = np.mean(counts)
    std_freq = np.std(counts)
    if std_freq == 0:
        z_scores = np.zeros_like(counts)
    else:
        z_scores = (counts - mean_freq) / std_freq

    # Combine statistics into a list of tuples
    word_stats = list(zip(words, counts, percentages, z_scores))

    return {
        'total_word_count': total_word_count,
        'unique_word_count': unique_word_count,
        'word_stats': word_stats  # Each item is (word, count, percentage, z_score)
    }

def get_sorted_word_frequencies(word_counts):
    """Returns a list of word frequencies sorted in descending order."""
    return [count for word, count in word_counts.most_common()]



