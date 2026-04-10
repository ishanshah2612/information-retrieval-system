# main_ui.py (or your preferred filename)

import re
import string
from document import Document
from test_wrapper import (
    Document,
    stem_term,
    load_documents_from_url,
    remove_stopwords_by_list,
    remove_stopwords_by_frequency,
    linear_boolean_search,
    boolean_conjunction_search,     # <-- ADD THIS LINE
    vector_space_search,
    precision_recall
)

# Load ground truth mapping for evaluation (query -> set of doc IDs)
def load_ground_truth(collection_origin: str) -> dict:
    """
    Loads the ground truth file based on the collection's origin.
    The ground truth file should be in the format: query:doc_id1,doc_id2,...
    e.g., "the fox:1,5,12"
    """
    gt_files = {
        "Aesop's Fables": "aesop_gt.txt",
        "Grimm's Fairy Tales": "grimm_gt.txt"
    }
    
    filename = gt_files.get(collection_origin)
    if not filename:
        return {} # No ground truth file for this collection

    ground_truth = {}
    try:
        with open(filename, 'r') as f:
            for line in f:
                if ':' in line:
                    query, doc_ids_str = line.strip().split(':', 1)
                    doc_ids = {int(doc_id) for doc_id in doc_ids_str.split(',') if doc_id}
                    ground_truth[query.strip()] = doc_ids
    except FileNotFoundError:
        print(f"\nWarning: Ground truth file '{filename}' not found.")
    except Exception as e:
        print(f"\nError reading ground truth file: {e}")
        
    return ground_truth

# Display the main menu and return user choice
def display_menu():
    print("\n===== Information Retrieval System (PR03) =====")
    print("1. Load document collection from URL")
    print("2. Search Collection (Boolean / VSM)")
    print("3. Apply stop word removal (list-based)")
    print("4. Apply stop word removal (frequency-based)")
    print("5. Display document collection info")
    print("6. Exit")
    return input("Enter your choice (1-6): ")

# UI to load a new document collection from the web
def load_collection_ui():
    print("\n--- Load Document Collection ---")
    # Default values for quick testing with known ground truth files
    print("Hint: Try 'aesop.txt' or 'grimm.txt' from Project Gutenberg.")
    url = input("Enter URL (e.g., https://www.gutenberg.org/files/11339/11339-0.txt for Grimm): ")
    author = input("Enter author name (e.g., Brothers Grimm): ")
    origin = input("Enter origin title (e.g., Grimm's Fairy Tales): ")
    start_line = int(input("Enter start line number: "))
    end_line = int(input("Enter end line number: "))
    
    # A robust pattern for Gutenberg fables/tales
    pattern = re.compile(r'\b([A-Z][A-Z\s]+(?:\s[IVXLC]+\.|\s[1-9]+\.)?)\b\n\n(.*?)(?=\n\n\b[A-Z][A-Z\s]+(?:\s[IVXLC]+\.|\s[1-9]+\.)?\b|\Z)', re.DOTALL)
    
    try:
        docs = load_documents_from_url(url, author, origin, start_line, end_line, pattern)
        print(f"\nSuccessfully loaded {len(docs)} documents from '{origin}'.")
        return docs
    except Exception as e:
        print(f"\nError loading documents: {e}")
        return None

# UI for searching the collection and running evaluation
def search_ui(collection, ground_truth):
    if not collection:
        print("\nNo document collection loaded! Please load a collection first.")
        return

    print("\n--- Search Collection ---")
    model = input("Select search model:\n (1) Boolean (Conjunction)\n (2) Vector Space Model\nEnter choice: ")
    query = input("Enter search query (terms separated by spaces): ").lower()
    use_filtered = input("Use stopword-filtered terms? (y/n): ").lower() == 'y'
    use_stemming = input("Enable stemming? (y/n): ").lower() == 'y'

    results = []
    if model == '1':
        print("\nPerforming Boolean search...")
        results = boolean_conjunction_search(query, collection, use_filtered, use_stemming)
    elif model == '2':
        print("\nPerforming Vector Space search...")
        results = vector_space_search(query, collection, use_filtered, use_stemming)
    else:
        print("Invalid model choice.")
        return

    print(f"\nFound {len(results)} matching documents for query: '{query}'")
    for score, doc in results:
        # For VSM, format the score. For Boolean, it's just 1.
        score_str = f"{score:.4f}" if isinstance(score, float) else str(score)
        print(f"  [{score_str}] Doc ID {doc.document_id}: {doc.title}")

    # --- Evaluation Step ---
    print("\n--- Evaluation ---")
    if query in ground_truth:
        relevant_docs = ground_truth[query]
        retrieved_docs = {doc.document_id for score, doc in results if score > 0}
        
        precision, recall = precision_recall(list(retrieved_docs), list(relevant_docs))
        
        print(f"Ground truth found for this query.")
        print(f"Precision: {precision:.4f}")
        print(f"Recall:    {recall:.4f}")
    else:
        print("No ground truth available for this specific query.")

# UI to remove stopwords using a provided word list
def stopwords_list_ui(collection):
    if not collection:
        print("\nNo document collection loaded!")
        return
    
    print("\n--- Stop Word Removal (List) ---")
    file_path = input("Enter path to stop words file (or press Enter for default 'englishST.txt'): ")
    
    try:
        if not file_path:
            file_path = "englishST.txt"
        
        with open(file_path, 'r') as f:
            stopwords = set(line.strip().lower() for line in f)
        
        for doc in collection:
            remove_stopwords_by_list(doc, stopwords)
        
        print(f"\nApplied stop word removal to {len(collection)} documents.")
    except Exception as e:
        print(f"\nError applying stop words: {e}")

# UI to remove stopwords by frequency (common/rare) in the collection
def stopwords_frequency_ui(collection):
    if not collection:
        print("\nNo document collection loaded!")
        return
    
    print("\n--- Stop Word Removal (Frequency) ---")
    try:
        common = float(input("Enter common frequency threshold (e.g., 0.9): "))
        rare = float(input("Enter rare frequency threshold (e.g., 0.02): "))
        
        for doc in collection:
            remove_stopwords_by_frequency(doc, collection, rare, common)
        
        print(f"\nApplied frequency-based stop word removal to {len(collection)} documents.")
    except Exception as e:
        print(f"\nError applying frequency-based stop words: {e}")

# Display basic info about loaded collection (count, sample docs)
def display_collection_info(collection):
    if not collection:
        print("\nNo document collection loaded!")
        return
    
    print("\n--- Document Collection Info ---")
    print(f"Number of documents: {len(collection)}")
    if collection:
        print(f"Collection Origin: {collection[0].origin}")
        print(f"Sample documents:")
        for i, doc in enumerate(collection[:3]):
            filtered_info = f"({len(doc._filtered_terms)} filtered terms)" if doc._filtered_terms else ""
            print(f"  {i+1}. Doc ID {doc.document_id}: {doc.title} ({len(doc.terms)} terms) {filtered_info}")
        if len(collection) > 3:
            print(f"  ... and {len(collection)-3} more.")

# The main event loop for the CLI system
def main():
    collection = None
    ground_truth = {}
    
    while True:
        choice = display_menu()
        
        if choice == '1':
            collection = load_collection_ui()
            if collection:
                # Load ground truth automatically when a collection is loaded
                ground_truth = load_ground_truth(collection[0].origin)
        elif choice == '2':
            search_ui(collection, ground_truth)
        elif choice == '3':
            stopwords_list_ui(collection)
        elif choice == '4':
            stopwords_frequency_ui(collection)
        elif choice == '5':
            display_collection_info(collection)
        elif choice == '6':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

# Run CLI interface if this script is executed directly
if __name__ == "__main__":
    main()