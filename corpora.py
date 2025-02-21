class Corpus:
    def __init__(self, name, files=None):
        """
        Initialize a corpus with a unique name and an optional list of files.
        """
        self.name = name
        self.files = files if files is not None else []

    def add_file(self, file_path):
        """
        Add a new file to the corpus if it is not already present.
        """
        if file_path not in self.files:
            self.files.append(file_path)

    def remove_file(self, file_path):
        """
        Remove a file from the corpus if it exists.
        """
        if file_path in self.files:
            self.files.remove(file_path)

    def get_files(self):
        """
        Return the list of files in the corpus.
        """
        return self.files 