import unittest
import os
from collections import Counter
from model.word_analyzer import read_and_preprocess_file, calculate_word_frequencies, get_text_statistics

class TestWordAnalyzer(unittest.TestCase):
    def setUp(self):
        # Define the path to the test data directory
        self.test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data')

        # Check if all test files exist
        for filename in ['benchmark_test1.txt', 'benchmark_test2.txt', 'benchmark_test3.txt', 'benchmark_test_empty.txt']:
            file_path = os.path.join(self.test_data_dir, filename)
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Test file not found: {file_path}")

        # Updated expected results for benchmark_test1.txt
        self.expected_counts_text1 = Counter({
            'hello': 51,
            'world': 53,
            'apple': 50,
            'the': 61,
            'of': 41,
            'and': 71
        })
        self.total_words_text1 = 327

        # Updated expected results for benchmark_test2.txt
        self.expected_counts_text2 = Counter({
            'hello': 37,
            'world': 40
        })
        self.total_words_text2 = 77

        # Adjust expected word counts for test_benchmark_test3
        self.expected_counts_text3 = Counter({
            'hello': 10, '123': 3, '101': 3, 'café': 3, 
            '456': 2, '789': 2, '2020': 2, '3030': 2, 
            'value': 2, 'price': 2, 'data@code': 2, 'level#1': 2, 'result&2': 2
        })
        self.total_words_text3 = 37


        # Expected results for benchmark_test_empty.txt
        self.expected_counts_empty = Counter()
        self.total_words_empty = 0

    def test_benchmark_test1(self):
        self.run_test_for_file('benchmark_test1.txt', self.expected_counts_text1, self.total_words_text1)

    def test_benchmark_test2(self):
        self.run_test_for_file('benchmark_test2.txt', self.expected_counts_text2, self.total_words_text2)

    def test_benchmark_test3(self):
        self.run_test_for_file('benchmark_test3.txt', self.expected_counts_text3, self.total_words_text3)

    def test_benchmark_test_empty(self):
        self.run_test_for_file('benchmark_test_empty.txt', self.expected_counts_empty, self.total_words_empty)

        # Additionally, check that word_stats is an empty list
        file_path = os.path.join(self.test_data_dir, 'benchmark_test_empty.txt')
        words, _ = read_and_preprocess_file(file_path)
        word_counts = calculate_word_frequencies(words)
        stats = get_text_statistics(word_counts)

        self.assertEqual(stats['word_stats'], [],
                        "Expected word_stats to be an empty list for empty input.")


    def run_test_for_file(self, filename, expected_counts, expected_total):
        file_path = os.path.join(self.test_data_dir, filename)
        words, _ = read_and_preprocess_file(file_path)  # Ignore punctuation output

        # Debugging: Print extracted words and their counts for review
        print(f"\nExtracted words from {filename}: {words}")
        word_counts = calculate_word_frequencies(words)
        print(f"Word counts from {filename}: {word_counts}")
        print(f"Expected word counts for {filename}: {expected_counts}")

        stats = get_text_statistics(word_counts)

        # Check word counts and totals only
        self.assertEqual(stats['total_word_count'], expected_total,
                        f"Expected {expected_total} words, but got {stats['total_word_count']}.")
        self.assertEqual(word_counts, expected_counts,
                        f"Word counts do not match for {filename}.\nExpected: {expected_counts}\nGot: {word_counts}")


if __name__ == '__main__':
    unittest.main()
