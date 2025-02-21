# corpora.py

class Corpus:
    def __init__(self, name="", file_paths=None):
        """
        Initialize a new Corpus with a unique name and an optional list of file paths.
        
        Args:
            name (str): The initial name for this corpus (e.g., "Corpus 1").
            file_paths (list, optional): A list of file paths belonging to this corpus.
        """
        self.name = name
        self.files = file_paths if file_paths else []

    def add_file(self, file_path):
        """
        Add a file to the corpus if it's not already present.
        
        Args:
            file_path (str): The path of the file to add.
        """
        if file_path not in self.files:
            self.files.append(file_path)

    def remove_file(self, file_path):
        """
        Remove a file from the corpus.
        
        Args:
            file_path (str): The path of the file to remove.
        """
        if file_path in self.files:
            self.files.remove(file_path)

    def get_files(self):
        """
        Return the list of files in the corpus.
        
        Returns:
            list: The file paths belonging to the corpus.
        """
        return self.files

    def rename(self, new_name):
        """
        Rename the corpus.
        
        Args:
            new_name (str): The new name for this corpus.
        """
        self.name = new_name

    def __str__(self):
        """String representation showing name and number of files."""
        return f"{self.name} ({len(self.files)} files)"
