import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.tools import tool

load_dotenv()

CHROMA_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")

_vectorstore = None

def get_vectorstore():
    """Lazy-load the vector store (only once)."""
    global _vectorstore
    if _vectorstore is None:
        embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        _vectorstore = Chroma(
            persist_directory=CHROMA_PATH,
            embedding_function=embeddings,
            collection_name="company_knowledge"
        )
    return _vectorstore

@tool
def knowledge_base_search(query: str) -> str:
    """
    Search the company's internal knowledge base for policies, FAQs, troubleshooting steps, and product information.
    Use this tool when a customer asks about company policies, how to do something, what the rules are, or troubleshooting steps.
    Input: a natural language question or search query.
    Output: Relevant information from the company's documents.
    """
    try:
        vectorstore = get_vectorstore()
        results = vectorstore.similarity_search(query, k=3)
        
        if not results:
            return "No relevant information found in the knowledge base for this query."
        
        combined = "\n\n---\n\n".join([doc.page_content for doc in results])
        return f"Relevant policy/FAQ information:\n\n{combined}"
    
    except Exception as e:
        return f"Knowledge base search failed: {str(e)}. Please answer from general knowledge."
