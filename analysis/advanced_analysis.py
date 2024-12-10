import numpy as np
import logging
from itertools import combinations


class OverlapAnalyzer:
    def __init__(self, file_reports):
        """
        Initializes the OverlapAnalyzer with the file reports.

        Parameters:
            file_reports (dict): Dictionary containing file reports with word statistics.
        """
        self.file_reports = file_reports
        self.word_sets = {}

    def create_word_sets(self):
        """
        Creates word sets for each text from the file reports, excluding the Master Report.

        Returns:
            None: The method updates self.word_sets with sets of unique words.
        """
        self.word_sets = {}
        for file_key, report in self.file_reports.items():
            # Skip the Master Report
            if file_key == "Master Report":
                continue
            
            # Extract the word stats and create a set of words for the text
            word_stats = report['data']['word_stats']
            words = [word for word, _, _, _, _ in word_stats]
            word_set = set(words)
            self.word_sets[file_key] = word_set

    
    def create_intersection_set(self, text1, text2):
            """
            Creates an intersection set of words that are present in both text1 and text2.

            Parameters:
                text1 (str): The key corresponding to the first text.
                text2 (str): The key corresponding to the second text.

            Returns:
                set: A set of words that are present in both text1 and text2.
            """
            # Ensure both texts exist in the word_sets dictionary
            if text1 not in self.word_sets or text2 not in self.word_sets:
                raise ValueError(f"One or both texts ({text1}, {text2}) are not in the word_sets dictionary.")

            # Compute the intersection of the two word sets
            intersection = self.word_sets[text1] & self.word_sets[text2]

            return intersection
        
    def generate_pairwise_intersections(self):
            """
            Generate intersection sets for all pairwise combinations of texts.

            Returns:
                dict: A dictionary where keys are tuples of text pairs (text1, text2)
                    and values are the sets of intersecting words.
            """
            pairwise_intersections = {}

            # Generate all pairwise combinations of text keys
            text_keys = list(self.word_sets.keys())
            for text1, text2 in combinations(text_keys, 2):
                # Compute intersection for each pair
                intersection_set = self.create_intersection_set(text1, text2)
                pairwise_intersections[(text1, text2)] = intersection_set

            return pairwise_intersections
        
    def calculate_total_intersection_words(self, pairwise_intersections):
            """
            Calculate the total number of unique words across all pairwise intersection sets.

            Args:
                pairwise_intersections (dict): A dictionary of pairwise intersections where
                    keys are tuples of text pairs (text1, text2) and values are the sets of intersecting words.

            Returns:
                int: Total number of unique words across all intersection sets.
            """
            # Combine all words from all intersection sets into one set
            all_intersection_words = set()
            for intersection_set in pairwise_intersections.values():
                all_intersection_words.update(intersection_set)

            # Return the size of the combined set
            return len(all_intersection_words)

    def calculate_assurance_metrics(self, pairwise_intersections):
        """
        Calculates and validates the assurance metric to ensure the total number of 
        unique words across all texts matches the sum of intersection and unique words.

        Args:
            pairwise_intersections (dict): A dictionary of pairwise intersections where
                keys are tuples of text pairs (text1, text2) and values are the sets of intersecting words.

        Returns:
            dict: A dictionary containing the total unique words, intersection words, 
                unique-to-single-text words, and a boolean indicating if the assurance passed.
        """
        # Calculate total unique words across all intersection sets
        all_intersection_words = set()
        for intersection_set in pairwise_intersections.values():
            all_intersection_words.update(intersection_set)
        total_intersection_words = len(all_intersection_words)

        # Calculate words unique to a single text
        unique_to_single_text = set()
        for text, word_set in self.word_sets.items():
            other_texts = set(self.word_sets.keys()) - {text}
            other_words = set.union(*(self.word_sets[t] for t in other_texts))
            unique_to_single_text.update(word_set - other_words)
        total_unique_to_single_text = len(unique_to_single_text)

        # Total unique words in the corpus
        total_unique_words_in_corpus = len(set.union(*self.word_sets.values()))

        # Assurance check
        assurance_passed = (total_intersection_words + total_unique_to_single_text == total_unique_words_in_corpus)

        return {
            "total_unique_words_in_corpus": total_unique_words_in_corpus,
            "total_intersection_words": total_intersection_words,
            "total_unique_to_single_text": total_unique_to_single_text,
            "assurance_passed": assurance_passed
    }

    def prepare_bo_data(self):
        self.word_counts = {}
        self.total_words = {}
        self.word_sets = {}
        word_occurrences = {}

        for file_key, report in self.file_reports.items():
            word_stats = report['data']['word_stats']
            word_counts = {word: count for word, count, _, _, _ in word_stats}
            total_word_count = sum(word_counts.values())

            self.word_counts[file_key] = word_counts
            self.total_words[file_key] = total_word_count
            self.word_sets[file_key] = set(word_counts.keys())

            for word in word_counts.keys():
                if word not in word_occurrences:
                    word_occurrences[word] = set()
                word_occurrences[word].add(file_key)

        self.words_in_multiple_texts = {word for word, texts in word_occurrences.items() if len(texts) >= 2}

    def calculate_bo_pairwise_weights(self):
        self.pairwise_pw = {}
        text_pairs = list(combinations(self.file_reports.keys(), 2))
        unique_intersection_words = set()

        for T1, T2 in text_pairs:
            set1 = self.word_sets[T1]
            set2 = self.word_sets[T2]
            intersection = set1 & set2
            unique_intersection_words.update(intersection)

            counts1 = self.word_counts[T1]
            counts2 = self.word_counts[T2]
            total_words1 = self.total_words[T1]
            total_words2 = self.total_words[T2]

            freq_percent_T1_all = {w: counts1[w] / total_words1 for w in counts1}
            freq_percent_T2_all = {w: counts2[w] / total_words2 for w in counts2}

            avg_freq_T1 = np.mean(list(freq_percent_T1_all.values()))
            avg_freq_T2 = np.mean(list(freq_percent_T2_all.values()))
            normalization_factor_bon1 = (avg_freq_T1 + avg_freq_T2) / 2

            union_words = set1 | set2
            freq_union = {
                w: (freq_percent_T1_all.get(w, 0) + freq_percent_T2_all.get(w, 0)) / 2
                for w in union_words
            }
            avg_freq_union = np.mean(list(freq_union.values()))

            for w in intersection:
                freq1 = counts1[w] / total_words1
                freq2 = counts2[w] / total_words2
                pw = freq1 * freq2

                if normalization_factor_bon1 != 0:
                    pw_normalized_bon1 = pw / normalization_factor_bon1
                else:
                    pw_normalized_bon1 = 0

                if avg_freq_union != 0:
                    pw_normalized_bon2 = pw / avg_freq_union
                else:
                    pw_normalized_bon2 = 0

                key = (w, T1, T2)
                self.pairwise_pw[key] = {
                    'PW': pw,
                    'PW_normalized_BOn1': pw_normalized_bon1,
                    'PW_normalized_BOn2': pw_normalized_bon2
                }

    def aggregate_bo_scores(self):
        self.summed_pw_bon1 = {}
        self.summed_pw_bon2 = {}

        for (w, T1, T2), values in self.pairwise_pw.items():
            self.summed_pw_bon1[w] = self.summed_pw_bon1.get(w, 0) + values['PW_normalized_BOn1']
            self.summed_pw_bon2[w] = self.summed_pw_bon2.get(w, 0) + values['PW_normalized_BOn2']

    def compute_bo_scores(self):
        self.prepare_bo_data()
        self.calculate_bo_pairwise_weights()
        self.aggregate_bo_scores()

        non_zero_bon1 = {w: score for w, score in self.summed_pw_bon1.items() if score > 0}
        non_zero_bon2 = {w: score for w, score in self.summed_pw_bon2.items() if score > 0}

        unique_to_one_text = set(self.words_in_multiple_texts)
        bon1_unique_check = [w for w in self.summed_pw_bon1.keys() if w not in unique_to_one_text]
        bon2_unique_check = [w for w in self.summed_pw_bon2.keys() if w not in unique_to_one_text]

        if bon1_unique_check:
            logging.warning(f"Words in BOn1 that should not be present: {bon1_unique_check}")
        if bon2_unique_check:
            logging.warning(f"Words in BOn2 that should not be present: {bon2_unique_check}")

    def get_bo_scores(self):
        return self.summed_pw_bon1, self.summed_pw_bon2

    def create_word_frequency_vectors(self):
        all_words_set = set()
        for report in self.file_reports.values():
            word_stats = report['data']['word_stats']
            words = [word for word, _, _, _, _ in word_stats]
            all_words_set.update(words)
        
        all_words = sorted(list(all_words_set))

        frequency_vectors = {}
        for file_key, report in self.file_reports.items():
            word_counts = {word: count for word, count, _, _, _ in report['data']['word_stats']}
            vector = [word_counts.get(word, 0) for word in all_words]
            frequency_vectors[file_key] = vector
        
        return frequency_vectors, all_words

    def create_normalized_frequency_vectors(self, frequency_vectors):
        normalized_vectors = {}
        for text_name, vector in frequency_vectors.items():
            total = sum(vector)
            if total > 0:
                normalized_vector = [count / total for count in vector]
            else:
                normalized_vector = vector
            normalized_vectors[text_name] = normalized_vector
        return normalized_vectors



        
        