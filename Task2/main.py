import string
from document import Document
from test_wrapper import (
    load_documents_from_url,
    linear_boolean_search,
    remove_stopwords_by_list,
    remove_stopwords_by_frequency
)

def display_menu():
    print("\n===== Information Retrieval System =====")
    print("1. Load document collection from URL")
    print("2. Search for term in collection")
    print("3. Apply stop word removal (list-based)")
    print("4. Apply stop word removal (frequency-based)")
    print("5. Display document collection info")
    print("6. Exit")
    return input("Enter your choice (1-6): ")

def load_collection_ui():
    print("\n--- Load Document Collection ---")
    url = input("Enter URL of text file: ")
    author = input("Enter author name: ")
    origin = input("Enter origin/source title: ")
    start_line = int(input("Enter start line number: "))
    end_line = int(input("Enter end line number: "))
    
    # Simple pattern that works for most Gutenberg-style documents
    pattern = re.compile(r'([^\n]+)\n\n(.*?)(?=\n{3,}[^\n]+\n\n|\Z)', re.DOTALL)
    
    try:
        docs = load_documents_from_url(url, author, origin, start_line, end_line, pattern)
        print(f"\nSuccessfully loaded {len(docs)} documents.")
        return docs
    except Exception as e:
        print(f"\nError loading documents: {e}")
        return None

def search_ui(collection):
    if not collection:
        print("No document collection loaded!")
        return
    
    print("\n--- Search Collection ---")
    term = input("Enter search term: ")
    use_filtered = input("Search in filtered terms? (y/n): ").lower() == 'y'
    
    results = linear_boolean_search(term, collection, use_filtered)
    
    print(f"\nFound {len([r for r in results if r[0] > 0])} matching documents:")
    for score, doc in results:
        if score > 0:
            print(f"[{score}] {doc.title}")

def stopwords_list_ui(collection):
    if not collection:
        print("No document collection loaded!")
        return
    
    print("\n--- Stop Word Removal (List) ---")
    file_path = input("Enter path to stop words file (or press Enter for default): ")
    
    try:
        if not file_path:
            # Use the default file that comes with the tests
            import os
            file_path = os.path.join(os.path.dirname(__file__), "englishST.txt")
        
        with open(file_path, 'r') as f:
            stopwords = set(line.strip().lower() for line in f)
        
        for doc in collection:
            remove_stopwords_by_list(doc, stopwords)
        
        print(f"Applied stop word removal to {len(collection)} documents.")
    except Exception as e:
        print(f"Error applying stop words: {e}")

def stopwords_frequency_ui(collection):
    if not collection:
        print("No document collection loaded!")
        return
    
    print("\n--- Stop Word Removal (Frequency) ---")
    try:
        common = float(input("Enter common frequency threshold (e.g., 0.9): "))
        rare = float(input("Enter rare frequency threshold (e.g., 0.2): "))
        
        for doc in collection:
            remove_stopwords_by_frequency(doc, collection, common, rare)
        
        print(f"Applied frequency-based stop word removal to {len(collection)} documents.")
    except Exception as e:
        print(f"Error applying frequency-based stop words: {e}")

def display_collection_info(collection):
    if not collection:
        print("No document collection loaded!")
        return
    
    print("\n--- Document Collection Info ---")
    print(f"Number of documents: {len(collection)}")
    print(f"Sample documents:")
    for i, doc in enumerate(collection[:3]):
        print(f"{i+1}. {doc.title} ({len(doc.terms)} terms)")
    print(f"... and {max(0, len(collection)-3)} more")

def main():
    collection = None
    
    while True:
        choice = display_menu()
        
        if choice == '1':
            collection = load_collection_ui()
        elif choice == '2':
            search_ui(collection)
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

if __name__ == "__main__":
    import re
    main()