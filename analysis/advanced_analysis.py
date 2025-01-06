import numpy as np
import logging
from itertools import combinations

##############################################################################
# Debug helper and toggle for debug messages
##############################################################################
DEBUG_MODE = False  # Set to True to enable debug logs

def debug(msg: str):
    if DEBUG_MODE:
        print(f"[DEBUG advanced_analysis] {msg}")
class OverlapAnalyzer:
    """
    The OverlapAnalyzer handles:
      1) Building word sets for actual texts (skipping 'Master Report').
      2) Generating pairwise intersections among texts.
      3) Performing optional assurance checks (unique vs. intersection).
      4) Computing BO Scores (BOn1, BOn2) across all texts.

    Usage:
      analyzer = OverlapAnalyzer(file_reports)
      analyzer.compute_bo_scores()  # aggregates final results
      bon1_dict, bon2_dict = analyzer.get_bo_scores()
    """

    def __init__(self, file_reports):
        """
        file_reports (dict):
          {
            "path/to/fileA.txt": {
              "data": {
                "word_stats": [(word, count, pct, z, logz), ...]
              }
            },
            "path/to/fileB.txt": {...},
            "Master Report": {...}  # We skip it in actual computations
          }
        """
        self.file_reports = file_reports

        # For text-based intersection logic:
        self.word_sets = {}  # text_key -> set of words (excl. Master)

        # For BO computations:
        self.word_counts = {}   # text_key -> {word: count}
        self.total_words = {}   # text_key -> sum of counts
        self.pairwise_pw = {}   # (word, T1, T2) -> { "PW":..., "BOn1":..., "BOn2":... }
        self.summed_pw_bon1 = {}  # final {word -> BO Score (BOn1)}
        self.summed_pw_bon2 = {}  # final {word -> BO Score (BOn2)}

    ###########################################################################
    # (1) Basic Intersection / Assurance logic
    ###########################################################################
    def create_word_sets_excluding_master(self):
        """
        Builds self.word_sets with each text's unique words,
        skipping any text named 'Master Report'.
        """
        debug("create_word_sets_excluding_master() invoked.")
        self.word_sets.clear()

        for text_key, report in self.file_reports.items():
            debug(f"  Checking text_key={text_key!r}")
            if text_key == "Master Report":
                debug("   -> Skipped Master Report.")
                continue
            word_stats = report["data"]["word_stats"]  # list of (word, count, pct, z, logz)
            words = [ws[0] for ws in word_stats]       # extract the 'word'
            self.word_sets[text_key] = set(words)
            debug(f"   -> Found {len(words)} words in {text_key!r}")

        debug(f" -> Built word_sets for {len(self.word_sets)} texts (excluding Master).")

    def generate_pairwise_intersections(self):
        """
        Create intersection sets for all pairs of actual texts.
        Returns: dict { (text1, text2): set_of_shared_words }
        """
        debug("generate_pairwise_intersections() invoked.")
        pairwise_intersections = {}
        text_keys = list(self.word_sets.keys())  # no Master

        for T1, T2 in combinations(text_keys, 2):
            intersection = self.word_sets[T1] & self.word_sets[T2]
            pairwise_intersections[(T1, T2)] = intersection
            debug(f"   -> Intersection of '{T1}' and '{T2}' has {len(intersection)} words.")

        debug(f" -> Generated {len(pairwise_intersections)} pairwise intersections.")
        return pairwise_intersections

    def calculate_total_intersection_words(self, pairwise_intersections):
        """
        Given the dictionary of intersections, find how many unique
        words appear in *any* intersection across all text pairs.
        """
        debug("calculate_total_intersection_words() invoked.")
        all_intersection_words = set()
        for inter_set in pairwise_intersections.values():
            all_intersection_words.update(inter_set)

        result = len(all_intersection_words)
        debug(f" -> total_intersection_words = {result}")
        return result

    def calculate_assurance_metrics(self, pairwise_intersections):
        """
        Checks that the total unique words across all texts is
        the sum of intersection words + unique-to-single-text words.

        Returns a dictionary with details.
        """
        debug("calculate_assurance_metrics() invoked.")
        # union of all intersection sets
        all_intersection_words = set()
        for inter_set in pairwise_intersections.values():
            all_intersection_words.update(inter_set)
        total_intersection_words = len(all_intersection_words)

        # words unique to a single text
        unique_to_single_text = set()
        for text, wordset in self.word_sets.items():
            other_texts = set(self.word_sets.keys()) - {text}
            combined_others = set.union(*(self.word_sets[o] for o in other_texts)) if other_texts else set()
            # difference => words that appear in text but not in any other
            unique_to_single_text.update(wordset - combined_others)
        total_unique_to_single_text = len(unique_to_single_text)

        # total unique across all actual texts
        if self.word_sets:
            total_unique_words_in_corpus = len(set.union(*self.word_sets.values()))
        else:
            total_unique_words_in_corpus = 0

        # check
        assurance_passed = (
            total_intersection_words + total_unique_to_single_text == total_unique_words_in_corpus
        )

        debug(f" -> total_unique_words_in_corpus={total_unique_words_in_corpus}, "
              f"total_intersection_words={total_intersection_words}, "
              f"total_unique_to_single_text={total_unique_to_single_text}, "
              f"assurance_passed={assurance_passed}")

        return {
            "total_unique_words_in_corpus": total_unique_words_in_corpus,
            "total_intersection_words": total_intersection_words,
            "total_unique_to_single_text": total_unique_to_single_text,
            "assurance_passed": assurance_passed
        }

    ###########################################################################
    # (2) BO Scores (BOn1, BOn2)
    ###########################################################################
    def prepare_bo_data(self):
        """
        Gathers word_counts & total_words for each actual text (excl. Master).
        """
        debug("prepare_bo_data() invoked.")
        self.word_counts.clear()
        self.total_words.clear()

        for text_key, report in self.file_reports.items():
            if text_key == "Master Report":
                continue
            word_stats = report["data"]["word_stats"]
            counts = {ws[0]: ws[1] for ws in word_stats}
            total_count = sum(counts.values())

            self.word_counts[text_key] = counts
            self.total_words[text_key] = total_count
            debug(f"   -> {text_key!r} has total_word_count={total_count}")

        debug(f" -> Prepared data for {len(self.word_counts)} texts (excluding Master).")

    def calculate_bo_pairwise_weights(self):
        """
        For each pair (T1, T2), compute pairwise weight (PW),
        then do BOn1/BOn2 normalizations. Results go into self.pairwise_pw.
        """
        debug("calculate_bo_pairwise_weights() invoked.")
        self.pairwise_pw.clear()

        text_keys = list(self.word_sets.keys())
        debug(f" -> We'll compare {len(text_keys)} texts in pairs.")

        for T1, T2 in combinations(text_keys, 2):
            intersection = self.word_sets[T1] & self.word_sets[T2]
            if not intersection:
                debug(f"   -> T1={T1!r}, T2={T2!r} had NO intersection.")
                continue

            counts1 = self.word_counts[T1]
            counts2 = self.word_counts[T2]
            total1 = self.total_words[T1]
            total2 = self.total_words[T2]

            freq1 = {w: (counts1[w]/total1) for w in counts1}
            freq2 = {w: (counts2[w]/total2) for w in counts2}

            avg_f1 = np.mean(list(freq1.values())) if freq1 else 0.0
            avg_f2 = np.mean(list(freq2.values())) if freq2 else 0.0
            norm_bon1 = (avg_f1 + avg_f2) / 2.0 if (avg_f1 + avg_f2) else 0.0

            union_words = self.word_sets[T1] | self.word_sets[T2]
            union_vals = []
            for w in union_words:
                p1 = freq1.get(w, 0.0)
                p2 = freq2.get(w, 0.0)
                union_vals.append((p1 + p2)/2.0)
            avg_union = np.mean(union_vals) if union_vals else 0.0

            debug(f"   -> T1={T1!r}, T2={T2!r}, intersection_size={len(intersection)}, "
                  f"norm_bon1={norm_bon1:.4f}, avg_union={avg_union:.4f}")

            for w in intersection:
                p1 = freq1[w]
                p2 = freq2[w]
                pw = p1 * p2
                bon1_val = pw / norm_bon1 if norm_bon1 else 0.0
                bon2_val = pw / avg_union if avg_union else 0.0

                self.pairwise_pw[(w, T1, T2)] = {
                    "PW": pw,
                    "BOn1": bon1_val,
                    "BOn2": bon2_val
                }

        debug(f" -> Calculated PW for {len(self.pairwise_pw)} (word, T1, T2) combos.")

    def aggregate_bo_scores(self):
        """
        Sum pairwise BOn1/BOn2 across all (T1, T2).
        """
        debug("aggregate_bo_scores() invoked.")
        self.summed_pw_bon1.clear()
        self.summed_pw_bon2.clear()

        for (w, T1, T2), vals in self.pairwise_pw.items():
            self.summed_pw_bon1[w] = self.summed_pw_bon1.get(w, 0.0) + vals["BOn1"]
            self.summed_pw_bon2[w] = self.summed_pw_bon2.get(w, 0.0) + vals["BOn2"]

        debug(f" -> Aggregated BOn1 for {len(self.summed_pw_bon1)} words, "
              f"BOn2 for {len(self.summed_pw_bon2)} words.")

    def compute_bo_scores(self):
        """
        1) create_word_sets_excluding_master()
        2) prepare_bo_data()
        3) calculate_bo_pairwise_weights()
        4) aggregate_bo_scores()
        """
        debug("compute_bo_scores() invoked.")
        self.create_word_sets_excluding_master()
        self.prepare_bo_data()
        self.calculate_bo_pairwise_weights()
        self.aggregate_bo_scores()
        debug(" -> compute_bo_scores() finished successfully.")

    def get_bo_scores(self):
        """
        Return (bon1_dict, bon2_dict).
        """
        debug("get_bo_scores() invoked. Returning final results.")
        return (self.summed_pw_bon1, self.summed_pw_bon2)

##############################################################################
# External Helper
##############################################################################
def compute_bo_scores(file_reports):
    """
    High-level convenience function. Instantiates OverlapAnalyzer,
    calls compute_bo_scores(), and returns (bon1_dict, bon2_dict).
    """
    debug("compute_bo_scores() called from outside. Building OverlapAnalyzer.")
    analyzer = OverlapAnalyzer(file_reports)
    analyzer.compute_bo_scores()
    bon1, bon2 = analyzer.get_bo_scores()
    debug(f" -> DONE. returning bo1(len={len(bon1)}), bo2(len={len(bon2)})")
    return bon1, bon2
