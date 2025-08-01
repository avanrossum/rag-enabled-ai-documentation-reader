import os
from typing import List, Dict, Any
from openai import OpenAI

from app.core.embeddings import get_embedding
from app.db.vector_store import FAISSVectorStore

# Get the completion model from environment variables
COMPLETION_MODEL = os.getenv("COMPLETION_MODEL", "gpt-4o")

# Initialize vector store
vector_store = FAISSVectorStore()

# Load vector store if it exists
vector_store.load()

def query_documentation(query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Query the documentation with a natural language question.
    
    Args:
        query: The natural language question
        top_k: The number of most relevant chunks to retrieve
        
    Returns:
        A dictionary containing the answer and the sources
    """
    try:
        # Generate embedding for the query
        query_embedding = get_embedding(query)
        
        # Search for relevant chunks
        relevant_chunks = vector_store.search(query_embedding, top_k=top_k)
        
        if not relevant_chunks:
            return {
                "answer": "I couldn't find any relevant information in the documentation. Please try rephrasing your question.",
                "sources": []
            }
    except Exception as e:
        return {
            "answer": f"The vector database is not yet initialized or there was an error: {str(e)}. Please run the vectorization process first.",
            "sources": []
        }
    
    # Prepare context for the completion
    context = "\n\n".join([
        f"Source {i+1}: {chunk['content']}"
        for i, chunk in enumerate(relevant_chunks)
    ])
    
    # Prepare sources for the response
    sources = []
    for chunk in relevant_chunks:
        source = {
            "content": chunk["content"][:200] + "..." if len(chunk["content"]) > 200 else chunk["content"],
            "metadata": chunk["metadata"],
            "score": chunk["score"]
        }
        sources.append(source)
    
    # Generate completion
    prompt = f"""
You are an API documentation assistant. Answer the following question based on the provided documentation chunks.
If the answer is not contained in the documentation, say "I don't know" or "I couldn't find information about that in the documentation."
Do not make up or infer information that is not explicitly stated in the documentation.

Documentation chunks:
{context}

Question: {query}

Answer:
"""
    
    # Initialize OpenAI client inside the function with minimal parameters
    api_key = os.getenv("OPENAI_API_KEY", "")
    client = OpenAI()
    client.api_key = api_key
    
    response = client.chat.completions.create(
        model=COMPLETION_MODEL,
        messages=[
            {"role": "system", "content": "You are an API documentation assistant that provides accurate, helpful answers based solely on the provided documentation."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_tokens=1000
    )
    
    answer = response.choices[0].message.content.strip()
    
    return {
        "answer": answer,
        "sources": sources
    }