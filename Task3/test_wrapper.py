import re
import string
import math
import urllib.request
from typing import List, Tuple
from collections import defaultdict, Counter

class Document:
    def __init__(self, document_id: int, title: str, raw_text: str, terms: List[str], author: str, origin: str):
        self.document_id = document_id
        self.title = title
        self.raw_text = raw_text
        self.terms = terms
        self.author = author
        self.origin = origin
        self._filtered_terms = []

### Porter Stemmer (unchanged) ###
def stem_term(word):
    word = word.lower()
    if len(word) <= 2: return word
    vowels = 'aeiou'
    def cons(w, i):
        if w[i] in vowels: return False
        if w[i] == 'y': return i == 0 or not cons(w, i-1)
        return True
    def m(w):
        n, i, L = 0, 0, len(w)
        while i < L and cons(w, i): i+=1
        while i < L:
            while i < L and not cons(w, i): i+=1
            while i < L and cons(w, i): i+=1; n+=1
        return n
    def contains_vowel(w): return any(not cons(w, i) for i in range(len(w)))
    def doublec(w): return len(w) > 1 and w[-1] == w[-2] and cons(w, -1)
    def cvc(w): return len(w) > 2 and cons(w, -1) and not cons(w, -2) and cons(w, -3) and w[-1] not in 'wxy'
    if word.endswith("sses"): word = word[:-2]
    elif word.endswith("ies"): word = word[:-2]
    elif word.endswith("ss"): pass
    elif word.endswith("s"): word = word[:-1]
    flag = False
    if word.endswith("eed"):
        if m(word[:-3]) > 0: word = word[:-1]
    elif word.endswith("ed"):
        stem = word[:-2]
        if contains_vowel(stem): word = stem; flag = True
    elif word.endswith("ing"):
        stem = word[:-3]
        if contains_vowel(stem): word = stem; flag = True
    if flag:
        if word.endswith(("at", "bl", "iz")): word += "e"
        elif doublec(word) and not word.endswith(("l", "s", "z")): word = word[:-1]
        elif m(word) == 1 and cvc(word): word += "e"
    if word.endswith("y") and contains_vowel(word[:-1]): word = word[:-1] + "i"
    suf2 = {"ational":"ate","tional":"tion","enci":"ence","anci":"ance","izer":"ize","abli":"able","alli":"al","entli":"ent","eli":"e",
            "ousli":"ous","ization":"ize","ation":"ate","ator":"ate","alism":"al","iveness":"ive","fulness":"ful","ousness":"ous",
            "aliti":"al","iviti":"ive","biliti":"ble"}
    for s, r in suf2.items():
        if word.endswith(s) and m(word[:-len(s)]) > 0:
            word = word[:-len(s)]+r; break
    suf3 = {"icate":"ic","ative":"","alize":"al","iciti":"ic","ical":"ic","ful":"","ness":""}
    for s, r in suf3.items():
        if word.endswith(s) and m(word[:-len(s)]) > 0:
            word = word[:-len(s)]+r; break
    suf4 = ["al","ance","ence","er","ic","able","ible","ant","ement","ment","ent","ion","ou","ism","ate","iti","ous","ive","ize"]
    for s in suf4:
        if word.endswith(s):
            stem = word[:-len(s)]
            if m(stem) > 1:
                if s == "ion":
                    if stem.endswith(("s", "t")): word = stem
                else: word = stem
            break
    if word.endswith("e"):
        stem = word[:-1]
        if m(stem)>1 or (m(stem)==1 and not cvc(stem)): word = stem
    if m(word) > 1 and doublec(word) and word.endswith("l"): word = word[:-1]
    return word

def remove_stopwords_by_list(doc: Document, stopwords: set[str]):
    stopwords_lower = {w.lower() for w in stopwords}
    filtered = []
    for term in doc.terms:
        clean = term.lower().translate(str.maketrans('', '', string.punctuation))
        if clean and clean not in stopwords_lower:
            filtered.append(clean)
    doc._filtered_terms = filtered

def remove_stopwords_by_frequency(doc: Document, collection: List[Document], rare_frequency: float = 0.02, common_frequency: float = 0.9):
    term_counts = defaultdict(int)
    total_docs = len(collection)
    for d in collection:
        unique_terms = {t.lower().translate(str.maketrans('', '', string.punctuation)) for t in d.terms if t}
        for t in unique_terms:
            term_counts[t] += 1
    
    frequencies = {term: count / total_docs for term, count in term_counts.items()}
    to_filter = {term for term, freq in frequencies.items() if freq >= common_frequency or freq <= rare_frequency}
    
    filtered = []
    for term in doc.terms:
        clean = term.lower().translate(str.maketrans('', '', string.punctuation))
        if clean and clean not in to_filter:
            filtered.append(clean)
    doc._filtered_terms = filtered

def load_documents_from_url(url: str, author: str, origin: str, start_line: int, end_line: int, search_pattern: re.Pattern) -> List[Document]:
    with urllib.request.urlopen(url) as response:
        text = response.read().decode('utf-8')

    lines = text.splitlines()
    if end_line > len(lines):
        end_line = len(lines)
    
    relevant_text = '\n'.join(lines[start_line:end_line])
    
    matches = list(search_pattern.finditer(relevant_text))
    documents = []
    
    SKIP_TITLES = {
        "index", "table of contents", "aesop's fables", 
        "the life of aesop", "life of aesop", "contents", "title page"
    }
    
    for match in matches:
        title = match.group(1).strip()
        content = match.group(2)
        
        normalized_title = title.lower().translate(str.maketrans('', '', string.punctuation)).strip()
        
        if normalized_title in SKIP_TITLES:
            continue
            
        clean_content = ' '.join(content.split())
        terms = [w.lower().translate(str.maketrans('', '', string.punctuation)) 
                 for w in clean_content.split() if w]
                
        doc = Document(
            document_id=len(documents),
            title=title,
            raw_text=clean_content,
            terms=terms,
            author=author,
            origin=origin
        )
        documents.append(doc)
            
    return documents

def linear_boolean_search(term: str, collection: List[Document], stopword_filtered: bool = False, stemmed: bool = False) -> List[Tuple[int, Document]]:
    clean_term = term.lower().translate(str.maketrans('', '', string.punctuation))
    search_term = stem_term(clean_term) if stemmed else clean_term
    results = []

    for doc in collection:
        target_terms = doc._filtered_terms if stopword_filtered and hasattr(doc, '_filtered_terms') else doc.terms
        
        found = False
        for word in target_terms:
            processed_word = word.lower().translate(str.maketrans('', '', string.punctuation))
            if stemmed:
                processed_word = stem_term(processed_word)
            
            if processed_word == search_term:
                found = True
                break
        
        if found:
            results.append((1, doc))
            
    return results

def vector_space_search(query: str, documents: List[Document], stopword_filtered: bool = False, stemmed: bool = False) -> List[Tuple[float, Document]]:
    query_terms = [t.lower().translate(str.maketrans('', '', string.punctuation)) for t in query.strip().split()]
    if stemmed:
        query_terms = [stem_term(t) for t in query_terms]

    all_docs_terms = []
    for doc in documents:
        terms_to_process = doc._filtered_terms if stopword_filtered and hasattr(doc, '_filtered_terms') else doc.terms
        processed_terms = [t.lower().translate(str.maketrans('', '', string.punctuation)) for t in terms_to_process]
        if stemmed:
            processed_terms = [stem_term(t) for t in processed_terms]
        all_docs_terms.append(processed_terms)

    vocab = sorted(list(set(query_terms)))
    N = len(documents)

    df = Counter()
    for terms in all_docs_terms:
        for term in set(terms):
            if term in vocab:
                df[term] += 1

    idf = {term: math.log(N / df[term]) if df[term] > 0 else 0 for term in vocab}

    q_tf = Counter(query_terms)
    q_vec = [q_tf[term] * idf[term] for term in vocab]

    def cosine_similarity(vec1, vec2):
        dot_product = sum(x * y for x, y in zip(vec1, vec2))
        norm_vec1 = math.sqrt(sum(x * x for x in vec1))
        norm_vec2 = math.sqrt(sum(y * y for y in vec2))
        if norm_vec1 == 0 or norm_vec2 == 0:
            return 0.0
        return dot_product / (norm_vec1 * norm_vec2)

    results = []
    for i, terms in enumerate(all_docs_terms):
        doc_tf = Counter(terms)
        doc_vec = [doc_tf[term] * idf[term] for term in vocab]
        similarity = cosine_similarity(q_vec, doc_vec)
        results.append((similarity, documents[i]))
        
    return sorted(results, key=lambda item: item[0], reverse=True)

def precision_recall(retrieved: List[int], relevant: List[int]) -> Tuple[float, float]:
    retrieved_set = set(retrieved)
    relevant_set = set(relevant)
    
    # This special case correctly handles when both are empty.
    if not retrieved_set and not relevant_set:
        return 0.0, 0.0
    
    true_positives = len(retrieved_set.intersection(relevant_set))
    
    # The ternary operator correctly handles the case where the denominator would be zero.
    precision = true_positives / len(retrieved_set) if retrieved_set else 0.0
    recall = true_positives / len(relevant_set) if relevant_set else 0.0
    
    return precision, recall

# PASTE THIS FUNCTION INTO YOUR solution.py FILE

def boolean_conjunction_search(query: str, collection: List[Document], stopword_filtered: bool = False, stemmed: bool = False) -> List[Tuple[int, Document]]:
    """
    Performs a boolean search for documents containing ALL query terms.
    """
    query_terms = query.lower().strip().split()
    results = []
    if not query_terms:
        return results

    if stemmed:
        processed_query_terms = {stem_term(t.translate(str.maketrans('', '', string.punctuation))) for t in query_terms}
    else:
        processed_query_terms = {t.translate(str.maketrans('', '', string.punctuation)) for t in query_terms}

    for doc in collection:
        target_terms = doc._filtered_terms if stopword_filtered and hasattr(doc, '_filtered_terms') and doc._filtered_terms else doc.terms
        
        if stemmed:
            doc_terms_set = {stem_term(t.lower().translate(str.maketrans('', '', string.punctuation))) for t in target_terms}
        else:
            doc_terms_set = {t.lower().translate(str.maketrans('', '', string.punctuation)) for t in target_terms}

        if processed_query_terms.issubset(doc_terms_set):
            results.append((1, doc))
            
    return results