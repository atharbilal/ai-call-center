"""
Knowledge base ingestion script.
Run this ONCE before starting the server to populate the vector database.
Usage: python -m knowledge.ingest
"""

import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings

load_dotenv()

DOCS_FOLDER = Path("./sample_docs")
CHROMA_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")

def load_documents():
    """Load all .txt and .pdf files from sample_docs folder."""
    documents = []
    
    for file_path in DOCS_FOLDER.glob("**/*"):
        if file_path.suffix == ".txt":
            print(f"Loading text file: {file_path}")
            loader = TextLoader(str(file_path), encoding="utf-8")
            documents.extend(loader.load())
        elif file_path.suffix == ".pdf":
            print(f"Loading PDF: {file_path}")
            loader = PyPDFLoader(str(file_path))
            documents.extend(loader.load())
    
    print(f"Loaded {len(documents)} document(s).")
    return documents

def split_documents(documents):
    """Split documents into chunks for embedding."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", "!", "?", ",", " "]
    )
    chunks = splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks.")
    return chunks

def create_vector_store(chunks):
    """Create ChromaDB vector store from document chunks."""
    print("Creating embeddings — this may take 1-2 minutes on first run...")
    
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH,
        collection_name="company_knowledge"
    )
    
    vectorstore.persist()
    print(f"Vector store saved to {CHROMA_PATH}")
    print(f"Total documents in store: {vectorstore._collection.count()}")
    return vectorstore

def main():
    print("=== Knowledge Base Ingestion ===")
    docs = load_documents()
    if not docs:
        print("No documents found in sample_docs/. Add .txt or .pdf files and re-run.")
        return
    chunks = split_documents(docs)
    create_vector_store(chunks)
    print("=== Ingestion Complete ===")

if __name__ == "__main__":
    main()
