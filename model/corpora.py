# corpora.py

class Corpus:
    def __init__(self, name, file_paths=None):
        """
        Initialize a new Corpus with a unique name and an optional list of file paths.
        
        Args:
            name (str): The initial name for this corpus (e.g., "Corpus 1").
            file_paths (list, optional): A list of file paths belonging to this corpus.
        """
        self.name = name
        self.file_paths = file_paths if file_paths is not None else []

    def add_file(self, file_path):
        """
        Add a file to the corpus if it isn't already present.
        
        Args:
            file_path (str): The path of the file to add.
        """
        if file_path not in self.file_paths:
            self.file_paths.append(file_path)

    def remove_file(self, file_path):
        """
        Remove a file from the corpus.
        
        Args:
            file_path (str): The path of the file to remove.
        """
        if file_path in self.file_paths:
            self.file_paths.remove(file_path)

    def get_files(self):
        """
        Return the list of file paths for this corpus.
        
        Returns:
            list: The file paths belonging to the corpus.
        """
        return self.file_paths

    def rename(self, new_name):
        """
        Rename the corpus.
        
        Args:
            new_name (str): The new name for this corpus.
        """
        self.name = new_name

    def __str__(self):
        return f"Corpus(name={self.name}, num_files={len(self.file_paths)})"
