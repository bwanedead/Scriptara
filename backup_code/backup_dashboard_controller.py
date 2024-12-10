
# import logging
# from ui.dashboard_ui import DashboardWindow
# from analysis.advanced_analysis import (OverlapAnalyzer)

# class DashboardController:
#     def __init__(self, main_controller):
#         self.main_controller = main_controller
#         self._similarity_results = None
#         self.view = DashboardWindow(self)
        

#     def show(self):
#         """Show the dashboard and prepare similarity metrics."""
#         self.compute_similarity_metrics()  # Compute overlap metrics before showing the dashboard
#         self.view.show()


#     @property
#     def imported_files(self):
#         return self.main_controller.imported_files

#     @property
#     def word_frequencies(self):
#         return self.main_controller.word_frequencies

#     @property
#     def percentage_frequencies(self):
#         return self.main_controller.percentage_frequencies

#     @property
#     def z_scores(self):
#         return self.main_controller.z_scores
    
#     @property
#     def file_reports(self):
#         # Pass the file reports from the MainController
#         return self.main_controller.file_reports
    
#     @property
#     def similarity_results(self):
#         """Access the similarity results, computing them if necessary."""
#         if self._similarity_results is None:
#             logging.info("Computing similarity metrics as they are not available.")
#             self.compute_similarity_metrics()
#         return self._similarity_results



#     def compute_similarity_metrics(self):
#         """Computes similarity metrics between texts and BO Scores."""
#         analyzer = OverlapAnalyzer(self.file_reports)
#         analyzer.create_word_sets()
#         frequency_vectors, _ = analyzer.create_word_frequency_vectors()
#         normalized_vectors = analyzer.create_normalized_frequency_vectors(frequency_vectors)

#         # Generate similarity results
#         similarity_results = {
#             'Jaccard Index': {},
#             'Dice Coefficient': {},
#             'Overlap Coefficient': {},
#             'Cosine Similarity': {},
#             'KL Divergence': {},
#             'JS Divergence': {},
#             'Bhattacharyya Distance': {},
#             'BO Score BOn1': {},  # Initialize storage for BO Scores
#             'BO Score BOn2': {}
#         }

#         texts = list(self.file_reports.keys())

#         # Calculate traditional similarity metrics
#         for i in range(len(texts)):
#             for j in range(i + 1, len(texts)):
#                 text1, text2 = texts[i], texts[j]

#                 # Set-based metrics
#                 set1, set2 = analyzer.word_sets[text1], analyzer.word_sets[text2]
#                 similarity_results['Jaccard Index'][(text1, text2)] = analyzer.jaccard_index(set1, set2)
#                 similarity_results['Dice Coefficient'][(text1, text2)] = analyzer.dice_coefficient(set1, set2)
#                 similarity_results['Overlap Coefficient'][(text1, text2)] = analyzer.overlap_coefficient(set1, set2)

#                 # Vector-based metrics
#                 vec1, vec2 = frequency_vectors[text1], frequency_vectors[text2]
#                 norm_vec1, norm_vec2 = normalized_vectors[text1], normalized_vectors[text2]
#                 similarity_results['Cosine Similarity'][(text1, text2)] = analyzer.cosine_similarity(vec1, vec2)
#                 similarity_results['KL Divergence'][(text1, text2)] = analyzer.kl_divergence(norm_vec1, norm_vec2)
#                 similarity_results['JS Divergence'][(text1, text2)] = analyzer.js_divergence(norm_vec1, norm_vec2)
#                 similarity_results['Bhattacharyya Distance'][(text1, text2)] = analyzer.bhattacharyya_distance(norm_vec1, norm_vec2)

#         # Compute BO Scores using OverlapAnalyzer
#         analyzer.compute_bo_scores()
#         bo_scores_bon1, bo_scores_bon2 = analyzer.get_bo_scores()

#         # Store BO Scores in similarity_results
#         similarity_results['BO Score BOn1'] = bo_scores_bon1
#         similarity_results['BO Score BOn2'] = bo_scores_bon2

#         # Store results in the internal attribute
#         self._similarity_results = similarity_results
