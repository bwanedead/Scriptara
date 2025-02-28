class CorpusReportManager:
    """
    Manages analysis reports for multiple corpora, allowing each visualization
    to access data for its specific corpus regardless of which corpus is currently active.
    """
    
    def __init__(self):
        # Main storage structure - a dictionary mapping corpus names to their report data
        # {corpus_name: {file_path: {'data': {...}}}}
        self.corpus_reports = {}
        
    def get_report_for_corpus(self, corpus_name):
        """
        Retrieve the analysis report for a specific corpus.
        
        Args:
            corpus_name (str): The name of the corpus
            
        Returns:
            dict: The report data for this corpus, or an empty dict if not found
        """
        if corpus_name in self.corpus_reports:
            return self.corpus_reports[corpus_name]
        return {}
        
    def update_report_for_corpus(self, corpus_name, report_data):
        """
        Store or update the analysis results for a corpus.
        
        Args:
            corpus_name (str): The name of the corpus
            report_data (dict): The analysis results to store
        """
        self.corpus_reports[corpus_name] = report_data
        
    def remove_corpus_report(self, corpus_name):
        """
        Remove a corpus report when the corpus is deleted.
        
        Args:
            corpus_name (str): The name of the corpus to remove
        """
        if corpus_name in self.corpus_reports:
            del self.corpus_reports[corpus_name]
            
    def has_report_for_corpus(self, corpus_name):
        """
        Check if a report exists for the specified corpus.
        
        Args:
            corpus_name (str): The name of the corpus to check
            
        Returns:
            bool: True if a report exists, False otherwise
        """
        return corpus_name in self.corpus_reports
    
    def list_available_reports(self):
        """
        Get a list of corpus names that have reports available.
        
        Returns:
            list: Names of corpora with reports
        """
        return list(self.corpus_reports.keys())
