import re
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
    """Returns key statistics like total words, unique words, and word frequencies."""
    total_word_count = sum(word_counts.values())
    unique_word_count = len(word_counts)
    
    # For each word, calculate its percentage frequency
    word_stats = [(word, count, (count / total_word_count) * 100) for word, count in word_counts.most_common()]

    return {
        'total_word_count': total_word_count,
        'unique_word_count': unique_word_count,
        'word_stats': word_stats
    }

def get_sorted_word_frequencies(word_counts):
    """Returns a list of word frequencies sorted in descending order."""
    return [count for word, count in word_counts.most_common()]



