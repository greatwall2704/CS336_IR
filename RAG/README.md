# RAG PDF Question Answering System

This project implements a Retrieval-Augmented Generation (RAG) system for querying PDF documents using vector similarity search.

## Features
- PDF text extraction and processing
- Vector embedding using HuggingFace models
- FAISS vector store for efficient similarity search
- Question answering based on retrieved context

## Setup
```bash
# Clone repository
git clone <your-repo-url>
cd RAG

# Install dependencies
pip install -r requirements.txt

# Place your PDF file in the directory
# Run the indexing notebook
jupyter notebook build_index.ipynb

# Run the query notebook
jupyter notebook query_index.ipynb
```

## Usage
1. Add your PDF file to the directory
2. Run build_index.ipynb to create the vector index
3. Use query_index.ipynb to ask questions about the PDF content

## Requirements
See requirements.txt for full list of dependencies.
