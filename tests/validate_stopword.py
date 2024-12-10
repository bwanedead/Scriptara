import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.word_analyzer import read_and_preprocess_file



def test_stopword_filtering():
    """
    Test if the read_and_preprocess_file function correctly filters out standalone 's'.
    """
    # Define a test input
    test_text = """
    It's simple: this is a test. John's examples are good, but s shouldn't be here.
    """

    # Write the test input to a temporary file
    test_file_path = "test_input.txt"
    with open(test_file_path, "w", encoding="utf-8") as test_file:
        test_file.write(test_text)

    # Call the function to be tested
    words, punctuation = read_and_preprocess_file(test_file_path)

    # Remove the test file after processing
    os.remove(test_file_path)

    # Validate the results
    print("Words extracted:")
    print(words)

    print("\nPunctuation extracted:")
    print(punctuation)

    # Assert that 's' is not in the list of words
    assert 's' not in words, "'s' should have been filtered out as a stopword."
    print("\nValidation passed: Standalone 's' is correctly removed.")

# Run the test
if __name__ == "__main__":
    test_stopword_filtering()
