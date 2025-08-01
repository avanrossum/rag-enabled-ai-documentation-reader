import os
from typing import List, Dict, Any
import numpy as np
from openai import OpenAI

# Get the embedding model from environment variables
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of texts using OpenAI's API.
    
    Args:
        texts: A list of text strings to generate embeddings for
        
    Returns:
        A list of embedding vectors
    """
    if not texts:
        return []
    
    # Initialize OpenAI client inside the function with minimal parameters
    api_key = os.getenv("OPENAI_API_KEY", "")
    client = OpenAI()
    client.api_key = api_key
    
    # Call OpenAI API to get embeddings
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
        dimensions=1536  # Default for text-embedding-3-small
    )
    
    # Extract embeddings from response
    embeddings = [item.embedding for item in response.data]
    
    return embeddings

def get_embedding(text: str) -> List[float]:
    """
    Generate an embedding for a single text using OpenAI's API.
    
    Args:
        text: The text to generate an embedding for
        
    Returns:
        An embedding vector
    """
    embeddings = get_embeddings([text])
    return embeddings[0] if embeddings else []

def cosine_similarity(a: List[float], b: List[float]) -> float:
    """
    Calculate the cosine similarity between two vectors.
    
    Args:
        a: First vector
        b: Second vector
        
    Returns:
        The cosine similarity between the vectors
    """
    a_np = np.array(a)
    b_np = np.array(b)
    
    return np.dot(a_np, b_np) / (np.linalg.norm(a_np) * np.linalg.norm(b_np))