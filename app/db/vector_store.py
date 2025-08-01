import os
import json
import faiss
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import pickle

class FAISSVectorStore:
    """
    A vector store implementation using FAISS for efficient similarity search.
    """
    
    def __init__(self, dimension: int = 1536, index_type: str = "L2"):
        """
        Initialize the FAISS vector store.
        
        Args:
            dimension: The dimension of the embedding vectors
            index_type: The type of FAISS index to use (L2 or IP for inner product)
        """
        self.dimension = dimension
        self.index_type = index_type
        
        # Initialize FAISS index
        if index_type == "L2":
            self.index = faiss.IndexFlatL2(dimension)
        elif index_type == "IP":
            self.index = faiss.IndexFlatIP(dimension)
        else:
            raise ValueError(f"Unsupported index type: {index_type}")
        
        # Initialize document store
        self.documents = []
        
        # Path to save the vector store
        self.vector_db_path = os.getenv("VECTOR_DB_PATH", "./vector_db")
        
        # Create the directory if it doesn't exist
        os.makedirs(self.vector_db_path, exist_ok=True)
    
    def add_documents(self, documents: List[Dict[str, Any]], embeddings: List[List[float]]):
        """
        Add documents and their embeddings to the vector store.
        
        Args:
            documents: A list of document dictionaries
            embeddings: A list of embedding vectors corresponding to the documents
        """
        if not documents or not embeddings:
            return
        
        if len(documents) != len(embeddings):
            raise ValueError("Number of documents and embeddings must match")
        
        # Convert embeddings to numpy array
        embeddings_np = np.array(embeddings).astype('float32')
        
        # Add embeddings to FAISS index
        self.index.add(embeddings_np)
        
        # Add documents to document store
        start_idx = len(self.documents)
        for i, doc in enumerate(documents):
            doc["id"] = start_idx + i
            self.documents.append(doc)
    
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for the most similar documents to a query embedding.
        
        Args:
            query_embedding: The embedding vector of the query
            top_k: The number of results to return
            
        Returns:
            A list of the most similar documents
        """
        if not self.documents:
            return []
        
        # Convert query embedding to numpy array
        query_embedding_np = np.array([query_embedding]).astype('float32')
        
        # Search FAISS index
        distances, indices = self.index.search(query_embedding_np, min(top_k, len(self.documents)))
        
        # Get the corresponding documents
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                doc = self.documents[idx].copy()
                doc["score"] = float(distances[0][i])
                results.append(doc)
        
        return results
    
    def save(self, filename: Optional[str] = None):
        """
        Save the vector store to disk.
        
        Args:
            filename: The filename to save to (without extension)
        """
        if filename is None:
            filename = "vector_store"
        
        # Create full paths
        index_path = os.path.join(self.vector_db_path, f"{filename}.index")
        docs_path = os.path.join(self.vector_db_path, f"{filename}.pkl")
        
        # Save FAISS index
        faiss.write_index(self.index, index_path)
        
        # Save documents
        with open(docs_path, "wb") as f:
            pickle.dump(self.documents, f)
    
    def load(self, filename: Optional[str] = None) -> bool:
        """
        Load the vector store from disk.
        
        Args:
            filename: The filename to load from (without extension)
            
        Returns:
            True if the vector store was loaded successfully, False otherwise
        """
        if filename is None:
            filename = "vector_store"
        
        # Create full paths
        index_path = os.path.join(self.vector_db_path, f"{filename}.index")
        docs_path = os.path.join(self.vector_db_path, f"{filename}.pkl")
        
        # Check if files exist
        if not os.path.exists(index_path) or not os.path.exists(docs_path):
            return False
        
        try:
            # Load FAISS index
            self.index = faiss.read_index(index_path)
            
            # Load documents
            with open(docs_path, "rb") as f:
                self.documents = pickle.load(f)
            
            return True
        except Exception as e:
            print(f"Error loading vector store: {e}")
            return False