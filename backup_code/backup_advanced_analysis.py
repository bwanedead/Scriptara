# import numpy as np
# import logging
# from itertools import combinations

# class OverlapAnalyzer:
#     def __init__(self, file_reports):
#         """
#         Initializes the OverlapAnalyzer with the file reports.

#         Parameters:
#             file_reports (dict): Dictionary containing file reports with word statistics.
#         """
#         self.file_reports = file_reports
#         self.word_sets = {}
#         self.frequency_vectors = {}
#         self.normalized_vectors = {}
#         self.similarity_results = {}

#          # New data structures for BO Score
#         self.word_counts = {}
#         self.total_words = {}
#         self.words_in_corpus = set()
#         self.pairwise_pw = {}
#         self.summed_pw_bon1 = {}
#         self.summed_pw_bon2 = {}

#     def create_word_sets(self):
#         """
#         Creates word sets for each text from the file reports.

#         Returns:
#             None: The method updates self.word_sets with sets of unique words.
#         """
#         self.word_sets = {}
#         for file_key, report in self.file_reports.items():
#             word_stats = report['data']['word_stats']
#             words = [word for word, _, _, _, _ in word_stats]
#             word_set = set(words)
#             self.word_sets[file_key] = word_set
    
#     def create_intersection_set(self, text1, text2):
#         """
#         Creates an intersection set of words that are present in both text1 and text2.

#         Parameters:
#             text1 (str): The key corresponding to the first text.
#             text2 (str): The key corresponding to the second text.

#         Returns:
#             set: A set of words that are present in both text1 and text2.
#         """
#         # Ensure both texts exist in the word_sets dictionary
#         if text1 not in self.word_sets or text2 not in self.word_sets:
#             raise ValueError(f"One or both texts ({text1}, {text2}) are not in the word_sets dictionary.")

#         # Compute the intersection of the two word sets
#         intersection = self.word_sets[text1] & self.word_sets[text2]

#         return intersection
    
#     def generate_pairwise_intersections(self):
#         """
#         Generate intersection sets for all pairwise combinations of texts.

#         Returns:
#             dict: A dictionary where keys are tuples of text pairs (text1, text2)
#                 and values are the sets of intersecting words.
#         """
#         pairwise_intersections = {}

#         # Generate all pairwise combinations of text keys
#         text_keys = list(self.word_sets.keys())
#         for text1, text2 in combinations(text_keys, 2):
#             # Compute intersection for each pair
#             intersection_set = self.create_intersection_set(text1, text2)
#             pairwise_intersections[(text1, text2)] = intersection_set

#         return pairwise_intersections
    
#     def calculate_total_intersection_words(self, pairwise_intersections):
#         """
#         Calculate the total number of unique words across all pairwise intersection sets.

#         Args:
#             pairwise_intersections (dict): A dictionary of pairwise intersections where
#                 keys are tuples of text pairs (text1, text2) and values are the sets of intersecting words.

#         Returns:
#             int: Total number of unique words across all intersection sets.
#         """
#         # Combine all words from all intersection sets into one set
#         all_intersection_words = set()
#         for intersection_set in pairwise_intersections.values():
#             all_intersection_words.update(intersection_set)

#         # Return the size of the combined set
#         return len(all_intersection_words)


    
#     def prepare_bo_data(self):
#         """
#         Prepares data required for BO Score calculations by collecting word counts,
#         total words, and word sets for each text. Also tracks word occurrences across texts.
#         """
#         self.word_counts = {}
#         self.total_words = {}
#         self.word_sets = {}
#         word_occurrences = {}  # Dictionary to track how many texts each word appears in

#         for file_key, report in self.file_reports.items():
#             word_stats = report['data']['word_stats']
#             word_counts = {word: count for word, count, _, _, _ in word_stats}
#             total_word_count = sum(word_counts.values())

#             self.word_counts[file_key] = word_counts
#             self.total_words[file_key] = total_word_count
#             self.word_sets[file_key] = set(word_counts.keys())

#             for word in word_counts.keys():
#                 if word not in word_occurrences:
#                     word_occurrences[word] = set()  # Use a set to track which texts the word appears in
#                 word_occurrences[word].add(file_key)

#         # Debugging: Check sample of word_occurrences
#         print(f"Sample of word_occurrences (First 20): {list(word_occurrences.items())[:20]}")

#         # Identify words that appear in at least two texts
#         self.words_in_multiple_texts = {word for word, texts in word_occurrences.items() if len(texts) >= 2}

#         # Debugging: Check results
#         words_with_count_1 = [word for word, texts in word_occurrences.items() if len(texts) == 1]
#         print(f"Sample of words_in_multiple_texts (First 20): {list(self.words_in_multiple_texts)[:20]}")
#         print(f"Total intersection words (at least 2 texts): {len(self.words_in_multiple_texts)}")
#         print(f"Words in only one text: {len(words_with_count_1)}")

#         # Debugging logs
#         logging.info(f"Total unique words in corpus: {len(word_occurrences)}")
#         logging.info(f"Words appearing in at least two texts: {len(self.words_in_multiple_texts)}")
#         logging.info(f"Words appearing in only one text: {len(words_with_count_1)}")






#     def calculate_bo_pairwise_weights(self):
#         """
#         Calculates pairwise weights for BO Scores using percentage frequencies.
#         """
#         self.pairwise_pw = {}
#         text_pairs = list(combinations(self.file_reports.keys(), 2))

#         # Counter for unique intersection words
#         unique_intersection_words = set()

#         for T1, T2 in text_pairs:
#             set1 = self.word_sets[T1]
#             set2 = self.word_sets[T2]
#             intersection = set1 & set2

#             # Add intersection words to the global counter
#             unique_intersection_words.update(intersection)

#             counts1 = self.word_counts[T1]
#             counts2 = self.word_counts[T2]
#             total_words1 = self.total_words[T1]
#             total_words2 = self.total_words[T2]

#             # Percentage frequencies for all words in T1 and T2
#             freq_percent_T1_all = {w: counts1[w] / total_words1 for w in counts1}
#             freq_percent_T2_all = {w: counts2[w] / total_words2 for w in counts2}

#             # Average percentage frequencies for normalization
#             avg_freq_T1 = np.mean(list(freq_percent_T1_all.values()))
#             avg_freq_T2 = np.mean(list(freq_percent_T2_all.values()))
#             normalization_factor_bon1 = (avg_freq_T1 + avg_freq_T2) / 2

#             # For BOn2, calculate average percentage frequency over the union
#             union_words = set1 | set2
#             freq_union = {
#                 w: (freq_percent_T1_all.get(w, 0) + freq_percent_T2_all.get(w, 0)) / 2
#                 for w in union_words
#             }
#             avg_freq_union = np.mean(list(freq_union.values()))

#             for w in intersection:
#                 freq1 = counts1[w] / total_words1
#                 freq2 = counts2[w] / total_words2
#                 pw = freq1 * freq2  # Pairwise weight using percentage frequencies

#                 # Avoid division by zero in normalization factors
#                 if normalization_factor_bon1 != 0:
#                     pw_normalized_bon1 = pw / normalization_factor_bon1
#                 else:
#                     pw_normalized_bon1 = 0

#                 if avg_freq_union != 0:
#                     pw_normalized_bon2 = pw / avg_freq_union
#                 else:
#                     pw_normalized_bon2 = 0

#                 # Store the results
#                 key = (w, T1, T2)
#                 self.pairwise_pw[key] = {
#                     'PW': pw,
#                     'PW_normalized_BOn1': pw_normalized_bon1,
#                     'PW_normalized_BOn2': pw_normalized_bon2
#                 }

#         # Log the total number of unique intersection words
#         logging.info(f"Total unique intersection words: {len(unique_intersection_words)}")


#     def aggregate_bo_scores(self):
#         """
#         Aggregates the normalized pairwise weights across all text pairs for each word.
#         """
#         self.summed_pw_bon1 = {}
#         self.summed_pw_bon2 = {}

#         for (w, T1, T2), values in self.pairwise_pw.items():
#             self.summed_pw_bon1[w] = self.summed_pw_bon1.get(w, 0) + values['PW_normalized_BOn1']
#             self.summed_pw_bon2[w] = self.summed_pw_bon2.get(w, 0) + values['PW_normalized_BOn2']

#     def compute_bo_scores(self):
#         """
#         Computes the BO Scores by preparing data, calculating pairwise weights, and aggregating results.
#         Logs information about non-zero BO Scores and verifies exclusions.
#         """
#         self.prepare_bo_data()
#         self.calculate_bo_pairwise_weights()
#         self.aggregate_bo_scores()

#         # Log the number of words with non-zero BO Scores
#         non_zero_bon1 = {w: score for w, score in self.summed_pw_bon1.items() if score > 0}
#         non_zero_bon2 = {w: score for w, score in self.summed_pw_bon2.items() if score > 0}
#         logging.info(f"Number of words with non-zero BO Score BOn1: {len(non_zero_bon1)}")
#         logging.info(f"Number of words with non-zero BO Score BOn2: {len(non_zero_bon2)}")

#         # Verify exclusion of unique words
#         unique_to_one_text = set(self.words_in_multiple_texts)
#         bon1_unique_check = [w for w in self.summed_pw_bon1.keys() if w not in unique_to_one_text]
#         bon2_unique_check = [w for w in self.summed_pw_bon2.keys() if w not in unique_to_one_text]

#         if bon1_unique_check:
#             logging.warning(f"Words in BOn1 that should not be present: {bon1_unique_check}")
#         if bon2_unique_check:
#             logging.warning(f"Words in BOn2 that should not be present: {bon2_unique_check}")

    
#     def get_bo_scores(self):
#         """
#         Returns the BO Scores for BOn1 and BOn2 normalization.

#         Returns:
#             tuple: (bo_scores_bon1, bo_scores_bon2)
#         """
#         return self.summed_pw_bon1, self.summed_pw_bon2



#     def create_word_frequency_vectors(self):
#         """
#         Creates frequency vectors for each text from the file reports.

#         Returns:
#             tuple: A dictionary mapping text names to frequency vectors and a list of all unique words across all texts.
#         """
#         # Collect all unique words across all texts
#         all_words_set = set()
#         for report in self.file_reports.values():
#             word_stats = report['data']['word_stats']
#             words = [word for word, _, _, _, _ in word_stats]
#             all_words_set.update(words)
        
#         all_words = sorted(list(all_words_set))  # Ensure consistent order

#         # Create frequency vectors for each text
#         frequency_vectors = {}
#         for file_key, report in self.file_reports.items():
#             word_counts = {word: count for word, count, _, _, _ in report['data']['word_stats']}
#             vector = [word_counts.get(word, 0) for word in all_words]
#             frequency_vectors[file_key] = vector
        
#         return frequency_vectors, all_words
    
#     def create_normalized_frequency_vectors(self, frequency_vectors):
#         """
#         Normalizes frequency vectors to create probability distributions.

#         Parameters:
#             frequency_vectors (dict): Dictionary mapping text names to frequency vectors.

#         Returns:
#             dict: Dictionary mapping text names to normalized frequency vectors.
#         """
#         normalized_vectors = {}
#         for text_name, vector in frequency_vectors.items():
#             total = sum(vector)
#             if total > 0:
#                 normalized_vector = [count / total for count in vector]
#             else:
#                 normalized_vector = vector
#             normalized_vectors[text_name] = normalized_vector
#         return normalized_vectors
    
#     @staticmethod
#     def jaccard_index(set1, set2):
#         intersection = len(set1 & set2)
#         union = len(set1 | set2)
#         return intersection / union if union != 0 else 0

#     @staticmethod
#     def dice_coefficient(set1, set2):
#         intersection = len(set1 & set2)
#         return (2 * intersection) / (len(set1) + len(set2)) if (len(set1) + len(set2) != 0) else 0

#     @staticmethod
#     def overlap_coefficient(set1, set2):
#         intersection = len(set1 & set2)
#         min_size = min(len(set1), len(set2))
#         return intersection / min_size if min_size != 0 else 0

#     @staticmethod
#     def cosine_similarity(vec1, vec2):
#         import numpy as np
#         vec1 = np.array(vec1)
#         vec2 = np.array(vec2)
#         dot_product = np.dot(vec1, vec2)
#         norm_product = np.linalg.norm(vec1) * np.linalg.norm(vec2)
#         return dot_product / norm_product if norm_product != 0 else 0

#     @staticmethod
#     def kl_divergence(p, q):
#         import numpy as np
#         p = np.array(p, dtype=np.float64) + 1e-10  # Avoid log(0)
#         q = np.array(q, dtype=np.float64) + 1e-10
#         return np.sum(p * np.log(p / q))

#     @staticmethod
#     def js_divergence(p, q):
#         import numpy as np
#         m = 0.5 * (np.array(p) + np.array(q))
#         return 0.5 * OverlapAnalyzer.kl_divergence(p, m) + 0.5 * OverlapAnalyzer.kl_divergence(q, m)

#     @staticmethod
#     def bhattacharyya_distance(p, q):
#         import numpy as np
#         p = np.array(p, dtype=np.float64)
#         q = np.array(q, dtype=np.float64)
#         coefficient = np.sum(np.sqrt(p * q))
#         return -np.log(coefficient) if coefficient > 0 else np.inf