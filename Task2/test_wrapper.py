# Information Retrieval - Practical Task 2
# Wrapper for Unit Tests
# Version 1.1 (2025-06-04)

# You must implement this file so that the test suite can run your code.
# This file acts as a bridge between your individual implementation and the expected interface.

# You are free to organize your own code however you want - but make sure
# that the following three functions are importable and behave as specified below.

# Information Retrieval - Practical Task 2
# Wrapper for Unit Tests
# Version 1.1 (2025-06-04)

# You must implement this file so that the test suite can run your code.
# This file acts as a bridge between your individual implementation and the expected interface.

# You are free to organize your own code however you want - but make sure
# that the following three functions are importable and behave as specified below.

from document import Document
from re import Pattern
import re
import urllib.request
from typing import List, Tuple
from collections import defaultdict
import string


def load_documents_from_file(filepath, author, origin, start_line, end_line, search_pattern):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

# This function removes stopwords from a document.
def remove_stopwords_by_list(doc: Document, stopwords: set[str]):
    filtered = []
    for term in doc.terms:
        # Make the word lowercase and remove punctuation
        clean_term = term.lower().translate(str.maketrans('', '', string.punctuation))
        # Only keep the word if it's not a stopword
        if clean_term and clean_term not in stopwords:
            filtered.append(clean_term)
    # Save the filtered words in the document
    doc._filtered_terms = filtered

# This function removes words that are too common or too rare in all documents.
def remove_stopwords_by_frequency(doc: Document, collection: List[Document], 
                                 common_frequency: float, rare_frequency: float):
    term_counts = defaultdict(int)
    total_docs = len(collection)
    # Count how many documents each word appears in
    for document in collection:
        unique_terms_in_doc = set()
        for term in document.terms:
            clean_term = term.lower().translate(str.maketrans('', '', string.punctuation))
            if clean_term:
                unique_terms_in_doc.add(clean_term)
        for term in unique_terms_in_doc:
            term_counts[term] += 1
    # Calculate how common each word is
    term_frequencies = {term: count / total_docs for term, count in term_counts.items()}
    terms_to_filter = set()
    # Mark words that are too common or too rare
    for term, freq in term_frequencies.items():
        if freq >= common_frequency or freq <= rare_frequency:
            terms_to_filter.add(term)
    filtered = []
    # Only keep words that are not too common or too rare
    for term in doc.terms:
        clean_term = term.lower().translate(str.maketrans('', '', string.punctuation))
        if clean_term and clean_term not in terms_to_filter:
            filtered.append(clean_term)
    # Save the filtered words in the document
    doc._filtered_terms = filtered

# This function downloads a text file from the internet and splits it into documents.
def load_documents_from_url(url: str, author: str, origin: str, 
                           start_line: int, end_line: int,
                           search_pattern: Pattern[str]) -> List[Document]:
    # Download the text from the URL
    with urllib.request.urlopen(url) as response:
        text = response.read().decode('utf-8')
    
    # Use only the lines we want
    lines = text.splitlines()
    if end_line > len(lines):
        end_line = len(lines)
    relevant_lines = lines[start_line:end_line]
    relevant_text = '\n'.join(relevant_lines)
    
    # Find all parts (like chapters or stories) using the pattern
    matches = search_pattern.findall(relevant_text)
    documents = []
    
    for i, (title, content) in enumerate(matches):
        # Clean up the content
        clean_content = ' '.join(content.split())
        
        # Split the content into words
        terms = []
        for word in clean_content.split():
            # Remove punctuation and make lowercase
            clean_word = word.translate(str.maketrans('', '', string.punctuation))
            if clean_word:
                terms.append(clean_word.lower())
        
        # Create a Document object for this part
        doc = Document(
            document_id=i,
            title=title.strip(),
            raw_text=clean_content,
            terms=terms,
            author=author,
            origin=origin
        )
        documents.append(doc)
    
    return documents

# This function searches for a word in all documents and shows which documents have it.
def linear_boolean_search(term: str, collection: List[Document], 
                         stopword_filtered: bool = False) -> List[Tuple[int, Document]]:
    results = []
    # Make the search word lowercase and remove punctuation
    clean_search_term = term.lower().translate(str.maketrans('', '', string.punctuation))
    
    for doc in collection:
        # Use filtered words if asked, otherwise use all words
        terms_to_search = doc._filtered_terms if stopword_filtered else doc.terms
        
        # Check if the word is in the document
        found = any(
            clean_search_term == 
            doc_term.lower().translate(str.maketrans('', '', string.punctuation))
            for doc_term in terms_to_search
        )
        
        # 1 if found, 0 if not found
        results.append((1 if found else 0, doc))
    
    # Show documents with the word first
    return sorted(results, key=lambda x: -x[0])
