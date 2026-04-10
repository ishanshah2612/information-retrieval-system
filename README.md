# 🔍 Information Retrieval System  
### Boolean & Vector Space Model Implementation

---

## 📌 Overview

This project implements an **Information Retrieval System (IRS)** that enables users to search through a collection of documents using two different retrieval techniques:

- **Boolean Retrieval Model** (exact matching)
- **Vector Space Model** (ranked retrieval)

The system also evaluates search performance using **Precision** and **Recall** metrics.

---

## 🚀 Features

- 🔎 Keyword-based search functionality  
- 📊 Dual retrieval models:
  - Boolean Model (exact match)
  - Vector Space Model (similarity-based ranking)
- 🧹 Text preprocessing:
  - Stop-word removal  
  - Stemming  
- 📈 Performance evaluation:
  - Precision  
  - Recall  
- 🖥️ Simple user interface for interaction  

---

## 🏗️ System Architecture

The system follows an object-oriented design with the following components:

information-retrieval-system/
│
├── src/ # Source code
├── data/ # Input documents (if any)
├── docs/ # Documentation
│ └── Practical_Task_1.pdf
│
├── README.md

### 📄 Document
Represents a single document and handles preprocessing.

- Attributes: `content`, `title`, `fileName`  
- Methods:
  - `removeStopWords()`
  - `applyStemming()`
  - `getProcessedText()`

---

### 📚 DocumentCollection
Manages a collection of documents.

- Methods:
  - `createFromTextFile(filePath)`
  - `storeToDisk()`
  - `loadFromDisk()`

---

### 🧠 RetrievalModel (Abstract Class)
Defines a common interface for all retrieval models.

- Method:
  - `search()`

---

### 🔍 BooleanModel
Implements Boolean retrieval using an inverted index.

- Returns documents that exactly match query terms  

---

### 📊 VectorSpaceModel
Implements ranked retrieval using vector representation.

- Calculates similarity between query and documents  
- Returns ranked results  

---

### 🔄 Search
Acts as the controller for executing search queries.

- Switches between retrieval models  
- Processes user queries  

---

### 📈 PrecisionRecallCalculator
Evaluates system performance.

- `calculatePrecision()`  
- `calculateRecall()`  

---

### 🖥️ UserInterface
Handles user interaction and displays results.

---

## ⚙️ How It Works

1. Documents are loaded into the system  
2. Text preprocessing is applied:
   - Stop-word removal  
   - Stemming  
3. User inputs a query  
4. A retrieval model is selected:
   - Boolean → exact match  
   - Vector → ranked results  
5. Results are displayed  
6. Precision and Recall are calculated  

---

## 🧪 Example

**Query:**

---

## 💡 Future Improvements

- Add TF-IDF weighting  
- Improve ranking algorithms  
- Build a web-based interface  
- Handle large-scale datasets  

---

## 👨‍💻 Author

**Ishan Shah**

---

## ⭐ Notes

This project was developed as part of an academic assignment to demonstrate core concepts of **Information Retrieval Systems**, including search models and evaluation techniques.