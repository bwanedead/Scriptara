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
    """Calculates total word count, unique word count, and word statistics including percentage, Z-score, and log-transformed Z-score."""
    total_word_count = sum(word_counts.values())
    unique_word_count = len(word_counts)

    # Extract word counts
    words = list(word_counts.keys())
    counts = list(word_counts.values())

    # Calculate percentage frequencies
    percentages = (np.array(counts) / total_word_count) * 100

    # Calculate Z-scores for raw counts
    mean_freq = np.mean(counts)
    std_freq = np.std(counts)
    z_scores = (counts - mean_freq) / std_freq if std_freq > 0 else np.zeros_like(counts)

    # Calculate log-transformed Z-scores
    log_counts = np.log(counts)
    mean_log_count = np.mean(log_counts)
    std_log_count = np.std(log_counts)
    log_z_scores = (log_counts - mean_log_count) / std_log_count if std_log_count > 0 else np.zeros_like(log_counts)

    # Combine statistics into a list of tuples with five elements
    word_stats = list(zip(words, counts, percentages, z_scores, log_z_scores))

    return {
        'total_word_count': total_word_count,
        'unique_word_count': unique_word_count,
        'word_stats': word_stats  # Each item is (word, count, percentage, z_score, log_z_score)
    }


def get_sorted_word_frequencies(word_counts):
    """Returns a list of word frequencies sorted in descending order."""
    return [count for word, count in word_counts.most_common()]



